<script setup>
import { computed, onMounted } from 'vue'
import { RouterLink } from 'vue-router'
import { useCartStore } from '../stores/cart.js'

const cart = useCartStore()

onMounted(() => {
  cart.initFromStorage()
})

function formatMoney(value, currency) {
  const c = currency || 'EUR'
  return new Intl.NumberFormat('de-DE', { style: 'currency', currency: c }).format(
    Number(value) || 0,
  )
}

const isEmpty = computed(() => cart.items.length === 0)
</script>

<template>
  <div class="mx-auto w-full max-w-6xl px-4 py-8">
    <div class="mb-6 flex items-center justify-between gap-3">
      <div>
        <h1 class="text-2xl font-semibold tracking-tight text-slate-950 sm:text-3xl">Košarica</h1>
        <div class="mt-1 text-sm text-slate-600">
          {{ cart.totalItems }} artik(a)l • {{ formatMoney(cart.totalPrice, 'EUR') }}
        </div>
      </div>
      <RouterLink
        to="/"
        class="group inline-flex cursor-pointer items-center gap-2 text-sm font-semibold text-slate-700 transition hover:text-slate-950"
      >
        <span class="transition group-hover:-translate-x-0.5">←</span>
        Nazad na proizvode
      </RouterLink>
    </div>

    <div
      v-if="isEmpty"
      class="rounded-2xl border border-black/10 bg-(--c-surface) p-6 text-slate-700"
    >
      Your cart is empty.
    </div>

    <div v-else class="grid gap-4 lg:grid-cols-3">
      <div class="lg:col-span-2">
        <div
          class="divide-y divide-black/10 overflow-hidden rounded-2xl border border-black/10 bg-(--c-surface)"
        >
          <div v-for="item in cart.items" :key="item.id" class="flex gap-4 p-4">
            <div class="h-20 w-20 overflow-hidden rounded-xl border border-black/10 bg-slate-50">
              <img
                v-if="item.img"
                :src="item.img"
                :alt="item.title"
                class="h-full w-full object-cover"
                loading="lazy"
              />
            </div>
            <div class="min-w-0 flex-1">
              <div class="flex items-start justify-between gap-3">
                <div class="min-w-0">
                  <div class="truncate text-sm font-semibold text-slate-950">{{ item.title }}</div>
                  <div class="mt-1 text-sm font-extrabold tracking-tight text-slate-950">
                    {{ formatMoney(item.price, item.currency) }}
                  </div>
                </div>
                <button
                  type="button"
                  class="cursor-pointer rounded-lg px-2 py-1 text-sm font-semibold text-slate-600 transition hover:bg-black/5 hover:text-slate-950"
                  @click="cart.remove(item.id)"
                >
                  Ukloni
                </button>
              </div>

              <div class="mt-3 flex items-center gap-3">
                <label class="text-xs font-semibold text-slate-500">Qty</label>
                <input
                  type="number"
                  min="1"
                  class="w-20 rounded-xl border border-black/10 bg-white px-3 py-2 text-sm text-slate-900 outline-none ring-(--fipu_blue) focus:ring-2"
                  :value="item.qty"
                  @input="cart.setQty(item.id, $event.target.value)"
                />
                <div class="ml-auto text-sm font-semibold text-slate-700">
                  Ukupno:
                  <span class="font-extrabold text-slate-950">
                    {{
                      formatMoney(
                        (Number(item.qty) || 0) * (Number(item.price) || 0),
                        item.currency,
                      )
                    }}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="rounded-2xl border border-black/10 bg-(--c-surface) p-5">
        <div class="text-sm font-semibold text-slate-950">Sažetak</div>
        <div class="mt-3 flex items-center justify-between text-sm text-slate-700">
          <span>Stavke</span>
          <span class="font-semibold text-slate-950">{{ cart.totalItems }}</span>
        </div>
        <div class="mt-2 flex items-center justify-between text-sm text-slate-700">
          <span>Ukupno za platiti</span>
          <span class="text-lg font-extrabold tracking-tight text-slate-950">
            {{ formatMoney(cart.totalPrice, 'EUR') }}
          </span>
        </div>
        <button
          type="button"
          class="mt-4 w-full cursor-pointer rounded-2xl bg-(--fipu_blue) px-5 py-3 text-sm font-semibold text-slate-950 transition hover:brightness-105 active:scale-[0.99]"
        >
          <RouterLink to="/checkout" class="block w-full">Unos osobnih podataka</RouterLink>
        </button>
        <button
          type="button"
          class="mt-2 w-full cursor-pointer rounded-2xl border border-black/10 bg-transparent px-5 py-3 text-sm font-semibold text-slate-800 transition hover:border-black/20 hover:bg-black/5 active:scale-[0.99]"
          @click="cart.clear()"
        >
          Očisti košaricu
        </button>
      </div>
    </div>
  </div>
</template>
