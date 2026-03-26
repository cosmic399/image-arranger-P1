---
name: image-arranger-workflow
description: Workflow rules and conventions for developing the image-arranger-P1 SvelteKit canvas app. Use this when working on any features, bug fixes, or exports in the project at c:\Users\gcsr2\AIMG.
---

# Image Arranger – Developer Workflow

## Project Context
- **Framework**: SvelteKit 5 with Svelte 5 runes (`$state`, `$derived`, `$effect`)
- **Styling**: Tailwind CSS v4 (no arbitrary Tailwind classes — use inline styles for dynamic pixel values)
- **Runtime**: Bun (`bun run dev`, `bun install`)
- **Canvas**: Fixed A4 size — **794px × 1123px** (96 DPI equivalent). All coordinates are in these pixel units.
- **Dev URL**: http://localhost:5173

## File Roles
| File | Role |
|------|------|
| `src/routes/+page.svelte` | Main orchestrator — holds page/image state, handles all top-level events |
| `src/lib/components/ImageItem.svelte` | Per-image draggable element — handles drag, resize, rotate, text overlays |
| `src/lib/components/ImageFilters.svelte` | Sidebar filter panel for selected image |
| `src/lib/components/Canvas.svelte` | Renders the A4 canvas area and all ImageItem instances |
| `src/lib/components/CropModal.svelte` | Full-screen crop dialog with pan/zoom |
| `src/lib/utils/exportUtils.js` | PNG / JPEG / PDF rendering via off-screen Canvas API |
| `src/lib/utils/imageUtils.js` | CSS filter string builder and crop helper |

## Core Invariants — Never Break These
1. **A4 dimensions are constant** — `A4_WIDTH = 794`, `A4_HEIGHT = 1123`. Never hardcode different values.
2. **Export renders a fresh off-screen `<canvas>` at 2× scale** — never screenshot the DOM.
3. **What you see = what you export** — the clamped visual position (`clampedX`, `clampedY`) must be written back to the image store before export. The export reads raw `image.x` / `image.y`.
4. **Image state is immutable-style** — always spread (`{ ...image, x: newX }`) when updating via `onUpdate()`.
5. **Blob URLs must be revoked** — when deleting images or pages, call `URL.revokeObjectURL(image.url)`.

## Coordinate System
- **Origin** = top-left of canvas (0, 0)
- Images store `x`, `y` (top-left anchor), `width`, `height` (natural), `scaleX`, `scaleY`
- Displayed size = `width * scaleX` × `height * scaleY`
- `zIndex` determines layer order — selecting an image bumps it to `maxZ + 1`

## Adding a New Feature — Checklist
- [ ] Does the feature affect image state? → update via `onUpdate()` in `ImageItem.svelte`
- [ ] Does the feature render in the export? → update `renderSceneToCanvas()` in `exportUtils.js`
- [ ] Does it need a new sidebar control? → add to `ImageFilters.svelte` or extend the selection side panel in `ImageItem.svelte`
- [ ] Does it affect text overlays? → check `hasText`, `hasOuterTop`, `hasOuterBottom` flags and their render logic in both `ImageItem.svelte` and `exportUtils.js`

## Export Rules
- **PNG** — single-page only; button is disabled for multi-page documents
- **PDF** — all pages; each page rendered as JPEG (quality 0.7) inside jsPDF
- **JPEG** — implemented in `exportUtils.js` but not yet wired to a UI button
- Always `await renderSceneToCanvas(pageImages, 2)` — never use scale factor < 2

## Running the Project
```bash
bun install       # Install deps
bun run dev       # Start dev server at http://localhost:5173
```

## Common Mistakes to Avoid
- ❌ Do NOT use `html2canvas` — the project uses a manual Canvas API renderer
- ❌ Do NOT use `img.style.filter` for export — use `ctx.filter = applyFilters(imgData)` via `imageUtils.js`
- ❌ Do NOT use Tailwind for dynamic pixel values (`left-[${x}px]`) — use `style="left: {x}px"`
- ❌ Do NOT forget to handle the `pointerdown` event with `stopPropagation()` when adding new clickable controls inside `ImageItem.svelte`
