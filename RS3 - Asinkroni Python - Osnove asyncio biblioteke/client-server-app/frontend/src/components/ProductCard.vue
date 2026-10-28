<script setup>
import { MotionDirective } from '@vueuse/motion'
import { formatPrice } from '../data/products.js'

defineProps({ product: { type: Object, required: true } })
defineEmits(['add-to-cart'])
const vMotion = MotionDirective()
</script>

<template>
  <article
    v-motion
    :initial="{ y: 0 }"
    :hovered="{ y: -6 }"
    :duration="180"
    class="product-card"
  >
    <div class="flex aspect-square items-center justify-center rounded-lg bg-white p-5">
      <img :src="product.image" :alt="product.name" width="300" height="300" loading="lazy" class="h-full w-full object-contain">
    </div>
    <p class="mt-5 text-xs uppercase tracking-widest text-stone-500">{{ product.category }}</p>
    <h4 class="mt-1 font-semibold">{{ product.name }}</h4>
    <div class="mt-3 flex items-center justify-between gap-2">
      <span class="text-sm">{{ formatPrice(product.price) }}</span>
      <button type="button" :aria-label="`Add ${product.name} to cart`" class="rounded-full border border-stone-300 px-3 py-1.5 text-xs font-medium hover:border-emerald-700 hover:bg-emerald-50" @click="$emit('add-to-cart', product)">Add to cart +</button>
    </div>
  </article>
</template>
