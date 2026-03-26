"""
Auto-Arrange Solver — Vercel Serverless Python Endpoint
POST /api/arrange

Receives a list of images with pixel dimensions and a canvas size,
returns non-overlapping x/y positions that fit inside the canvas.

Solver  : Google OR-Tools CP-SAT (Constraint Programming)
Framework: FastAPI + Pydantic for typed request/response validation
Time limit: 8 s hard cap — returns best layout found before the buzzer.
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from ortools.sat.python import cp_model

app = FastAPI()


# ---------------------------------------------------------------------------
# Request / Response models
# ---------------------------------------------------------------------------

class ImageDimensions(BaseModel):
    id: str
    width: int
    height: int


class Canvas(BaseModel):
    width: int
    height: int


class ArrangeRequest(BaseModel):
    canvas: Canvas
    images: List[ImageDimensions]
    allow_rotation: bool = True


# ---------------------------------------------------------------------------
# Solver endpoint
# ---------------------------------------------------------------------------

@app.post("/api/arrange")
def arrange_images(request: ArrangeRequest):
    """
    Run the CP-SAT 2-D bin packing solver.

    Each image is placed at an integer (x, y) top-left coordinate.
    The solver guarantees:
      - Every image stays fully within the canvas boundary.
      - No two images overlap (AddNoOverlap2D constraint).
      - Positions are compacted toward the top-left (minimise Σ x + Σ y).

    Returns the solved layout or raises HTTP 400 if no feasible solution
    exists within the 8-second time limit.
    """
    model = cp_model.CpModel()

    W = request.canvas.width
    H = request.canvas.height
    GAP = 20  # Space between images

    image_vars = {}

    for img in request.images:
        w = min(img.width, W)
        h = min(img.height, H)

        is_rotated = model.NewBoolVar(f"rot_{img.id}")
        
        if not request.allow_rotation:
            model.Add(is_rotated == 0)

        # Actual dimensions including the gap
        actual_w = model.NewIntVar(1, max(W, H) + GAP, f"aw_{img.id}")
        actual_h = model.NewIntVar(1, max(W, H) + GAP, f"ah_{img.id}")

        # If NOT rotated: actual width is w + GAP, height is h + GAP
        model.Add(actual_w == w + GAP).OnlyEnforceIf(is_rotated.Not())
        model.Add(actual_h == h + GAP).OnlyEnforceIf(is_rotated.Not())
        
        # If ROTATED: actual width is h + GAP, height is w + GAP
        model.Add(actual_w == h + GAP).OnlyEnforceIf(is_rotated)
        model.Add(actual_h == w + GAP).OnlyEnforceIf(is_rotated)

        # X/Y bounded by canvas size minus the actual image (excluding gap for the right/bottom edge)
        x = model.NewIntVar(0, W, f"x_{img.id}")
        y = model.NewIntVar(0, H, f"y_{img.id}")
        
        # Ensure the image itself strictly fits in the canvas (x + w <= W)
        # We do this conditionally based on rotation
        model.Add(x + w <= W).OnlyEnforceIf(is_rotated.Not())
        model.Add(y + h <= H).OnlyEnforceIf(is_rotated.Not())
        
        model.Add(x + h <= W).OnlyEnforceIf(is_rotated)
        model.Add(y + w <= H).OnlyEnforceIf(is_rotated)

        # Interval vars for NoOverlap2D
        x_end = model.NewIntVar(0, W + GAP, f"xe_{img.id}")
        y_end = model.NewIntVar(0, H + GAP, f"ye_{img.id}")
        
        model.Add(x_end == x + actual_w)
        model.Add(y_end == y + actual_h)

        x_interval = model.NewIntervalVar(x, actual_w, x_end, f"xi_{img.id}")
        y_interval = model.NewIntervalVar(y, actual_h, y_end, f"yi_{img.id}")

        image_vars[img.id] = {
            "x": x,
            "y": y,
            "x_int": x_interval,
            "y_int": y_interval,
            "is_rotated": is_rotated
        }

    # Non-overlap constraint
    model.AddNoOverlap2D(
        [v["x_int"] for v in image_vars.values()],
        [v["y_int"] for v in image_vars.values()],
    )

    # Objective: pack everything toward the top-left corner
    all_pos_vars = []
    for v in image_vars.values():
        all_pos_vars.extend([v["x"], v["y"]])
    model.Minimize(sum(all_pos_vars))

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 8.0
    solver.parameters.num_search_workers = 4

    status = solver.Solve(model)

    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        layout = []
        for img_id, v in image_vars.items():
            did_rotate = solver.Value(v["is_rotated"]) == 1
            layout.append({
                "id": img_id, 
                "x": solver.Value(v["x"]), 
                "y": solver.Value(v["y"]),
                "rotation": 90 if did_rotate else 0
            })
        return {"status": "SUCCESS", "layout": layout}

    raise HTTPException(
        status_code=400,
        detail="The images are a bit too large to pack onto one page! Try scaling them down slightly using the corner handles.",
    )
