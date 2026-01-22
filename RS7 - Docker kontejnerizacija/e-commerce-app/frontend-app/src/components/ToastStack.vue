<script setup>
import { computed } from 'vue'
import { useUiStore } from '../stores/ui'
import Toast from './Toast.vue'

const ui = useUiStore()

const items = computed(() => ui.toasts)
</script>

<template>
  <div class="pointer-events-none fixed bottom-4 right-4 z-60 w-[min(92vw,380px)]">
    <TransitionGroup name="toast" tag="div" class="flex flex-col gap-3">
      <Toast
        v-for="t in items"
        :key="t.id"
        :type="t.type"
        :title="t.title"
        :text="t.message"
        @close="ui.removeToast(t.id)"
      />
    </TransitionGroup>
  </div>
</template>

<style scoped>
.toast-enter-active,
.toast-leave-active {
  transition:
    opacity 160ms ease,
    transform 180ms ease;
}

.toast-enter-from,
.toast-leave-to {
  opacity: 0;
  transform: translateY(10px) scale(0.98);
}
</style>
