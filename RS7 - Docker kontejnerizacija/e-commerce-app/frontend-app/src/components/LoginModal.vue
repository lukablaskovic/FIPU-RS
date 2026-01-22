<script setup>
import { computed, onBeforeUnmount, watch } from 'vue'

const props = defineProps({
  open: { type: Boolean, default: false },
  loginUrl: { type: String, required: true },
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
  <Transition name="login-modal">
    <div v-if="show" class="fixed inset-0 z-50">
      <div class="absolute inset-0 bg-black/40 backdrop-blur-[1px]" @click="close"></div>

      <div class="absolute inset-0 flex items-center justify-center p-4">
        <div
          class="w-full max-w-md rounded-2xl border border-black/10 bg-white shadow-xl"
          role="dialog"
          aria-modal="true"
          aria-label="Login"
        >
          <div class="flex items-start justify-between gap-4 border-b border-black/10 px-5 py-4">
            <div>
              <div class="text-sm font-semibold text-slate-950 mb-2">Prijava</div>
              <div class="text-xs text-slate-500">
                Autentifikacija se provodi putem autentifikacijskog mikroservisa
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
            <a
              :href="loginUrl"
              class="inline-flex w-full items-center justify-center rounded-xl bg-(--fipu_blue) px-4 py-3 text-sm font-semibold text-white transition hover:bg-(--fipu_blue)/80 active:scale-[0.99]"
            >
              Nastavi s prijavom
            </a>
          </div>
        </div>
      </div>
    </div>
  </Transition>
</template>

<style scoped>
.login-modal-enter-active,
.login-modal-leave-active {
  transition: opacity 160ms ease;
}

.login-modal-enter-from,
.login-modal-leave-to {
  opacity: 0;
}

.login-modal-enter-active .rounded-2xl,
.login-modal-leave-active .rounded-2xl {
  transition:
    transform 180ms ease,
    opacity 180ms ease;
}

.login-modal-enter-from .rounded-2xl {
  transform: translateY(10px) scale(0.98);
  opacity: 0;
}

.login-modal-leave-to .rounded-2xl {
  transform: translateY(8px) scale(0.98);
  opacity: 0;
}
</style>
