<script setup>
import { computed } from 'vue'
import { formatPrice } from '../data/products.js'

const props = defineProps({ items: { type: Array, required: true } })
defineEmits(['remove', 'increase', 'decrease'])
const groupedItems = computed(() => {
  const groups = new Map()
  for (const product of props.items) {
    const existing = groups.get(product.id)
    if (existing) existing.quantity++
    else groups.set(product.id, { product, quantity: 1 })
  }
  return [...groups.values()]
})
const total = computed(() => props.items.reduce((sum, product) => sum + product.price, 0))
</script>

<template>
  <section
    v-if="items.length"
    id="cart"
    aria-labelledby="cart-heading"
    class="fixed inset-x-0 bottom-0 z-50 max-h-[40dvh] overflow-y-auto border-t border-stone-200 bg-white p-5 pb-[max(1.25rem,env(safe-area-inset-bottom))] shadow-lg sm:px-8"
  >
    <div class="mx-auto max-w-6xl">
      <div class="flex flex-wrap items-center justify-between gap-3">
        <h2 id="cart-heading" class="text-xl font-semibold">Your cart</h2>
        <p role="status" aria-atomic="true" class="text-sm">{{ items.length }} items · <strong>{{ formatPrice(total) }}</strong></p>
      </div>
      <ul class="mt-3 divide-y divide-stone-100">
        <li v-for="{ product, quantity } in groupedItems" :key="product.id" class="flex flex-wrap items-center justify-between gap-3 py-3 text-sm">
          <span>{{ product.name }} × {{ quantity }} · {{ formatPrice(product.price * quantity) }}</span>
          <div class="flex items-center gap-3">
            <div class="flex items-center rounded-full border border-stone-300">
              <button type="button" :aria-label="`Decrease quantity of ${product.name}`" class="h-11 w-11 rounded-full text-lg hover:bg-stone-100" @click="$emit('decrease', items.indexOf(product))">−</button>
              <span class="min-w-6 text-center tabular-nums" :aria-label="`Quantity: ${quantity}`">{{ quantity }}</span>
              <button type="button" :aria-label="`Increase quantity of ${product.name}`" class="h-11 w-11 rounded-full text-lg hover:bg-stone-100" @click="$emit('increase', product)">+</button>
            </div>
            <button type="button" :aria-label="`Remove all ${product.name} from cart`" class="text-stone-600 underline hover:text-stone-900" @click="$emit('remove', product.id)">Remove</button>
          </div>
        </li>
      </ul>
    </div>
  </section>
</template>
