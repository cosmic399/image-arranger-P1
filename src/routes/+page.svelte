<script>
	import { onMount } from 'svelte';
	import {
		Download,
		FileImage,
		FileText,
		Trash2,
		Upload,
		ZoomIn,
		ZoomOut,
		RotateCcw,
		Sparkles,
		X
	} from 'lucide-svelte';
	import ImageUpload from '$lib/components/ImageUpload.svelte';
	import ImageItem from '$lib/components/ImageItem.svelte';
	import ImageFilters from '$lib/components/ImageFilters.svelte';
	import CropModal from '$lib/components/CropModal.svelte';
	import { exportAsPNG, exportAsJPEG, exportAsPDF } from '$lib/utils/exportUtils.js';

	// A4 dimensions at 96 DPI: 210mm x 297mm = 794px x 1123px
	const A4_WIDTH = 794;
	const A4_HEIGHT = 1123;

	let images = $state([]);
	let selectedImageId = $state(null);
	let canvasRef = $state(null);
	let canvasScale = $state(1);
	let isExporting = $state(false);
	let cropModalOpen = $state(false);
	let cropImageData = $state(null);

	function handleImagesAdded(newImages) {
		// Find highest z-index
		const maxZ = images.reduce((max, img) => Math.max(max, img.zIndex), 0);
		let currentZ = maxZ + 1;

		newImages.forEach((img, index) => {
			// Ensure Width/Height are real
			if (!img.width) img.width = 100;
			if (!img.height) img.height = 100;

			// Smart Import Scaling
			const targetWidth = A4_WIDTH * 0.8;
			const targetHeight = A4_HEIGHT * 0.8;

			if (img.width > targetWidth || img.height > targetHeight) {
				const scaleW = targetWidth / img.width;
				const scaleH = targetHeight / img.height;
				const fitScale = Math.min(scaleW, scaleH);
				img.scale = fitScale;
				img.scaleX = fitScale;
				img.scaleY = fitScale;
			} else {
				img.scale = 1;
				img.scaleX = 1;
				img.scaleY = 1;
			}

			// Center on Canvas
			// Note: img.width is intrinsic. Display width is width * scale.
			const displayW = img.width * (img.scaleX || 1);
			const displayH = img.height * (img.scaleY || 1);

			img.x = (A4_WIDTH - displayW) / 2 + index * 20; // Add offset for multiple shuffle
			img.y = (A4_HEIGHT - displayH) / 2 + index * 20;
			img.zIndex = currentZ++;
		});
		images = [...images, ...newImages];
	}

	function handleImageUpdate(updatedImage) {
		images = images.map((img) => (img.id === updatedImage.id ? updatedImage : img));
	}

	function handleImageDelete(id) {
		images = images.filter((img) => img.id !== id);
		if (selectedImageId === id) {
			selectedImageId = null;
		}
	}

	function handleImageSelect(id) {
		selectedImageId = id;
		const maxZ = Math.max(...images.map((img) => img.zIndex), 0);
		images = images.map((img) => (img.id === id ? { ...img, zIndex: maxZ + 1 } : img));
	}

	function clearAll() {
		if (confirm('Clear all images?')) {
			images = [];
			selectedImageId = null;
		}
	}

	// Zoom functions kept for potential keyboard shortcuts, but slider is primary control
	function zoomIn() {
		canvasScale = Math.min(2, canvasScale + 0.1);
	}

	function zoomOut() {
		canvasScale = Math.max(0.25, canvasScale - 0.1);
	}

	function resetZoom() {
		canvasScale = 1;
	}

	async function exportImage(format) {
		if (!canvasRef || images.length === 0) {
			alert('Please add some images first!');
			return;
		}

		isExporting = true;
		try {
			let result;
			const timestamp = new Date().toISOString().slice(0, 19).replace(/:/g, '-');

			switch (format) {
				case 'png':
					result = await exportAsPNG(images, `image-arrangement-${timestamp}.png`);
					break;
				case 'jpg':
					result = await exportAsJPEG(images, `image-arrangement-${timestamp}.jpg`);
					break;
				case 'pdf':
					result = await exportAsPDF(images, `image-arrangement-${timestamp}.pdf`);
					break;
			}

			if (!result.success) {
				alert(`Export failed: ${result.error}`);
			}
		} catch (error) {
			console.error('Export error:', error);
			alert('Export failed. Please try again.');
		} finally {
			isExporting = false;
		}
	}

	function handleCanvasClick(e) {
		// Only deselect if clicking directly on canvas background, not on images or controls
		if (
			e.target === canvasRef ||
			(e.target.classList.contains('canvas-area') &&
				!e.target.closest('.control-panel') &&
				!e.target.closest('img'))
		) {
			selectedImageId = null;
		}
	}

	const selectedImage = $derived(images.find((img) => img.id === selectedImageId));

	function handleCropRequest(image) {
		cropImageData = image;
		cropModalOpen = true;
	}

	function handleCropApply(croppedImage) {
		handleImageUpdate(croppedImage);
		cropModalOpen = false;
		cropImageData = null;
	}

	function handleCropClose() {
		cropModalOpen = false;
		cropImageData = null;
	}
</script>

<div
	class="relative min-h-screen overflow-hidden bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900"
>
	<!-- Animated Background -->
	<div class="pointer-events-none fixed inset-0 overflow-hidden">
		<div
			class="animate-blob absolute top-0 left-1/4 h-96 w-96 rounded-full bg-cyan-500/20 blur-3xl"
		></div>
		<div
			class="animate-blob animation-delay-2000 absolute top-1/4 right-1/4 h-96 w-96 rounded-full bg-purple-500/20 blur-3xl"
		></div>
		<div
			class="animate-blob animation-delay-4000 absolute bottom-0 left-1/2 h-96 w-96 rounded-full bg-pink-500/20 blur-3xl"
		></div>
	</div>

	<div class="relative z-10 min-h-screen">
		<!-- Minimal Header -->
		<header class="border-b border-white/10 bg-white/5 backdrop-blur-xl">
			<div class="mx-auto max-w-[1400px] px-6 py-4">
				<div class="flex items-center justify-between">
					<div class="flex items-center gap-3">
						<div
							class="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-cyan-400 to-purple-500 shadow-lg shadow-cyan-500/50"
						>
							<Sparkles class="h-5 w-5 text-white" />
						</div>
						<div>
							<h1 class="text-xl font-light tracking-wide text-white/90">Image Arranger</h1>
							<p class="text-xs font-light text-white/50">A4 Canvas</p>
						</div>
					</div>

					<div class="flex items-center gap-3">
						<!-- Zoom Slider -->
						<div
							class="flex min-w-[200px] items-center gap-3 rounded-xl border border-white/10 bg-white/5 px-4 py-2 backdrop-blur-xl"
						>
							<ZoomOut class="h-4 w-4 flex-shrink-0 text-white/70" />
							<input
								type="range"
								min="25"
								max="200"
								value={canvasScale * 100}
								oninput={(e) => (canvasScale = parseFloat(e.target.value) / 100)}
								class="h-1.5 flex-1 cursor-pointer appearance-none rounded-lg bg-white/10 accent-cyan-500"
							/>
							<span class="min-w-[3.5rem] text-right text-sm font-light text-white/80">
								{Math.round(canvasScale * 100)}%
							</span>
							<ZoomIn class="h-4 w-4 flex-shrink-0 text-white/70" />
						</div>

						<!-- Export -->
						<div class="flex items-center gap-2">
							<button
								onclick={() => exportImage('png')}
								disabled={isExporting || images.length === 0}
								class="rounded-xl bg-gradient-to-r from-cyan-500 to-blue-500 px-4 py-2 text-sm font-light text-white shadow-lg shadow-cyan-500/30 transition-all duration-300 hover:from-cyan-400 hover:to-blue-400 hover:shadow-cyan-500/50 disabled:cursor-not-allowed disabled:opacity-30"
							>
								PNG
							</button>
							<button
								onclick={() => exportImage('pdf')}
								disabled={isExporting || images.length === 0}
								class="rounded-xl bg-gradient-to-r from-purple-500 to-pink-500 px-4 py-2 text-sm font-light text-white shadow-lg shadow-purple-500/30 transition-all duration-300 hover:from-purple-400 hover:to-pink-400 hover:shadow-purple-500/50 disabled:cursor-not-allowed disabled:opacity-30"
							>
								PDF
							</button>
						</div>
					</div>
				</div>
			</div>
		</header>

		<div class="mx-auto max-w-[1400px] px-6 py-8">
			<div class="grid grid-cols-12 gap-6">
				<!-- Sidebar -->
				<aside class="col-span-3 space-y-4">
					<!-- Upload -->
					<div class="rounded-2xl border border-white/10 bg-white/5 p-4 backdrop-blur-xl">
						<ImageUpload onImagesAdded={handleImagesAdded} />
					</div>

					<!-- Image List -->
					{#if images.length > 0}
						<div
							class="custom-scrollbar max-h-[600px] overflow-y-auto rounded-2xl border border-white/10 bg-white/5 p-4 backdrop-blur-xl"
						>
							<div class="mb-4 flex items-center justify-between">
								<h2 class="text-sm font-light tracking-wider text-white/70 uppercase">
									Images ({images.length})
								</h2>
								<button
									onclick={clearAll}
									class="rounded-lg p-1.5 text-white/50 transition-all duration-300 hover:bg-white/10 hover:text-white/80"
								>
									<Trash2 class="h-4 w-4" />
								</button>
							</div>
							<div class="space-y-2">
								{#each images as image (image.id)}
									<button
										onclick={() => handleImageSelect(image.id)}
										class="w-full rounded-xl p-3 text-left transition-all duration-300 {selectedImageId ===
										image.id
											? 'border border-cyan-400/50 bg-gradient-to-r from-cyan-500/20 to-purple-500/20'
											: 'border border-white/10 bg-white/5 hover:border-white/20 hover:bg-white/10'}"
									>
										<div class="flex items-center gap-3">
											<div class="relative">
												<img
													src={image.url}
													alt="Thumbnail"
													class="h-12 w-12 rounded-lg object-cover"
												/>
												{#if selectedImageId === image.id}
													<div class="absolute inset-0 rounded-lg bg-cyan-400/20"></div>
												{/if}
											</div>
											<div class="min-w-0 flex-1">
												<p class="truncate text-xs font-light text-white/80">
													{image.file.name}
												</p>
												<p class="mt-0.5 text-xs text-white/50">
													{Math.round(image.width * image.scale)} × {Math.round(
														image.height * image.scale
													)}
												</p>
											</div>
										</div>
									</button>
								{/each}
							</div>
						</div>
					{/if}

					<!-- Filters Panel -->
					{#if selectedImage}
						<div
							class="animate-slide-in rounded-2xl border border-white/10 bg-white/5 p-4 backdrop-blur-xl"
						>
							<ImageFilters image={selectedImage} onUpdate={handleImageUpdate} />
						</div>
					{/if}
				</aside>

				<!-- Canvas -->
				<main class="col-span-9">
					<div class="rounded-2xl border border-white/10 bg-white/5 p-6 backdrop-blur-xl">
						<div
							class="canvas-area relative mx-auto overflow-visible rounded-lg shadow-2xl"
							style="width: {A4_WIDTH}px; height: {A4_HEIGHT}px; transform: scale({canvasScale}) translate3d(0,0,0); transform-origin: top center; background-color: rgb(255, 255, 255); will-change: transform;"
							bind:this={canvasRef}
							onclick={handleCanvasClick}
						>
							{#if images.length === 0}
								<div class="absolute inset-0 flex items-center justify-center">
									<div class="text-center">
										<div
											class="mx-auto mb-4 flex h-20 w-20 items-center justify-center rounded-2xl border border-white/20 bg-gradient-to-br from-cyan-500/20 to-purple-500/20"
										>
											<Upload class="h-10 w-10 text-white/50" />
										</div>
										<p class="text-sm font-light text-white/60">Drop images to begin</p>
									</div>
								</div>
							{:else}
								{#each images as image (image.id)}
									<ImageItem
										{image}
										isSelected={selectedImageId === image.id}
										onUpdate={handleImageUpdate}
										onDelete={handleImageDelete}
										onSelect={() => handleImageSelect(image.id)}
										onCropRequest={handleCropRequest}
									/>
								{/each}
							{/if}
						</div>

						{#if isExporting}
							<div class="mt-4 text-center">
								<div class="inline-flex items-center gap-2 text-sm text-white/60">
									<div
										class="h-4 w-4 animate-spin rounded-full border-2 border-white/30 border-t-white/80"
									></div>
									<span class="font-light">Exporting...</span>
								</div>
							</div>
						{/if}
					</div>
				</main>
			</div>
		</div>
	</div>

	<!-- Crop Modal -->
	{#if cropModalOpen && cropImageData}
		<CropModal image={cropImageData} onClose={handleCropClose} onApply={handleCropApply} />
	{/if}
</div>

<style>
	@keyframes blob {
		0%,
		100% {
			transform: translate(0, 0) scale(1);
		}
		33% {
			transform: translate(30px, -50px) scale(1.1);
		}
		66% {
			transform: translate(-20px, 20px) scale(0.9);
		}
	}

	@keyframes slide-in {
		from {
			opacity: 0;
			transform: translateY(-10px);
		}
		to {
			opacity: 1;
			transform: translateY(0);
		}
	}

	.animate-blob {
		animation: blob 20s infinite;
	}

	.animate-slide-in {
		animation: slide-in 0.3s ease-out;
	}

	.animation-delay-2000 {
		animation-delay: 2s;
	}

	.animation-delay-4000 {
		animation-delay: 4s;
	}

	.custom-scrollbar::-webkit-scrollbar {
		width: 6px;
	}

	.custom-scrollbar::-webkit-scrollbar-track {
		background: rgba(255, 255, 255, 0.05);
		border-radius: 10px;
	}

	.custom-scrollbar::-webkit-scrollbar-thumb {
		background: rgba(255, 255, 255, 0.2);
		border-radius: 10px;
	}

	.custom-scrollbar::-webkit-scrollbar-thumb:hover {
		background: rgba(255, 255, 255, 0.3);
	}

	.canvas-area {
		transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
	}
</style>
