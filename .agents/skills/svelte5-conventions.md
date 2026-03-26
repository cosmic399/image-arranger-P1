---
name: svelte5-conventions
description: Coding conventions, patterns, and rules for writing Svelte 5 components using the runes API. Use whenever writing or reviewing .svelte files in any SvelteKit 5 project.
---

# Svelte 5 Runes — Coding Conventions

## Core Runes Cheatsheet

| Rune | Purpose | Example |
|------|---------|---------|
| `$state(val)` | Reactive local variable | `let count = $state(0)` |
| `$derived(expr)` | Computed value, auto-updates | `const doubled = $derived(count * 2)` |
| `$effect(() => {})` | Side effect when deps change | `$effect(() => { console.log(count) })` |
| `$props()` | Declare component props | `let { name, onUpdate = () => {} } = $props()` |

## State Rules
- Use `$state` for any variable that the template reacts to.
- Use `$derived` instead of `$effect` + manual variable for computed values.
- Never use `$effect` to compute values — only for side effects (DOM manipulation, subscriptions, logging).
- For deeply nested reactive objects, assign a new reference — don't mutate in-place.
  ```js
  // ✅ Correct
  images = images.map(img => img.id === id ? { ...img, x: newX } : img);
  // ❌ Wrong
  images.find(img => img.id === id).x = newX;
  ```

## Props Pattern
```svelte
<script>
  let {
    image,
    onUpdate = () => {},    // Always default callbacks to no-ops
    isSelected = false
  } = $props();
</script>
```
- Always provide default values for optional props.
- Callback props should default to `() => {}` to avoid null checks.

## Event Handling in Svelte 5
```svelte
<!-- ✅ Svelte 5 syntax -->
<button onclick={handleClick}>Click</button>
<input oninput={(e) => (value = e.target.value)} />

<!-- ❌ Svelte 4 syntax (deprecated) -->
<button on:click={handleClick}>Click</button>
```

## Two-Way Binding
```svelte
<!-- ✅ Bind directive still works for form elements -->
<input bind:value={myVar} />

<!-- ✅ Or use bind: on component props -->
<Canvas bind:images={pages[activePageIndex].images} />
```

## Effect Cleanup
```js
$effect(() => {
  const handler = () => { /* ... */ };
  window.addEventListener('resize', handler);
  return () => window.removeEventListener('resize', handler); // Cleanup
});
```

## Component File Structure (Preferred Order)
```svelte
<script>
  // 1. Imports
  // 2. Props ($props)
  // 3. State ($state)
  // 4. Derived ($derived)
  // 5. Functions
  // 6. Effects ($effect) — always last in script
</script>

<!-- Template -->

<style>
  /* Scoped styles */
</style>
```

## Styling Rules
- Use Tailwind utility classes for static styles.
- Use inline `style=` for **all dynamic values** (pixel calculations, conditional transforms).
  ```svelte
  <!-- ✅ Correct -->
  <div style="left: {x}px; top: {y}px; transform: rotate({rotation}deg);">

  <!-- ❌ Wrong — Tailwind can't handle dynamic values -->
  <div class="left-[{x}px]">
  ```

## Performance Tips
- Wrap expensive DOM reads in `requestAnimationFrame` when inside drag/move loops.
- Use `will-change: transform` and `backface-visibility: hidden` for frequently animated elements.
- Use `pointer-events: none` on child elements that shouldn't intercept drag events from parents.
- Use `touch-action: none` on draggable elements to prevent browser scroll interference.

## Avoiding Common Bugs
- **Infinite effect loops**: Don't read and write the same `$state` inside the same `$effect`.
- **Stale closure in event listeners**: Use module-level mutable variables (not `$state`) inside `pointermove`/`pointerup` closures for performance-critical data like mouse coordinates.
- **Svelte 4 vs 5 confusion**: If you see `on:click`, `createEventDispatcher`, or `$: derived`, those are Svelte 4 — rewrite them in Svelte 5 runes style.
