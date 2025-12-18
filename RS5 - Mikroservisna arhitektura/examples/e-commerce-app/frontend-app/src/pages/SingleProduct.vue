<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, RouterLink } from 'vue-router'
import { getProduct } from '../api/catalog'
import { useCartStore } from '../stores/cart.js'
import { useUiStore } from '../stores/ui'

const route = useRoute()
const cart = useCartStore()
const ui = useUiStore()

const product = ref(null)
const isLoading = ref(false)
const error = ref(null)

function formatMoney(value, currency) {
  const c = currency || 'EUR'
  return new Intl.NumberFormat('de-DE', { style: 'currency', currency: c }).format(
    Number(value) || 0,
  )
}

async function load() {
  const id = route.params.id
  if (!id) return
  isLoading.value = true
  error.value = null
  try {
    product.value = await getProduct(id)
  } catch (e) {
    error.value = e instanceof Error ? e.message : String(e)
    product.value = null
  } finally {
    isLoading.value = false
  }
}

onMounted(load)
watch(() => route.params.id, load)

const hasError = computed(() => Boolean(error.value))

function addToCart() {
  if (!product.value) return
  cart.add(product.value, 1)
  ui.info(product.value?.title || '', { title: 'Dodano u košaricu' })
}
</script>

<template>
  <div class="mx-auto w-full max-w-6xl px-4 py-8">
    <div class="mb-6">
      <RouterLink
        to="/"
        class="group inline-flex cursor-pointer items-center gap-2 text-sm font-semibold text-slate-700 transition hover:text-slate-950"
      >
        <span class="transition group-hover:-translate-x-0.5">←</span>
        Nazad na proizvode
      </RouterLink>
    </div>

    <div
      v-if="isLoading"
      class="rounded-2xl border border-black/10 bg-(--c-surface) p-6 text-slate-700"
    >
      Učitavanje proizvoda…
    </div>

    <div
      v-else-if="hasError"
      class="rounded-2xl border border-black/10 bg-(--c-surface) p-6 text-slate-950"
    >
      <div class="font-semibold">Nije moguće učitati proizvod.</div>
      <div class="mt-1 text-sm text-slate-600">{{ error }}</div>
    </div>

    <div v-else-if="product" class="grid gap-6 lg:grid-cols-2">
      <div class="overflow-hidden rounded-2xl border border-black/10 bg-(--c-surface)">
        <div class="aspect-square overflow-hidden">
          <img :src="product.img" :alt="product.title" class="h-full w-full object-cover" />
        </div>
      </div>

      <div class="rounded-2xl border border-black/10 bg-(--c-surface) p-6">
        <div class="text-xs font-semibold text-slate-500">{{ product.category }}</div>
        <h1 class="mt-2 text-2xl font-semibold tracking-tight text-slate-950 sm:text-3xl">
          {{ product.title }}
        </h1>
        <div class="mt-4 text-2xl font-extrabold tracking-tight text-slate-950">
          {{ formatMoney(product.price, product.currency) }}
        </div>
        <p class="mt-4 text-sm leading-6 text-slate-700">{{ product.desc }}</p>

        <div class="mt-6 flex flex-col gap-3 sm:flex-row">
          <button
            class="cursor-pointer rounded-2xl bg-(--fipu_blue) px-5 py-3 text-sm font-semibold text-slate-950 transition hover:brightness-105 active:scale-[0.99]"
            @click="addToCart"
          >
            Dodaj u košaricu
          </button>
        </div>

        <div class="mt-6 grid grid-cols-3 gap-3">
          <div class="rounded-2xl border border-black/10 bg-slate-50 p-3">
            <div class="text-xs text-slate-500">Shipping</div>
            <div class="mt-1 text-sm font-semibold text-slate-950">
              {{ product.shipping_time || '—' }}
            </div>
          </div>
          <div class="rounded-2xl border border-black/10 bg-slate-50 p-3">
            <div class="text-xs text-slate-500">Returns</div>
            <div class="mt-1 text-sm font-semibold text-slate-950">30 days</div>
          </div>
          <div class="rounded-2xl border border-black/10 bg-slate-50 p-3">
            <div class="text-xs text-slate-500">Support</div>
            <div class="mt-1 text-sm font-semibold text-slate-950">24/7</div>
          </div>
        </div>
      </div>
    </div>

    <div v-else class="rounded-2xl border border-black/10 bg-(--c-surface) p-6">
      <div class="text-slate-950">Proizvod nije pronađen.</div>
      <RouterLink
        to="/"
        class="group mt-3 inline-flex cursor-pointer items-center gap-2 text-sm font-semibold text-(--fipu_blue) transition hover:brightness-105"
      >
        Go back
        <span class="transition group-hover:translate-x-0.5">→</span>
      </RouterLink>
    </div>
  </div>
</template>
