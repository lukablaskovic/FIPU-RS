<script setup>
const props = defineProps({
  type: { type: String, default: 'info' }, // info | success | warning | error
  title: { type: String, default: '' },
  text: { type: String, default: '' },
})

defineEmits(['close'])

function variantClasses(type) {
  switch (type) {
    case 'success':
      return {
        wrap: 'border-emerald-200 bg-emerald-50',
        title: 'text-emerald-950',
        msg: 'text-emerald-800',
        dot: 'bg-emerald-500',
      }
    case 'warning':
      return {
        wrap: 'border-amber-200 bg-amber-50',
        title: 'text-amber-950',
        msg: 'text-amber-800',
        dot: 'bg-amber-500',
      }
    case 'error':
      return {
        wrap: 'border-rose-200 bg-rose-50',
        title: 'text-rose-950',
        msg: 'text-rose-800',
        dot: 'bg-rose-500',
      }
    case 'info':
    default:
      return {
        wrap: 'border-sky-200 bg-sky-50',
        title: 'text-sky-950',
        msg: 'text-sky-800',
        dot: 'bg-sky-500',
      }
  }
}
</script>

<template>
  <div
    class="pointer-events-auto overflow-hidden rounded-2xl border shadow-lg shadow-black/10"
    :class="variantClasses(props.type).wrap"
    :role="props.type === 'error' ? 'alert' : 'status'"
    aria-live="polite"
  >
    <div class="flex items-start gap-3 px-4 py-3">
      <div class="mt-1 h-2.5 w-2.5 rounded-full" :class="variantClasses(props.type).dot"></div>

      <div class="min-w-0 flex-1">
        <div
          v-if="props.title"
          class="text-sm font-semibold"
          :class="variantClasses(props.type).title"
        >
          {{ props.title }}
        </div>
        <div class="text-sm leading-5" :class="variantClasses(props.type).msg">
          {{ props.text }}
        </div>
      </div>

      <button
        type="button"
        class="rounded-lg px-2 py-1 text-sm font-semibold text-black/50 transition hover:bg-black/5 hover:text-black/80"
        aria-label="Close"
        @click="$emit('close')"
      >
        ✕
      </button>
    </div>
  </div>
</template>

