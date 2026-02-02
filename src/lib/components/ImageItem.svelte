<script>
	import { X, RotateCw, Crop, Trash2 } from 'lucide-svelte';
	import { applyFilters } from '../utils/imageUtils.js';

	let {
		image,
		onUpdate = () => {},
		onDelete = () => {},
		onSelect = () => {},
		onCropRequest = () => {},
		isSelected = false
	} = $props();

	let isDragging = $state(false);
	let isResizing = $state(false);
	let resizeHandle = $state(null);
	let dragStart = $state({ x: 0, y: 0 });
	let resizeStart = $state({ x: 0, y: 0, width: 0, height: 0, aspectRatio: 1 });

	// Virtual Proxy State (Unbounded)
	// We init with image.x/y which might be bounded, but track moves virtually
	let virtualX = $state(image.x);
	let virtualY = $state(image.y);

	// Sync local virual state with updates if external change happens (rare in single user)
	// But crucial if we just loaded or props changed
	$effect(() => {
		if (!isDragging) {
			virtualX = image.x;
			virtualY = image.y;
		}
	});

	// Context-Aware UI
	const isControlsContrastNeeded = $derived(image.y < 50);

	let animationFrameId = null;
	let currentMousePos = { x: 0, y: 0 };
	let startMousePos = { x: 0, y: 0 };
	let currentShiftKey = $state(false);
	let isDirty = false;
	let isRotating = $state(false);
	let hasMoved = false;

	function getCanvasScale(element) {
		const canvas = element.closest('.canvas-area');
		if (!canvas) return 1;
		const style = window.getComputedStyle(canvas);
		const matrix = new WebKitCSSMatrix(style.transform);
		return matrix.a || 1;
	}

	function getCanvasRect(element) {
		const canvas = element.closest('.canvas-area');
		return canvas ? canvas.getBoundingClientRect() : { left: 0, top: 0 };
	}

	function handlePointerDown(e) {
		// CRITICAL: Capture on the wrapper to track mouse even off-screen
		e.currentTarget.setPointerCapture(e.pointerId);

		const canvas = e.target.closest('.canvas-area');
		const scale = getCanvasScale(e.target);
		const rect = getCanvasRect(e.target);

		startMousePos = { x: e.clientX, y: e.clientY };
		hasMoved = false;

		const mouseX = (e.clientX - rect.left) / scale;
		const mouseY = (e.clientY - rect.top) / scale;

		if (e.target.closest('.rotation-handle')) {
			isRotating = true;
			resizeStart = {
				centerX: image.x + (image.width * (image.scaleX || image.scale)) / 2,
				centerY: image.y + (image.height * (image.scaleY || image.scale)) / 2
			};
		} else if (e.target.closest('.resize-handle')) {
			isResizing = true;
			const handle = e.target.closest('.resize-handle');
			resizeHandle = handle.dataset.handle;

			const currentScaleX = image.scaleX || image.scale || 1;
			const currentScaleY = image.scaleY || image.scale || 1;
			const currentWidth = image.width * currentScaleX;
			const currentHeight = image.height * currentScaleY;

			resizeStart = {
				mouseX: mouseX,
				mouseY: mouseY,
				width: currentWidth,
				height: currentHeight,
				aspectRatio: currentWidth / currentHeight,
				imageX: image.x,
				imageY: image.y,
				scale: scale,
				baseScaleX: currentScaleX,
				baseScaleY: currentScaleY
			};
		} else {
			isDragging = false;
			// Start Virtual Tracking
			virtualX = image.x;
			virtualY = image.y;

			dragStart = {
				x: mouseX - image.x,
				y: mouseY - image.y
			};
		}

		// e.preventDefault(); // Sometimes prevents capture? User said "setPointerCapture".
		// Note: preventDefault is needed to stop text selection / native drag
		e.preventDefault();
		e.stopPropagation();

		window.addEventListener('pointermove', handlePointerMove);
		window.addEventListener('pointerup', handlePointerUp);
	}

	function handlePointerMove(e) {
		currentMousePos = { x: e.clientX, y: e.clientY };
		currentShiftKey = e.shiftKey;

		if (!hasMoved && !isResizing && !isRotating) {
			const dist = Math.hypot(e.clientX - startMousePos.x, e.clientY - startMousePos.y);
			if (dist > 3) {
				hasMoved = true;
				isDragging = true;
				onSelect();
				if (!animationFrameId) updatePosition();
			}
		} else if (hasMoved || isResizing || isRotating) {
			isDirty = true;
			if (!animationFrameId) updatePosition();
		}
	}

	function handlePointerUp(e) {
		if (!hasMoved && !isResizing && !isRotating) {
			onSelect();
		}

		isDragging = false;
		isResizing = false;
		isRotating = false;
		resizeHandle = null;

		window.removeEventListener('pointermove', handlePointerMove);
		window.removeEventListener('pointerup', handlePointerUp);
	}

	function updatePosition() {
		if (!isDragging && !isResizing && !isRotating && !isDirty) return;

		const canvas = document.querySelector('.canvas-area');
		const scale = getCanvasScale(canvas);
		const rect = getCanvasRect(canvas);

		const mouseX = (currentMousePos.x - rect.left) / scale;
		const mouseY = (currentMousePos.y - rect.top) / scale;

		if (isDragging) {
			// Unbounded Virtual Move
			let targetX = mouseX - dragStart.x;
			let targetY = mouseY - dragStart.y;

			// Virtual Update
			virtualX = targetX;
			virtualY = targetY;

			// Sync to Store (Unbounded)
			onUpdate({
				...image,
				x: virtualX,
				y: virtualY
			});

			isDirty = true;
		} else if (isResizing) {
			// Calculate delta in canvas space
			const deltaX = mouseX - resizeStart.mouseX;
			const deltaY = mouseY - resizeStart.mouseY;

			let newWidth = resizeStart.width;
			let newHeight = resizeStart.height;
			let newX = resizeStart.imageX;
			let newY = resizeStart.imageY;

			// Handle different resize handles
			if (resizeHandle.includes('e')) newWidth += deltaX;
			if (resizeHandle.includes('w')) {
				newWidth -= deltaX;
				newX += deltaX;
			}
			if (resizeHandle.includes('s')) newHeight += deltaY;
			if (resizeHandle.includes('n')) {
				newHeight -= deltaY;
				newY += deltaY;
			}

			// Enforce min size
			if (newWidth < 20) newWidth = 20;
			if (newHeight < 20) newHeight = 20;

			// Aspect Ratio Logic
			if (!currentShiftKey) {
				if (resizeHandle.length === 2) {
					newHeight = newWidth / resizeStart.aspectRatio;
					if (resizeHandle.includes('n'))
						newY = resizeStart.imageY + (resizeStart.height - newHeight);
					if (resizeHandle.includes('w'))
						newX = resizeStart.imageX + (resizeStart.width - newWidth);
				} else if (resizeHandle === 'n' || resizeHandle === 's') {
					newWidth = newHeight * resizeStart.aspectRatio;
					newX = resizeStart.imageX + (resizeStart.width - newWidth) / 2;
				} else if (resizeHandle === 'e' || resizeHandle === 'w') {
					newHeight = newWidth / resizeStart.aspectRatio;
					newY = resizeStart.imageY + (resizeStart.height - newHeight) / 2;
				}
			}

			const newScaleX = newWidth / image.width;
			const newScaleY = newHeight / image.height;

			onUpdate({
				...image,
				x: newX,
				y: newY,
				scaleX: Math.max(0.01, newScaleX),
				scaleY: Math.max(0.01, newScaleY),
				scale: Math.max(0.01, newScaleX)
			});
		} else if (isRotating) {
			const dx = mouseX - resizeStart.centerX;
			const dy = mouseY - resizeStart.centerY;
			const angleRad = Math.atan2(dy, dx);
			const angleDeg = angleRad * (180 / Math.PI);

			onUpdate({
				...image,
				rotation: angleDeg + 90
			});
		}

		if (isDragging || isResizing || isRotating || isDirty) {
			animationFrameId = requestAnimationFrame(updatePosition);
		} else {
			animationFrameId = null;
		}
	}

	function handleRotate(e) {
		e.stopPropagation();
		onUpdate({
			...image,
			rotation: (image.rotation + 90) % 360
		});
	}

	function handleDelete(e) {
		e.stopPropagation();
		onDelete(image.id);
	}

	function handleCrop(e) {
		e.stopPropagation();
		onCropRequest(image);
	}

	const filterStyle = $derived(applyFilters(image));

	const sX = $derived(image.scaleX || image.scale || 1);
	const sY = $derived(image.scaleY || image.scale || 1);

	// Display Logic: Clamp the Virtual Coordinate
	// This creates the "Sticky/Elastic" visual at the edge while physics is free
	const dW = $derived(image.width * sX);
	const dH = $derived(image.height * sY);
	const maxX = $derived(794 - dW); // A4 Width approx
	const maxY = $derived(1123 - dH); // A4 Height approx

	const clampedX = $derived(Math.max(0, Math.min(maxX, image.x)));
	const clampedY = $derived(Math.max(0, Math.min(maxY, image.y)));

	// Wrapper Transform (Position Only)
	const transformStringWrapper = $derived(`translate3d(${clampedX}px, ${clampedY}px, 0)`);

	// Content Transform (Rotation)
	const transformStringContent = $derived(`rotate(${image.rotation}deg)`);
</script>

<!-- Outer Wrapper: Positioning & Selection (Non-Rotating Blue Box) -->
<div
	class="image-wrapper absolute cursor-move select-none {isSelected
		? 'outline outline-2 outline-offset-2 outline-cyan-400'
		: ''} {isDragging ? 'z-[9999] scale-[1.02] shadow-2xl' : ''}"
	style="
		top: 0;
		left: 0;
        z-index: {image.zIndex};
        transform: {transformStringWrapper};
		width: {image.width * sX}px;
		height: {image.height * sY}px;
        backface-visibility: hidden;
        perspective: 1000px;
        will-change: transform;
        transition: box-shadow 0.2s ease;
		touch-action: none;
    "
	onpointerdown={handlePointerDown}
	role="button"
	tabindex="0"
>
	<!-- Controls (Top-Left, Upright) -->
	{#if isSelected}
		<div
			class="absolute -top-12 left-0 z-50 flex gap-2 rounded-lg border border-gray-200 bg-white/95 p-1.5 shadow-md backdrop-blur"
			onpointerdown={(e) => e.stopPropagation()}
			onmousedown={(e) => e.stopPropagation()}
			onclick={(e) => e.stopPropagation()}
		>
			<button
				class="rounded p-1.5 text-cyan-700 transition-colors hover:bg-cyan-50"
				onclick={handleRotate}
				title="Rotate 90°"
			>
				<RotateCw size={16} />
			</button>
			<button
				class="rounded p-1.5 text-cyan-700 transition-colors hover:bg-cyan-50"
				onclick={handleCrop}
				title="Crop"
			>
				<Crop size={16} />
			</button>
			<div class="my-auto h-5 w-px bg-gray-200"></div>
			<button
				class="rounded p-1.5 text-red-600 transition-colors hover:bg-red-50"
				onclick={handleDelete}
				title="Delete"
			>
				<Trash2 size={16} />
			</button>
		</div>

		<!-- Resize Handles (Axis-Aligned resizing) -->
		{#each ['nw', 'ne', 'sw', 'se'] as handle}
			<div
				class="resize-handle absolute z-40 h-3 w-3 rounded-full border border-cyan-500 bg-white shadow-sm"
				style="
                    {handle.includes('n') ? 'top: -6px;' : 'bottom: -6px;'}
                    {handle.includes('w') ? 'left: -6px;' : 'right: -6px;'}
                    cursor: {handle}-resize;
                "
				data-handle={handle}
			></div>
		{/each}
	{/if}

	<!-- Inner Content: Rotation -->
	<div
		class="image-content h-full w-full"
		style="transform: {transformStringContent}; transform-origin: center center;"
	>
		<img
			src={image.url}
			alt=""
			class="pointer-events-none block h-full w-full select-none"
			style="object-fit: contain; filter: {filterStyle};"
			draggable="false"
		/>
	</div>

	<!-- Rotation Handle (Visual, attached to Wrapper top for now) -->
	{#if isSelected}
		<div
			class="rotation-handle group absolute -top-8 left-1/2 z-40 flex h-6 w-6 -translate-x-1/2 cursor-alias items-center justify-center"
			title="Free Rotate"
		>
			<div class="absolute top-4 left-1/2 h-4 w-0.5 -translate-x-1/2 bg-cyan-400"></div>
			<div
				class="h-3 w-3 rounded-full border-2 border-cyan-400 bg-white shadow-sm transition-transform group-hover:scale-125"
			></div>
		</div>
	{/if}
</div>
