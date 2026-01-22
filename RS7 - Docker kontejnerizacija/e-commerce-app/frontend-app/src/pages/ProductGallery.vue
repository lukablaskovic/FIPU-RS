<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { listProducts } from '../api/catalog'

const products = ref([])
const isLoading = ref(false)
const error = ref(null)

const searchQuery = ref('')
const filtersOpen = ref(false)
const selectedCategories = ref([])

const priceMin = ref(null)
const priceMax = ref(null)
const priceTouched = ref(false)

function formatMoney(value, currency) {
  const c = currency || 'EUR'
  return new Intl.NumberFormat('de-DE', { style: 'currency', currency: c }).format(
    Number(value) || 0,
  )
}

const hasError = computed(() => Boolean(error.value))

const categories = computed(() => {
  const set = new Set()
  for (const p of products.value || []) {
    if (p?.category) set.add(String(p.category))
  }
  return Array.from(set).sort((a, b) => a.localeCompare(b))
})

const priceBounds = computed(() => {
  const prices = (products.value || [])
    .map((p) => Number(p?.price))
    .filter((n) => Number.isFinite(n))
  const min = prices.length ? Math.min(...prices) : 0
  const max = prices.length ? Math.max(...prices) : 0
  return { min, max }
})

watch(
  () => products.value,
  () => {
    if (priceTouched.value) return
    const { min, max } = priceBounds.value
    priceMin.value = min
    priceMax.value = max
  },
  { immediate: true },
)

function normalizeSearch(s) {
  return String(s || '')
    .trim()
    .toLowerCase()
}

function resetFilters() {
  searchQuery.value = ''
  selectedCategories.value = []
  priceTouched.value = false
  const { min, max } = priceBounds.value
  priceMin.value = min
  priceMax.value = max
}

const filteredProducts = computed(() => {
  const q = normalizeSearch(searchQuery.value)
  const cats = new Set((selectedCategories.value || []).map(String))

  const min = Number(priceMin.value)
  const max = Number(priceMax.value)
  const hasMin = Number.isFinite(min)
  const hasMax = Number.isFinite(max)

  return (products.value || []).filter((p) => {
    const title = String(p?.title || '')
    const desc = String(p?.desc || '')

    if (q) {
      const hay = `${title} ${desc}`.toLowerCase()
      if (!hay.includes(q)) return false
    }

    if (cats.size > 0) {
      const c = String(p?.category || '')
      if (!cats.has(c)) return false
    }

    const price = Number(p?.price)
    if (Number.isFinite(price)) {
      if (hasMin && price < min) return false
      if (hasMax && price > max) return false
    }

    return true
  })
})

onMounted(async () => {
  isLoading.value = true
  error.value = null
  try {
    products.value = await listProducts()
  } catch (e) {
    error.value = e instanceof Error ? e.message : String(e)
    products.value = []
  } finally {
    isLoading.value = false
  }
})
</script>

<template>
  <div class="mx-auto w-full max-w-6xl px-4 py-8">
    <div class="mb-6 flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
      <div>
        <h1 class="text-2xl font-semibold tracking-tight text-slate-950 sm:text-3xl">
          Pregledajte sve proizvode iz našeg kataloga
        </h1>
      </div>
      <div class="flex items-center gap-2">
        <input
          placeholder="Traži..."
          v-model="searchQuery"
          class="w-44 rounded-xl border border-black/10 bg-(--c-surface) px-3 py-2 text-sm text-slate-900 placeholder:text-slate-400 outline-none ring-(--fipu_blue) focus:ring-2"
        />
        <button
          class="cursor-pointer rounded-xl bg-(--fipu_blue) px-4 py-2 text-sm font-semibold text-slate-950 transition hover:brightness-105 active:scale-[0.99]"
          @click="filtersOpen = !filtersOpen"
        >
          Filter
        </button>
      </div>
    </div>

    <div v-if="filtersOpen" class="mb-6 rounded-2xl border border-black/10 bg-(--c-surface) p-4">
      <div class="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
        <div class="min-w-0 flex-1">
          <div class="text-sm font-semibold text-slate-950">Kategorije</div>
          <div v-if="categories.length === 0" class="mt-2 text-sm text-slate-600">—</div>
          <div v-else class="mt-2 flex flex-wrap gap-2">
            <label
              v-for="c in categories"
              :key="c"
              class="inline-flex cursor-pointer items-center gap-2 rounded-xl border border-black/10 bg-white px-3 py-2 text-sm font-semibold text-slate-800 transition hover:border-black/20 hover:bg-black/5"
            >
              <input
                type="checkbox"
                class="accent-(--fipu_blue)"
                :value="c"
                v-model="selectedCategories"
              />
              {{ c }}
            </label>
          </div>
        </div>

        <div class="w-full max-w-md">
          <div class="text-sm font-semibold text-slate-950">Raspon cijena</div>
          <div class="mt-2 grid grid-cols-2 gap-2">
            <div>
              <div class="text-xs font-semibold text-slate-500">Min</div>
              <input
                type="number"
                :min="priceBounds.min"
                :max="priceBounds.max"
                class="mt-1 w-full rounded-xl border border-black/10 bg-white px-3 py-2 text-sm text-slate-900 outline-none ring-(--fipu_blue) focus:ring-2"
                v-model.number="priceMin"
                @input="priceTouched = true"
              />
            </div>
            <div>
              <div class="text-xs font-semibold text-slate-500">Max</div>
              <input
                type="number"
                :min="priceBounds.min"
                :max="priceBounds.max"
                class="mt-1 w-full rounded-xl border border-black/10 bg-white px-3 py-2 text-sm text-slate-900 outline-none ring-(--fipu_blue) focus:ring-2"
                v-model.number="priceMax"
                @input="priceTouched = true"
              />
            </div>
          </div>
          <div class="mt-3 flex items-center justify-between gap-2">
            <div class="text-xs font-semibold text-slate-600">
              Prikazuje se <span class="text-slate-950">{{ filteredProducts.length }}</span> /
              {{ products.length }} proizvoda
            </div>
            <button
              type="button"
              class="cursor-pointer rounded-xl border border-black/10 bg-transparent px-3 py-2 text-sm font-semibold text-slate-800 transition hover:border-black/20 hover:bg-black/5 active:scale-[0.99]"
              @click="resetFilters"
            >
              Reset
            </button>
          </div>
        </div>
      </div>
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
      <div class="font-semibold">Nije moguće učitati proizvode.</div>
      <div class="mt-1 text-sm text-slate-600">{{ error }}</div>
    </div>

    <div
      v-else-if="products.length === 0"
      class="rounded-2xl border border-black/10 bg-(--c-surface) p-6 text-slate-700"
    >
      Nema proizvoda u katalogu.
    </div>

    <div
      v-else-if="filteredProducts.length === 0"
      class="rounded-2xl border border-black/10 bg-(--c-surface) p-6 text-slate-700"
    >
      Nema rezultata za vašu pretragu / filter-e.
      <button
        type="button"
        class="ml-2 cursor-pointer font-semibold text-(--fipu_blue) transition hover:brightness-105"
        @click="resetFilters"
      >
        Reset
      </button>
    </div>

    <div class="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-4">
      <RouterLink
        v-for="p in filteredProducts"
        :key="p.id"
        :to="{ name: 'product', params: { id: p.id } }"
        class="group cursor-pointer overflow-hidden rounded-xl border border-black/10 bg-(--c-surface) transition hover:-translate-y-0.5 hover:border-black/20 hover:shadow-md hover:shadow-black/10"
      >
        <div class="aspect-square overflow-hidden bg-slate-50">
          <img
            :src="p.img"
            :alt="p.title"
            class="h-full w-full object-cover transition duration-300 group-hover:scale-[1.03]"
            loading="lazy"
          />
        </div>
        <div class="p-3">
          <div class="text-sm font-semibold leading-5 text-slate-950">{{ p.title }}</div>
          <div class="mt-1 text-xs text-slate-500">{{ p.category }}</div>
          <div class="mt-3 text-xl font-extrabold tracking-tight text-slate-950">
            {{ formatMoney(p.price, p.currency) }}
          </div>
          <div class="mt-3 flex items-center justify-between gap-2">
            <div class="text-xs font-semibold text-slate-600">Besplatna dostava</div>
            <div class="text-xs font-semibold text-(--fipu_blue)">View →</div>
          </div>
        </div>
      </RouterLink>
    </div>
  </div>
</template>
