<script setup>
import { computed, onMounted, ref } from 'vue'
import { RouterLink, useRouter } from 'vue-router'

import { createOrder } from '../api/orders'
import { ensureUser, inferConnectionFromAuthUser } from '../api/users'
import { useAuthStore } from '../stores/auth'
import { useCartStore } from '../stores/cart'
import { useUiStore } from '../stores/ui'

const router = useRouter()
const auth = useAuthStore()
const cart = useCartStore()
const ui = useUiStore()

function formatMoney(value, currency) {
  const c = currency || 'EUR'
  return new Intl.NumberFormat('de-DE', { style: 'currency', currency: c }).format(
    Number(value) || 0,
  )
}

const isEmpty = computed(() => cart.items.length === 0)

const ime = ref('')
const prezime = ref('')
const adresaDostave = ref('')
const brojTelefona = ref('')
const emailAdresa = ref('')
const zelimPotvrdu = ref(false)

onMounted(() => {
  cart.initFromStorage()

  if (auth.user?.email && !emailAdresa.value) {
    emailAdresa.value = String(auth.user.email)
  }
})

const isSubmitting = ref(false)

function newClientRequestId() {
  try {
    if (typeof crypto !== 'undefined' && typeof crypto.randomUUID === 'function') {
      return crypto.randomUUID()
    }
  } catch {}
  return `${Date.now()}-${Math.random().toString(16).slice(2)}`
}

const isFormValid = computed(() => {
  return (
    ime.value.trim().length > 0 &&
    prezime.value.trim().length > 0 &&
    adresaDostave.value.trim().length > 0 &&
    brojTelefona.value.trim().length > 0 &&
    emailAdresa.value.trim().length > 0 &&
    cart.items.length > 0
  )
})

async function submitOrder() {
  if (!auth.isAuthenticated) {
    ui.error('Za narudžbu se morate prijaviti.')
    return
  }

  if (!isFormValid.value) {
    ui.error('Molimo ispunite sva polja.')
    return
  }

  isSubmitting.value = true
  try {
    const email = auth.user?.email ? String(auth.user.email) : emailAdresa.value
    const connection = inferConnectionFromAuthUser(auth.user)
    const accessToken = auth.session?.token?.access_token

    const ensured = await ensureUser({ email, connection })
    const userId = ensured?.id ? String(ensured.id) : null
    if (!userId) throw new Error('user_service_missing_id')

    const clientRequestId = newClientRequestId()
    const res = await createOrder(
      {
        user_id: userId,
        items: cart.items.map((item) => ({ item_id: item.id, ordered_quantity: item.qty })),
        name: ime.value,
        surname: prezime.value,
        delivery_address: adresaDostave.value,
        phone_number: brojTelefona.value,
        email_address: email,
        client_request_id: clientRequestId,
        send_sms: Boolean(zelimPotvrdu.value),
      },
      { accessToken },
    )

    const id = res?.id || res?.order?.id
    ui.success(`Narudžba uspješno poslana${id ? ` (ID: ${id})` : ''}.`)

    cart.clear()
    await router.push('/')
  } catch (e) {
    ui.error(`Greška pri slanju narudžbe: ${String(e?.message || e)}`)
  } finally {
    isSubmitting.value = false
  }
}
</script>

<template>
  <div class="mx-auto w-full max-w-6xl px-4 py-8">
    <div class="mb-6 flex items-center justify-between gap-3">
      <div>
        <h1 class="text-2xl font-semibold tracking-tight text-slate-950 sm:text-3xl">
          Podaci za dostavu
        </h1>
        <div class="mt-1 text-sm text-slate-600">
          {{ cart.totalItems }} artik(a)l • {{ formatMoney(cart.totalPrice, 'EUR') }}
        </div>
      </div>
      <RouterLink
        to="/cart"
        class="group inline-flex cursor-pointer items-center gap-2 text-sm font-semibold text-slate-700 transition hover:text-slate-950"
      >
        <span class="transition group-hover:-translate-x-0.5">←</span>
        Nazad na košaricu
      </RouterLink>
    </div>

    <div
      v-if="isEmpty"
      class="rounded-2xl border border-black/10 bg-(--c-surface) p-6 text-slate-700"
    >
      Košarica je prazna.
    </div>

    <div v-else class="grid gap-4 lg:grid-cols-3">
      <div class="lg:col-span-2">
        <div
          v-if="!auth.isAuthenticated"
          class="mb-4 rounded-2xl border border-black/10 bg-(--c-surface) p-5"
        >
          <div class="text-sm font-semibold text-slate-950">Prijava je potrebna</div>
          <div class="mt-1 text-sm text-slate-600">Za slanje narudžbe morate biti prijavljeni.</div>
          <a
            :href="auth.loginRedirectUrl(`${window.location.origin}/auth/callback`)"
            class="mt-4 inline-flex cursor-pointer items-center justify-center rounded-2xl bg-slate-950 px-5 py-3 text-sm font-semibold text-white transition hover:bg-slate-900 active:scale-[0.99]"
          >
            Prijavi se
          </a>
        </div>

        <div class="rounded-2xl border border-black/10 bg-(--c-surface) p-5">
          <div class="text-sm font-semibold text-slate-950">Kontakt podaci</div>

          <div class="mt-4 grid gap-3 sm:grid-cols-2">
            <div>
              <label class="text-xs font-semibold text-slate-600">Ime</label>
              <input
                v-model="ime"
                type="text"
                autocomplete="given-name"
                class="mt-1 w-full rounded-xl border border-black/10 bg-white px-3 py-2 text-sm text-slate-900 outline-none ring-(--fipu_blue) focus:ring-2"
                placeholder="Unesite ime"
              />
            </div>

            <div>
              <label class="text-xs font-semibold text-slate-600">Prezime</label>
              <input
                v-model="prezime"
                type="text"
                autocomplete="family-name"
                class="mt-1 w-full rounded-xl border border-black/10 bg-white px-3 py-2 text-sm text-slate-900 outline-none ring-(--fipu_blue) focus:ring-2"
                placeholder="Unesite prezime"
              />
            </div>

            <div class="sm:col-span-2">
              <label class="text-xs font-semibold text-slate-600">Adresa dostave</label>
              <input
                v-model="adresaDostave"
                type="text"
                autocomplete="shipping street-address"
                class="mt-1 w-full rounded-xl border border-black/10 bg-white px-3 py-2 text-sm text-slate-900 outline-none ring-(--fipu_blue) focus:ring-2"
                placeholder="Ulica i kućni broj, grad"
              />
            </div>

            <div>
              <label class="text-xs font-semibold text-slate-600">Broj telefona</label>
              <input
                v-model="brojTelefona"
                type="tel"
                autocomplete="tel"
                class="mt-1 w-full rounded-xl border border-black/10 bg-white px-3 py-2 text-sm text-slate-900 outline-none ring-(--fipu_blue) focus:ring-2"
                placeholder="+385..."
              />
            </div>

            <div>
              <label class="text-xs font-semibold text-slate-600">Email adresa</label>
              <input
                v-model="emailAdresa"
                type="email"
                autocomplete="email"
                class="mt-1 w-full rounded-xl border border-black/10 bg-white px-3 py-2 text-sm text-slate-900 outline-none ring-(--fipu_blue) focus:ring-2"
                placeholder="ime.prezime@example.com"
              />
            </div>
          </div>

          <div class="mt-5 flex items-center gap-3">
            <button
              type="button"
              :disabled="isSubmitting || !auth.isAuthenticated"
              class="inline-flex cursor-pointer items-center justify-center rounded-2xl bg-(--fipu_blue) px-5 py-3 text-sm font-semibold text-slate-950 transition hover:brightness-105 active:scale-[0.99] disabled:cursor-not-allowed disabled:opacity-60"
              @click="submitOrder"
            >
              {{ isSubmitting ? 'Slanje…' : 'Pošalji narudžbu' }}
            </button>

            <span class="text-xs text-slate-600"
              >Narudžba se šalje prema <code>order-service</code>.</span
            >
          </div>

          <label class="mt-4 flex cursor-pointer items-center gap-3 text-sm text-slate-700">
            <input
              v-model="zelimPotvrdu"
              type="checkbox"
              class="h-4 w-4 rounded border-black/20 text-(--fipu_blue) focus:ring-(--fipu_blue)"
            />
            <span class="font-semibold text-slate-900">Želim potvrdu</span>
            <span class="text-xs text-slate-600">(SMS potvrda narudžbe)</span>
          </label>
        </div>
      </div>

      <div class="rounded-2xl border border-black/10 bg-(--c-surface) p-5">
        <div class="text-sm font-semibold text-slate-950">Sažetak</div>

        <div class="mt-3 space-y-2">
          <div
            v-for="item in cart.items"
            :key="item.id"
            class="flex items-start justify-between gap-3"
          >
            <div class="min-w-0">
              <div class="truncate text-sm font-semibold text-slate-950">{{ item.title }}</div>
              <div class="text-xs text-slate-600">Količina: {{ item.qty }}</div>
            </div>
            <div class="text-sm font-extrabold text-slate-950">
              {{ formatMoney((Number(item.qty) || 0) * (Number(item.price) || 0), item.currency) }}
            </div>
          </div>
        </div>

        <div class="mt-4 flex items-center justify-between text-sm text-slate-700">
          <span>Ukupno za platiti</span>
          <span class="text-lg font-extrabold tracking-tight text-slate-950">
            {{ formatMoney(cart.totalPrice, 'EUR') }}
          </span>
        </div>
      </div>
    </div>
  </div>
</template>
