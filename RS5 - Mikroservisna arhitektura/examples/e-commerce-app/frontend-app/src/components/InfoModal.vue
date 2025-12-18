<script setup>
import { computed, onBeforeUnmount, watch } from 'vue'

const props = defineProps({
  open: { type: Boolean, default: false },
  title: { type: String, default: 'Info' },
  message: { type: String, default: '' },
  buttonText: { type: String, default: 'U redu' },
  maxWidthClass: { type: String, default: 'max-w-md' },
})

const emit = defineEmits(['close'])

const show = computed(() => props.open)

function close() {
  emit('close')
}

function onKeydown(e) {
  if (e.key === 'Escape') close()
}

watch(
  () => props.open,
  (isOpen) => {
    if (isOpen) window.addEventListener('keydown', onKeydown)
    else window.removeEventListener('keydown', onKeydown)
  },
  { immediate: true },
)

onBeforeUnmount(() => {
  window.removeEventListener('keydown', onKeydown)
})
</script>

<template>
  <Transition name="info-modal">
    <div v-if="show" class="fixed inset-0 z-50">
      <div class="absolute inset-0 bg-black/40 backdrop-blur-[1px]" @click="close"></div>

      <div class="absolute inset-0 flex items-center justify-center p-4">
        <div
          class="w-full rounded-2xl border border-black/10 bg-white shadow-xl"
          :class="props.maxWidthClass"
          role="dialog"
          aria-modal="true"
          aria-label="Info"
        >
          <div class="flex items-start justify-between gap-4 border-b border-black/10 px-5 py-4">
            <div>
              <div class="text-sm font-semibold text-slate-950">{{ title }}</div>
              <div v-if="message" class="mt-2 text-xs text-slate-600">
                {{ message }}
              </div>
            </div>
            <button
              type="button"
              class="rounded-md p-2 text-slate-500 transition hover:bg-black/5 hover:text-slate-900 cursor-pointer"
              aria-label="Close"
              @click="close"
            >
              ✕
            </button>
          </div>

          <div class="px-5 py-5">
            <slot name="body"></slot>
          </div>

          <div class="border-t border-black/10 px-5 py-4">
            <slot name="footer">
              <button
                type="button"
                class="inline-flex w-full cursor-pointer items-center justify-center rounded-xl bg-(--fipu_blue) px-4 py-3 text-sm font-semibold text-white transition hover:bg-(--fipu_blue)/80 active:scale-[0.99]"
                @click="close"
              >
                {{ buttonText }}
              </button>
            </slot>
          </div>
        </div>
      </div>
    </div>
  </Transition>
</template>

<style scoped>
.info-modal-enter-active,
.info-modal-leave-active {
  transition: opacity 160ms ease;
}

.info-modal-enter-from,
.info-modal-leave-to {
  opacity: 0;
}

.info-modal-enter-active .rounded-2xl,
.info-modal-leave-active .rounded-2xl {
  transition:
    transform 180ms ease,
    opacity 180ms ease;
}

.info-modal-enter-from .rounded-2xl {
  transform: translateY(10px) scale(0.98);
  opacity: 0;
}

.info-modal-leave-to .rounded-2xl {
  transform: translateY(8px) scale(0.98);
  opacity: 0;
}
</style>
