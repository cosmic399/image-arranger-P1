import { jsPDF } from 'jspdf';
import { applyFilters } from './imageUtils.js';

// A4 Dimensions (matching +page.svelte)
const A4_WIDTH = 794;
const A4_HEIGHT = 1123;

/**
 * Helper to load an image source for Canvas
 */
function loadImageForCanvas(url) {
	return new Promise((resolve, reject) => {
		const img = new Image();
		img.crossOrigin = 'anonymous';
		img.onload = () => resolve(img);
		img.onerror = reject;
		img.src = url;
	});
}

/**
 * Re-render the scene onto a high-res canvas (WYSIWYG)
 */
async function renderSceneToCanvas(images, scaleFactor = 2) {
	const canvas = document.createElement('canvas');
	canvas.width = A4_WIDTH * scaleFactor;
	canvas.height = A4_HEIGHT * scaleFactor;
	const ctx = canvas.getContext('2d');

	// Scale context to match resolution
	ctx.scale(scaleFactor, scaleFactor);

	// White background
	ctx.fillStyle = '#ffffff';
	ctx.fillRect(0, 0, A4_WIDTH, A4_HEIGHT);

	// Sort by zIndex (lowest first)
	const sortedImages = [...images].sort((a, b) => a.zIndex - b.zIndex);

	for (const imgData of sortedImages) {
		try {
			const imgValues = await loadImageForCanvas(imgData.url);

			// Support non-uniform scaling (fallback to .scale if X/Y not present for backward compat)
			const sX = imgData.scaleX ?? imgData.scale;
			const sY = imgData.scaleY ?? imgData.scale;

			const width = imgData.width * sX;
			const height = imgData.height * sY;

			// Center coordinates for rotation
			const centerX = imgData.x + width / 2;
			const centerY = imgData.y + height / 2;

			ctx.save();

			// Apply Transforms
			ctx.translate(centerX, centerY);
			ctx.rotate((imgData.rotation * Math.PI) / 180);
			// Draw centered
			ctx.translate(-width / 2, -height / 2);

			// Apply Filters
			// Note: ctx.filter expects standard CSS filter string
			ctx.filter = applyFilters(imgData);

			ctx.drawImage(imgValues, 0, 0, width, height);

			ctx.restore();
		} catch (err) {
			console.error(`Failed to render image ${imgData.id}`, err);
		}
	}

	return canvas;
}

/**
 * Export canvas area as PNG (Optimized with Blob)
 */
export async function exportAsPNG(images, filename = 'image-arrangement.png') {
	try {
		const canvas = await renderSceneToCanvas(images, 2); // 2x resolution

		return new Promise((resolve) => {
			canvas.toBlob((blob) => {
				if (!blob) {
					resolve({ success: false, error: 'Blob creation failed' });
					return;
				}
				const url = URL.createObjectURL(blob);
				const link = document.createElement('a');
				link.download = filename;
				link.href = url;
				link.click();

				// Cleanup memory
				setTimeout(() => URL.revokeObjectURL(url), 100);
				resolve({ success: true });
			}, 'image/png');
		});
	} catch (error) {
		console.error('PNG Export Error:', error);
		return { success: false, error: error.message };
	}
}

/**
 * Export canvas area as JPEG (Optimized with Blob & Compression)
 */
export async function exportAsJPEG(images, filename = 'image-arrangement.jpg', quality = 0.7) {
	try {
		const canvas = await renderSceneToCanvas(images, 2); // 2x resolution

		return new Promise((resolve) => {
			canvas.toBlob((blob) => {
				if (!blob) {
					resolve({ success: false, error: 'Blob creation failed' });
					return;
				}
				const url = URL.createObjectURL(blob);
				const link = document.createElement('a');
				link.download = filename;
				link.href = url;
				link.click();

				// Cleanup memory
				setTimeout(() => URL.revokeObjectURL(url), 100);
				resolve({ success: true });
			}, 'image/jpeg', quality);
		});
	} catch (error) {
		console.error('JPEG Export Error:', error);
		return { success: false, error: error.message };
	}
}

/**
 * Export canvas area as PDF (Optimized size)
 */
export async function exportAsPDF(images, filename = 'image-arrangement.pdf', format = 'a4') {
	try {
		// Use 2x scale for sharpness (1588px width), then compress
		const canvas = await renderSceneToCanvas(images, 2);

		// Use JPEG compression (0.7) for significantly smaller PDF size
		const imgData = canvas.toDataURL('image/jpeg', 0.7);

		// PDF A4 points: 595.28 x 841.89
		// We map our canvas 1:1 to A4
		const pdf = new jsPDF({
			orientation: 'portrait',
			unit: 'pt',
			format: 'a4'
		});

		const pdfWidth = pdf.internal.pageSize.getWidth();
		const pdfHeight = pdf.internal.pageSize.getHeight();

		pdf.addImage(imgData, 'JPEG', 0, 0, pdfWidth, pdfHeight);
		pdf.save(filename);

		return { success: true };
	} catch (error) {
		console.error('PDF Export Error:', error);
		return { success: false, error: error.message };
	}
}
