import { ref } from 'vue'
import { defineStore } from 'pinia'

function makeId() {
  return `${Date.now()}-${Math.random().toString(16).slice(2)}`
}

export const useUiStore = defineStore('ui', () => {
  const toasts = ref([])

  // keep timeout handles outside of reactivity
  const timeouts = new Map()

  function removeToast(id) {
    const key = String(id)
    const t = timeouts.get(key)
    if (t) {
      clearTimeout(t)
      timeouts.delete(key)
    }
    toasts.value = toasts.value.filter((x) => String(x.id) !== key)
  }

  function toast(payload) {
    const id = payload?.id ? String(payload.id) : makeId()
    const type = payload?.type || 'info' // info | success | warning | error
    const title = payload?.title ?? null
    const message = payload?.message ?? ''
    const durationMs = Number.isFinite(Number(payload?.durationMs))
      ? Number(payload.durationMs)
      : 2600

    const item = {
      id,
      type,
      title,
      message,
      durationMs,
      createdAt: Date.now(),
    }

    toasts.value = [item, ...toasts.value].slice(0, 5)

    if (durationMs > 0) {
      const handle = setTimeout(() => removeToast(id), durationMs)
      timeouts.set(String(id), handle)
    }

    return id
  }

  const info = (message, opts = {}) => toast({ ...opts, type: 'info', message })
  const success = (message, opts = {}) => toast({ ...opts, type: 'success', message })
  const warning = (message, opts = {}) => toast({ ...opts, type: 'warning', message })
  const error = (message, opts = {}) => toast({ ...opts, type: 'error', message })

  return {
    toasts,
    toast,
    removeToast,
    info,
    success,
    warning,
    error,
  }
})
