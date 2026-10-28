<script setup>
import { ref } from 'vue'
import ProductCard from './components/ProductCard.vue'
import ShoppingCart from './components/ShoppingCart.vue'
import { products } from './data/products.js'

const categories = [...new Set(products.map((product) => product.category))]
// shortcut: cart is kept in memory, add persistence when the shop needs saved carts.
const cart = ref([])
</script>

<template>
  <div class="mx-auto max-w-6xl px-5 sm:px-8">
    <header class="flex flex-wrap items-center justify-between gap-5 border-b border-stone-200 py-6">
      <a href="/" class="flex items-center gap-3 text-xl font-bold tracking-tight">
        <img src="/fipu-logo.png" alt="" width="48" height="48" class="h-12 w-12 object-contain">
        <span>FIPU <span class="text-fipu">Webshop</span></span>
      </a>
      <nav aria-label="Main navigation" class="flex flex-wrap items-center gap-x-6 gap-y-3 text-sm font-medium">
        <a v-for="(category, index) in categories" :key="category" :href="`#category-${index}`" class="hover:text-emerald-700">{{ category }}</a>
        <a v-if="cart.length" href="#cart" class="rounded-full bg-stone-900 px-4 py-2 text-white">Cart ({{ cart.length }})</a>
      </nav>
    </header>

    <main>
      <section class="py-16 sm:py-24">
        <h1 class="max-w-2xl text-5xl font-semibold leading-tight tracking-tight sm:text-6xl">Good things.<br>Simple essentials.</h1>
        <p class="mt-6 max-w-md text-lg leading-relaxed text-stone-600">A few favorites for your desk, your studies, and everything in between.</p>
        <a href="#products" class="mt-8 inline-block border-b border-stone-900 pb-1 text-sm font-semibold">Explore the collection <span aria-hidden="true">↗</span></a>
      </section>

      <section id="products" aria-labelledby="products-heading" class="scroll-mt-6 pb-14">
        <div class="mb-6 flex items-baseline justify-between gap-4">
          <h2 id="products-heading" class="text-2xl font-semibold tracking-tight">Electronics</h2>
          <p class="text-sm text-stone-500">{{ products.length }} products</p>
        </div>
        <section v-for="(category, index) in categories" :id="`category-${index}`" :key="category" :aria-label="category" class="mt-10 scroll-mt-6">
          <h3 class="mb-5 text-xl font-semibold">{{ category }}</h3>
          <div class="grid gap-8 sm:grid-cols-2 lg:grid-cols-4">
            <ProductCard
              v-for="product in products.filter((item) => item.category === category)"
              :key="product.id"
              :product="product"
              @add-to-cart="cart.push($event)"
            />
          </div>
        </section>
      </section>


    </main>
    <footer class="flex flex-wrap justify-between gap-3 border-t border-stone-200 py-6 text-xs text-stone-500">
      <p>FIPU Webshop</p>
      <p>
        A part of <a href="https://github.com/lukablaskovic/FIPU-RS" target="_blank" rel="noopener noreferrer" class="underline hover:text-stone-900">Distributed Systems</a>
        course on <a href="https://fipu.unipu.hr/fipu/en/study_programmes/university_graduate_study_of_informatics" target="_blank" rel="noopener noreferrer" class="underline hover:text-stone-900">University graduate study of Informatics</a>.
      </p>
    </footer>
    <div v-if="cart.length" aria-hidden="true" class="h-[40dvh]"></div>
    <ShoppingCart
      :items="cart"
      @increase="cart.push($event)"
      @decrease="cart.splice($event, 1)"
      @remove="cart = cart.filter((product) => product.id !== $event)"
    />
  </div>
</template>
