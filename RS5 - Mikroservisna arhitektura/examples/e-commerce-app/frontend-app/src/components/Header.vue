<script setup>
import Navbar from './Navbar.vue'
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { useCartStore } from '../stores/cart.js'

const auth = useAuthStore()
const cart = useCartStore()
const router = useRouter()

onMounted(() => {
  auth.initFromStorage()
  cart.initFromStorage()
})
</script>

<template>
  <header class="border-b border-black/10 bg-(--c-surface)">
    <div class="mx-auto flex max-w-6xl items-center justify-between gap-4 px-4 py-4">
      <button
        type="button"
        class="flex cursor-pointer items-center gap-3 border-0 bg-transparent p-0 text-left"
        aria-label="Go to homepage"
        @click="router.push('/')"
      >
        <img src="/fipu_hr.png" alt="FIPU" class="h-14 w-14 rounded-lg object-contain" />
        <div class="leading-tight">
          <div class="text-sm font-semibold tracking-wide text-slate-950">E-commerce App</div>
          <div class="text-xs text-slate-500">
            FIPU RS - Demonstracija mikroservisne arhitekture
          </div>
        </div>
      </button>
      <Navbar />
    </div>
  </header>
</template>
