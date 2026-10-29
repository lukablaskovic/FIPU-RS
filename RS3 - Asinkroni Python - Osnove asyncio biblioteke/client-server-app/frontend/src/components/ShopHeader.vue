<script setup>
defineProps({
  categories: { type: Array, required: true },
  cartCount: { type: Number, required: true },
})
</script>

<template>
  <header class="flex flex-wrap items-center justify-between gap-5 border-b border-stone-200 py-6">
    <a href="/" class="flex items-center gap-3 text-xl font-bold tracking-tight">
      <img src="/fipu-logo.png" alt="" width="48" height="48" class="h-12 w-12 object-contain">
      <span>FIPU <span class="text-fipu">Webshop</span></span>
    </a>
    <nav aria-label="Main navigation" class="flex flex-wrap items-center gap-x-6 gap-y-3 text-sm font-medium">
      <a v-for="(category, index) in categories" :key="category" :href="`#category-${index}`" class="hover:text-emerald-700">{{ category }}</a>
      <a v-if="cartCount" href="#cart" class="rounded-full bg-stone-900 px-4 py-2 text-white">Cart ({{ cartCount }})</a>
    </nav>
  </header>
</template>
