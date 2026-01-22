import { computed, ref } from 'vue'
import { defineStore } from 'pinia'

const STORAGE_KEY = 'vue-shop.cart'

function safeJsonParse(value) {
  try {
    return JSON.parse(value)
  } catch {
    return null
  }
}

function normalizeItem(product, qty) {
  const q = Math.max(1, Number(qty) || 1)
  return {
    id: String(product?.id ?? ''),
    title: String(product?.title ?? ''),
    price: Number(product?.price) || 0,
    currency: product?.currency || 'EUR',
    img: product?.img || '',
    qty: q,
  }
}

export const useCartStore = defineStore('cart', () => {
  const items = ref([])

  function persist() {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(items.value))
  }

  function initFromStorage() {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (!raw) return
    const parsed = safeJsonParse(raw)
    if (Array.isArray(parsed)) items.value = parsed
  }

  function clear() {
    items.value = []
    persist()
  }

  function remove(id) {
    const key = String(id)
    items.value = items.value.filter((i) => String(i.id) !== key)
    persist()
  }

  function setQty(id, qty) {
    const key = String(id)
    const q = Math.max(1, Number(qty) || 1)
    const idx = items.value.findIndex((i) => String(i.id) === key)
    if (idx === -1) return
    items.value[idx] = { ...items.value[idx], qty: q }
    persist()
  }

  function add(product, qty = 1) {
    const next = normalizeItem(product, qty)
    if (!next.id) return
    const idx = items.value.findIndex((i) => String(i.id) === next.id)
    if (idx === -1) {
      items.value = [...items.value, next]
    } else {
      const current = items.value[idx]
      items.value[idx] = { ...current, qty: Math.max(1, (Number(current.qty) || 1) + next.qty) }
    }
    persist()
  }

  const totalItems = computed(() => items.value.reduce((sum, i) => sum + (Number(i.qty) || 0), 0))

  const totalPrice = computed(() =>
    items.value.reduce((sum, i) => sum + (Number(i.qty) || 0) * (Number(i.price) || 0), 0),
  )

  return {
    items,
    initFromStorage,
    add,
    remove,
    setQty,
    clear,
    totalItems,
    totalPrice,
  }
})
