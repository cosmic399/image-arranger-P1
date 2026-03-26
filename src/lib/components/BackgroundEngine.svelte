<script>
	let { theme = 'professional' } = $props();
</script>

<!-- Doraemon Sky theme: vibrant sky-blue, cyan, and golden-yellow blobs -->
<div class="fixed inset-0 overflow-hidden pointer-events-none z-0 transition-opacity duration-700 {theme !== 'ultimate' ? 'opacity-100' : 'opacity-0'}">
	<div class="absolute -top-[30%] -left-[10%] w-[60%] h-[60%] rounded-full blur-[130px]" style="background: radial-gradient(circle, rgba(0,210,255,0.35), rgba(0,160,220,0.15) 60%, transparent 80%);"></div>
	<div class="absolute top-[20%] -right-[15%] w-[50%] h-[60%] rounded-full blur-[120px]" style="background: radial-gradient(circle, rgba(255,214,10,0.20), rgba(255,180,0,0.08) 60%, transparent 80%);"></div>
	<div class="absolute -bottom-[20%] left-[15%] w-[65%] h-[50%] rounded-full blur-[110px]" style="background: radial-gradient(circle, rgba(0,230,180,0.18), rgba(0,200,255,0.08) 60%, transparent 80%);"></div>
	<div class="absolute top-[50%] left-[40%] w-[35%] h-[40%] rounded-full blur-[100px]" style="background: radial-gradient(circle, rgba(255,80,80,0.12), transparent 70%);"></div>
</div>

<!-- Dark (ultimate) theme: intense lime/crimson neons -->
<div class="fixed inset-0 overflow-hidden pointer-events-none z-0 transition-opacity duration-700 {theme === 'ultimate' ? 'opacity-100' : 'opacity-0'}">
	<div class="animate-blob absolute -top-[40%] -left-[10%] w-[70%] h-[70%] rounded-full opacity-20 blur-[120px] mix-blend-screen" style="background: radial-gradient(circle, #00E5CC, transparent 70%);"></div>
	<div class="animate-blob animation-delay-2000 absolute top-[20%] -right-[20%] w-[60%] h-[80%] rounded-full opacity-10 blur-[150px] mix-blend-screen" style="background: radial-gradient(circle, #FF2D78, transparent 70%);"></div>
	<div class="animate-blob animation-delay-4000 absolute -bottom-[20%] left-[20%] w-[80%] h-[60%] rounded-full opacity-15 blur-[100px] mix-blend-screen" style="background: radial-gradient(circle, #C5F40E, transparent 70%);"></div>
</div>

<style>
	@keyframes blob {
		0% { transform: translate(0px, 0px) scale(1); }
		33% { transform: translate(30px, -50px) scale(1.1); }
		66% { transform: translate(-20px, 20px) scale(0.9); }
		100% { transform: translate(0px, 0px) scale(1); }
	}
	.animate-blob { animation: blob 15s infinite alternate; }
	.animation-delay-2000 { animation-delay: 2s; }
	.animation-delay-4000 { animation-delay: 4s; }
</style>
