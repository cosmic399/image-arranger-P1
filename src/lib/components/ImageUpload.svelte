<script>
	import { Upload } from 'lucide-svelte';
	import { loadImage, isValidImageFile } from '../utils/imageUtils.js';

	let { onImagesAdded = () => {} } = $props();

	let isDragging = $state(false);
	let fileInput = $state(null);

	function handleDragOver(e) { e.preventDefault(); e.stopPropagation(); isDragging = true; }
	function handleDragLeave(e) { e.preventDefault(); e.stopPropagation(); isDragging = false; }

	function handleDrop(e) {
		e.preventDefault(); e.stopPropagation(); isDragging = false;
		const files = Array.from(e.dataTransfer.files).filter(isValidImageFile);
		processFiles(files);
	}

	function handleFileSelect(e) {
		const files = Array.from(e.target.files).filter(isValidImageFile);
		processFiles(files);
		e.target.value = '';
	}

	async function processFiles(files) {
		if (files.length === 0) return;
		try {
			const images = await Promise.all(files.map(loadImage));
			onImagesAdded(images);
		} catch (error) {
			alert(error.message === 'File format not supported' ? 'File format not supported.' : 'Error loading images. Please try again.');
		}
	}

	function openFileDialog() { fileInput?.click(); }
</script>

<div
	class="relative rounded-xl border-2 border-dashed p-6 transition-all duration-300 cursor-pointer"
	style={isDragging
		? 'border-color: var(--accent); background: var(--accent-soft);'
		: 'border-color: var(--tile-border); background: var(--tile-bg);'}
	ondragover={handleDragOver}
	ondragleave={handleDragLeave}
	ondrop={handleDrop}
	role="button"
	tabindex="0"
	onclick={openFileDialog}
	onkeydown={(e) => e.key === 'Enter' && openFileDialog()}
>
	<input bind:this={fileInput} type="file" accept="image/*" multiple class="hidden" onchange={handleFileSelect} />

	<div class="flex flex-col items-center justify-center space-y-3 text-center">
		<div
			class="rounded-xl p-3 transition-all duration-300"
			style="border: 1px solid var(--accent-border); background: var(--accent-soft);"
		>
			<Upload class="h-6 w-6" style="color: var(--accent);" />
		</div>
		<div>
			<p class="text-sm font-medium" style="color: var(--text-sub);">Drop or click to upload</p>
			<p class="mt-1 text-xs" style="color: var(--text-muted);">PNG · JPG · GIF · WebP</p>
		</div>
	</div>
</div>
