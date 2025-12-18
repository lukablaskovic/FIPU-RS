<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, reactive, ref } from 'vue'
import { RouterLink, useRouter } from 'vue-router'

import { getProduct } from '../api/catalog'
import { listOrdersByUserId } from '../api/orders'
import { ensureUser, getUserByEmail, inferConnectionFromAuthUser } from '../api/users'
import InfoModal from '../components/InfoModal.vue'
import { useAuthStore } from '../stores/auth'
import { useUiStore } from '../stores/ui'

const auth = useAuthStore()
const ui = useUiStore()
const router = useRouter()

const isLoading = ref(true)
const userRecord = ref(null)
const orders = ref([])

const accessToken = computed(() => auth.session?.token?.access_token || null)

const trackingModalOpen = ref(false)
const trackingModalText = ref('Praćenje narudžbe je aktivirano.')
const trackingOrderId = ref(null)
const trackingEvents = ref([])
const trackingError = ref('')
const trackingConnected = ref(false)
const trackingDone = ref(false)
const timelineWrapEl = ref(null)
let ws = null

const productsById = reactive({})

function formatDate(iso) {
  const s = String(iso || '')
  if (!s) return ''
  const d = new Date(s)
  if (Number.isNaN(d.getTime())) return s
  return d.toLocaleString('hr-HR')
}

function orderItems(o) {
  return Array.isArray(o?.items) ? o.items : []
}

function orderTotalQty(o) {
  return orderItems(o).reduce((sum, it) => sum + (Number(it?.ordered_quantity) || 0), 0)
}

function productFor(itemId) {
  const id = String(itemId || '')
  return productsById[id] || null
}

function productTitle(itemId) {
  return productFor(itemId)?.title || 'Proizvod'
}

async function prefetchProductsForOrders(orderList) {
  const ids = new Set()
  for (const o of Array.isArray(orderList) ? orderList : []) {
    for (const it of orderItems(o)) {
      if (it?.item_id) ids.add(String(it.item_id))
    }
  }

  const missing = Array.from(ids).filter((id) => !productsById[id])
  if (missing.length === 0) return

  await Promise.all(
    missing.map(async (id) => {
      try {
        const p = await getProduct(id)
        if (p) productsById[id] = p
      } catch {}
    }),
  )
}

function wsUrlForOrder(orderId) {
  const scheme = window.location.protocol === 'https:' ? 'wss' : 'ws'
  return `${scheme}://${window.location.host}/ws/orders/${encodeURIComponent(String(orderId))}`
}

function safeJsonParse(s) {
  try {
    return JSON.parse(String(s))
  } catch {
    return null
  }
}

function eventIcon(step, kind) {
  if (kind === 'done') return '✓'
  if (Number(step) === 1) return '📦'
  if (Number(step) === 2) return '🚚'
  if (Number(step) === 3) return '🛵'
  return '•'
}

function eventDotClasses(idx, ev) {
  const base = 'ring-4 ring-white'
  if (ev?.kind === 'done') return `${base} bg-emerald-500 shadow-[0_0_0_1px_rgba(16,185,129,0.25)]`
  // active = last item while still running
  const isLast = idx === trackingEvents.value.length - 1
  if (!trackingDone.value && isLast)
    return `${base} bg-(--fipu_blue) shadow-[0_0_0_1px_rgba(59,130,246,0.25)]`
  return `${base} bg-slate-300 shadow-[0_0_0_1px_rgba(148,163,184,0.35)]`
}

async function scrollTimelineToBottom() {
  await nextTick()
  const el = timelineWrapEl.value
  if (!el) return
  try {
    el.scrollTo({ top: el.scrollHeight, behavior: 'smooth' })
  } catch {
    el.scrollTop = el.scrollHeight
  }
}

function closeTracking() {
  if (ws) {
    try {
      ws.close()
    } catch {}
    ws = null
  }
  trackingConnected.value = false
  trackingDone.value = false
  trackingError.value = ''
  trackingOrderId.value = null
  trackingEvents.value = []
  trackingModalOpen.value = false
}

async function trackOrder(orderId) {
  if (!orderId) return

  closeTracking()

  try {
    trackingOrderId.value = String(orderId)
    ws = new WebSocket(wsUrlForOrder(orderId))
    ws.onopen = () => {
      trackingConnected.value = true
      trackingDone.value = false
      trackingError.value = ''
      trackingEvents.value = []
      trackingModalText.value = 'Praćenje narudžbe je aktivirano.'
      trackingModalOpen.value = true
    }
    ws.onmessage = (evt) => {
      const raw = evt?.data
      const data = safeJsonParse(raw)
      if (data?.type === 'order_tracking') {
        trackingEvents.value = [
          ...trackingEvents.value,
          {
            step: data?.step ?? null,
            kind: data?.kind ?? 'status',
            text: String(data?.text || ''),
            timestamp: String(data?.timestamp || ''),
          },
        ]
        if (String(data?.kind) === 'done') trackingDone.value = true
        scrollTimelineToBottom()
        return
      }
      // Fallback: show raw message as a simple line.
      trackingEvents.value = [
        ...trackingEvents.value,
        { step: null, kind: 'status', text: String(raw || ''), timestamp: '' },
      ]
      scrollTimelineToBottom()
    }
    ws.onerror = () => {
      trackingError.value = 'Neuspješno spajanje na praćenje narudžbe.'
      trackingConnected.value = false
      ui.error(trackingError.value)
      // Keep modal open to show the error + whatever we received so far.
      trackingModalOpen.value = true
      try {
        ws?.close()
      } catch {}
    }
    ws.onclose = () => {
      ws = null
      trackingConnected.value = false
    }
  } catch (e) {
    ui.error(`Neuspješno spajanje na praćenje narudžbe: ${String(e?.message || e)}`)
  }
}

onBeforeUnmount(() => {
  closeTracking()
})

onMounted(async () => {
  if (!auth.isAuthenticated) {
    ui.error('Za pregled profila morate biti prijavljeni.')
    await router.replace('/')
    return
  }

  isLoading.value = true
  try {
    const email = auth.user?.email ? String(auth.user.email) : ''
    const connection = inferConnectionFromAuthUser(auth.user)

    const ensured = await ensureUser({ email, connection })
    const userId = ensured?.id ? String(ensured.id) : null

    userRecord.value = await getUserByEmail(email)

    if (!userId) throw new Error('user_service_missing_id')

    orders.value = await listOrdersByUserId(userId, { accessToken: accessToken.value })
    await prefetchProductsForOrders(orders.value)
  } catch (e) {
    ui.error(`Greška pri učitavanju profila: ${String(e?.message || e)}`)
  } finally {
    isLoading.value = false
  }
})
</script>

<template>
  <div class="mx-auto w-full max-w-6xl px-4 py-8">
    <div class="mb-6 flex items-center justify-between gap-3">
      <div>
        <h1 class="text-2xl font-semibold tracking-tight text-slate-950 sm:text-3xl">Moj profil</h1>
        <div class="mt-1 text-sm text-slate-600">Pregled korisničkih podataka i narudžbi</div>
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
      v-if="isLoading"
      class="rounded-2xl border border-black/10 bg-(--c-surface) p-6 text-slate-700"
    >
      Učitavanje…
    </div>

    <div v-else class="grid gap-4 lg:grid-cols-3">
      <div class="lg:col-span-1">
        <div class="rounded-2xl border border-black/10 bg-(--c-surface) p-5">
          <div class="text-sm font-semibold text-slate-950">Korisnik</div>

          <div class="mt-4 flex items-center gap-3">
            <img
              v-if="auth.user?.picture"
              :src="auth.user.picture"
              alt=""
              class="h-12 w-12 rounded-full border border-black/10"
              referrerpolicy="no-referrer"
            />
            <div class="min-w-0">
              <div class="truncate text-sm font-semibold text-slate-950">
                {{ auth.user?.name || auth.user?.email || 'Korisnik' }}
              </div>
              <div class="truncate text-xs text-slate-600">{{ auth.user?.email }}</div>
            </div>
          </div>

          <div class="mt-4 space-y-2 text-sm text-slate-700">
            <div class="flex items-center justify-between gap-3">
              <span class="text-slate-600">ID (user-service)</span>
              <span class="font-mono text-xs font-semibold text-slate-950">{{
                userRecord?.id || '—'
              }}</span>
            </div>
            <div class="flex items-center justify-between gap-3">
              <span class="text-slate-600">Email</span>
              <span class="font-semibold text-slate-950">{{
                userRecord?.email || auth.user?.email || '—'
              }}</span>
            </div>
            <div class="flex items-center justify-between gap-3">
              <span class="text-slate-600">Connection</span>
              <span class="font-semibold text-slate-950">{{ userRecord?.connection || '—' }}</span>
            </div>
          </div>
        </div>
      </div>

      <div class="lg:col-span-2">
        <div class="rounded-2xl border border-black/10 bg-(--c-surface) p-5">
          <div class="flex items-center justify-between gap-3">
            <div class="text-sm font-semibold text-slate-950">Moje narudžbe</div>
            <div class="text-xs text-slate-600">{{ orders.length }} ukupno</div>
          </div>

          <div v-if="orders.length === 0" class="mt-4 text-sm text-slate-700">
            Još nema narudžbi.
          </div>

          <div v-else class="mt-4 space-y-3">
            <div
              v-for="o in orders"
              :key="o.id"
              class="rounded-2xl border border-black/10 bg-white p-4"
            >
              <div class="flex items-start justify-between gap-3">
                <div class="min-w-0">
                  <div class="truncate text-sm font-semibold text-slate-950">
                    Narudžba #{{ o.id }}
                  </div>
                  <div class="mt-1 text-xs text-slate-600">{{ formatDate(o.created_at) }}</div>
                </div>
                <div class="text-right text-xs text-slate-600">
                  <div class="font-semibold text-slate-950">{{ orderTotalQty(o) }}×</div>
                  <div class="font-mono">{{ orderItems(o).length }} stavk(i)</div>
                </div>
              </div>

              <div class="mt-4 overflow-hidden rounded-xl border border-black/10 bg-white">
                <div
                  v-for="it in orderItems(o)"
                  :key="String(it?.id || '') + ':' + String(it?.item_id || '')"
                  class="flex items-center gap-3 border-t border-black/10 p-3 first:border-t-0"
                >
                  <div
                    class="h-10 w-10 overflow-hidden rounded-lg border border-black/10 bg-slate-50"
                  >
                    <img
                      v-if="productFor(it.item_id)?.img"
                      :src="productFor(it.item_id).img"
                      :alt="productTitle(it.item_id)"
                      class="h-full w-full object-cover"
                      loading="lazy"
                    />
                  </div>

                  <div class="min-w-0 flex-1">
                    <div class="truncate text-sm font-semibold text-slate-950">
                      {{ productTitle(it.item_id) }}
                    </div>
                    <div class="mt-0.5 truncate font-mono text-xs text-slate-600">
                      {{ it.item_id }}
                    </div>
                  </div>

                  <div class="text-right">
                    <div class="text-xs font-semibold text-slate-500">Qty</div>
                    <div class="text-sm font-extrabold text-slate-950">
                      {{ it.ordered_quantity }}
                    </div>
                  </div>
                </div>
              </div>

              <div class="mt-3 grid gap-2 text-sm text-slate-700 sm:grid-cols-2">
                <div>
                  <div class="text-xs font-semibold text-slate-500">Dostava</div>
                  <div class="font-semibold text-slate-950">{{ o.delivery_address }}</div>
                </div>
                <div>
                  <div class="text-xs font-semibold text-slate-500">Kontakt</div>
                  <div class="font-semibold text-slate-950">{{ o.name }} {{ o.surname }}</div>
                  <div class="text-xs text-slate-600">
                    {{ o.phone_number }} • {{ o.email_address }}
                  </div>
                </div>
              </div>

              <div class="mt-4 flex items-center justify-end">
                <button
                  type="button"
                  class="cursor-pointer rounded-xl border border-black/10 bg-transparent px-4 py-2 text-sm font-semibold text-slate-800 transition hover:border-black/20 hover:bg-black/5 active:scale-[0.99]"
                  @click="trackOrder(o.id)"
                >
                  Prati narudžbu
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <InfoModal
    :open="trackingModalOpen"
    title="Praćenje narudžbe"
    :message="trackingModalText"
    button-text="Zatvori"
    @close="closeTracking"
    max-width-class="max-w-2xl"
  >
    <template #body>
      <div class="flex items-center justify-between gap-3">
        <div class="min-w-0">
          <div class="text-sm font-semibold text-slate-950">
            Narudžba
            <span class="font-mono text-xs text-slate-700">#{{ trackingOrderId || '—' }}</span>
          </div>
          <div class="mt-1 text-xs text-slate-600">
            Live status stream preko WebSocket veze na order-service mikroservisu
          </div>
        </div>

        <div class="flex items-center gap-2">
          <span
            class="inline-flex items-center gap-2 rounded-full border px-3 py-1 text-xs font-semibold"
            :class="
              trackingDone
                ? 'border-emerald-200 bg-emerald-50 text-emerald-900'
                : trackingConnected
                  ? 'border-sky-200 bg-sky-50 text-sky-900'
                  : 'border-slate-200 bg-slate-50 text-slate-700'
            "
          >
            <span
              class="h-2 w-2 rounded-full"
              :class="
                trackingDone
                  ? 'bg-emerald-500'
                  : trackingConnected
                    ? 'bg-sky-500 animate-pulse'
                    : 'bg-slate-300'
              "
            ></span>
            {{ trackingDone ? 'Dostavljeno' : trackingConnected ? 'Povezano' : 'Neaktivno' }}
          </span>
        </div>
      </div>

      <div v-if="trackingError" class="mt-4 rounded-xl border border-rose-200 bg-rose-50 p-3">
        <div class="text-sm font-semibold text-rose-950">Greška</div>
        <div class="mt-1 text-sm text-rose-800">{{ trackingError }}</div>
      </div>

      <div
        ref="timelineWrapEl"
        class="mt-4 max-h-[340px] overflow-auto rounded-2xl border border-black/10 bg-linear-to-b from-slate-50 to-white p-4"
      >
        <div v-if="trackingEvents.length === 0" class="py-10 text-center text-sm text-slate-600">
          Čekam događaje…
        </div>

        <ol v-else class="relative space-y-4">
          <div class="absolute left-[10px] top-0 h-full w-px bg-slate-200"></div>

          <li
            v-for="(ev, idx) in trackingEvents"
            :key="`${idx}-${String(ev?.timestamp || '')}-${String(ev?.text || '')}`"
            class="relative pl-10"
          >
            <div
              class="absolute left-[2px] top-1.5 grid h-5 w-5 place-items-center rounded-full text-[10px] font-extrabold text-white"
              :class="eventDotClasses(idx, ev)"
              :title="String(ev?.timestamp || '')"
            >
              {{ eventIcon(ev?.step, ev?.kind) }}
            </div>

            <div class="rounded-2xl border border-black/10 bg-white px-4 py-3 shadow-sm">
              <div class="flex items-start justify-between gap-3">
                <div class="min-w-0">
                  <div
                    class="text-sm font-semibold"
                    :class="ev?.kind === 'done' ? 'text-emerald-950' : 'text-slate-950'"
                  >
                    {{ ev?.text }}
                  </div>
                  <div class="mt-1 font-mono text-[11px] text-slate-500">
                    {{ ev?.timestamp || '—' }}
                  </div>
                </div>

                <div
                  class="shrink-0 rounded-full border px-2 py-1 text-[11px] font-semibold"
                  :class="
                    ev?.kind === 'done'
                      ? 'border-emerald-200 bg-emerald-50 text-emerald-900'
                      : 'border-slate-200 bg-slate-50 text-slate-700'
                  "
                >
                  {{ ev?.kind === 'done' ? 'DONE' : `STEP ${Number(ev?.step) || '—'}` }}
                </div>
              </div>
            </div>
          </li>
        </ol>
      </div>
    </template>

    <template #footer>
      <div class="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
        <div class="text-xs text-slate-600">
          Savjet: klikni “Prati narudžbu” ponovno za restart simulacije.
        </div>
        <button
          type="button"
          class="inline-flex cursor-pointer items-center justify-center rounded-xl bg-(--fipu_blue) px-5 py-2.5 text-sm font-semibold text-white transition hover:bg-(--fipu_blue)/80 active:scale-[0.99]"
          @click="closeTracking"
        >
          Zatvori
        </button>
      </div>
    </template>
  </InfoModal>
</template>
