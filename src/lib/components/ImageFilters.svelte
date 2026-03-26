<script>
	import { ImageOff, Palette, RotateCcw } from 'lucide-svelte';

	let { image, onUpdate = () => {} } = $props();

	function toggleFilter(filterName) {
		const newFilters = { ...image.filters, [filterName]: !image.filters[filterName] };
		onUpdate({ ...image, filters: newFilters });
	}

	function resetFilters() {
		onUpdate({
			...image,
			filters: { invert: false, grayscale: false, sepia: false, brightness: 100, contrast: 100, saturate: 100 }
		});
	}

	function updateFilterValue(filterName, value) {
		const newFilters = { ...image.filters, [filterName]: parseInt(value) };
		onUpdate({ ...image, filters: newFilters });
	}
</script>

<div class="space-y-4">
	<div class="flex items-center justify-between mb-4">
		<h3 class="text-xs font-semibold uppercase tracking-wider flex items-center gap-2" style="color: var(--text-dim);">
			<Palette class="w-4 h-4" />
			Filters
		</h3>
		<button
			onclick={resetFilters}
			class="p-1.5 rounded-lg transition-all duration-200"
			style="color: var(--text-muted); background: transparent;"
			onmouseenter={(e) => { e.currentTarget.style.background = 'var(--tile-bg)'; e.currentTarget.style.color = 'var(--text-sub)'; }}
			onmouseleave={(e) => { e.currentTarget.style.background = 'transparent'; e.currentTarget.style.color = 'var(--text-muted)'; }}
			title="Reset Filters"
		>
			<RotateCcw class="w-4 h-4" />
		</button>
	</div>

	<!-- Toggle Filters -->
	<div class="grid grid-cols-2 gap-2">
		<button
			onclick={() => toggleFilter('invert')}
			class="p-3 rounded-xl border-2 transition-all duration-300"
			style={image.filters.invert
				? 'border-color: var(--accent); background: var(--accent-soft); color: var(--accent);'
				: 'border-color: var(--tile-border); background: var(--tile-bg); color: var(--text-dim);'}
		>
			<div class="flex items-center gap-2 justify-center">
				<ImageOff class="w-4 h-4 flex-shrink-0" />
				<span class="text-xs font-medium">Negative</span>
			</div>
		</button>
		<button
			onclick={() => toggleFilter('grayscale')}
			class="p-3 rounded-xl border-2 transition-all duration-300"
			style={image.filters.grayscale
				? 'border-color: var(--accent); background: var(--accent-soft); color: var(--accent);'
				: 'border-color: var(--tile-border); background: var(--tile-bg); color: var(--text-dim);'}
		>
			<div class="flex items-center gap-2 justify-center">
				<ImageOff class="w-4 h-4 flex-shrink-0" />
				<span class="text-xs font-medium">Grayscale</span>
			</div>
		</button>
	</div>

	<!-- Slider Controls -->
	<div class="space-y-4">
		{#each [
			{ key: 'brightness', label: 'Brightness', value: image.filters.brightness },
			{ key: 'contrast',   label: 'Contrast',   value: image.filters.contrast   },
			{ key: 'saturate',   label: 'Saturation', value: image.filters.saturate   }
		] as slider}
			<div>
				<div class="flex items-center justify-between mb-1.5">
					<label for="filter-{slider.key}" class="text-xs font-medium" style="color: var(--text-dim);">{slider.label}</label>
					<span class="text-xs tabular-nums" style="color: var(--accent);">{slider.value}%</span>
				</div>
				<input
					id="filter-{slider.key}"
					type="range"
					min="0"
					max="200"
					value={slider.value}
					oninput={(e) => updateFilterValue(slider.key, e.target.value)}
					class="w-full h-1.5 rounded-lg appearance-none cursor-pointer"
					style="background: var(--slider-track); accent-color: var(--accent);"
				/>
			</div>
		{/each}
	</div>
</div>
