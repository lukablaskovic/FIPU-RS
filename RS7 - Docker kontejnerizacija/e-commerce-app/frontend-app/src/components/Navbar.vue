<script setup>
import { RouterLink, useRoute } from 'vue-router'
import { computed, ref } from 'vue'
import { useAuthStore } from '../stores/auth'
import { useCartStore } from '../stores/cart.js'
import LoginModal from './LoginModal.vue'

const auth = useAuthStore()
const cart = useCartStore()
const loginOpen = ref(false)
const route = useRoute()

const callbackUrl = computed(() => `${window.location.origin}/auth/callback`)
const loginUrl = computed(() => auth.loginRedirectUrl(callbackUrl.value))
const cartCount = computed(() => cart.totalItems)

const isShopActive = computed(() => route.path === '/')
const isCartActive = computed(() => route.path === '/cart')
const isProfileActive = computed(() => route.path === '/profile')

const navLinkBase =
  'rounded-md px-3 py-2 font-semibold transition hover:bg-black/5 hover:text-slate-950 active:scale-[0.99]'
const navLinkInactive = 'text-slate-700'
const navLinkActive = 'bg-black/5 text-slate-950'

function openLogin() {
  loginOpen.value = true
}

function closeLogin() {
  loginOpen.value = false
}

function logout() {
  auth.clearSession()
}
</script>

<template>
  <div class="flex items-center gap-3">
    <nav class="flex items-center gap-1 text-sm">
      <RouterLink to="/" :class="[navLinkBase, isShopActive ? navLinkActive : navLinkInactive]"
        >Shop</RouterLink
      >
      <RouterLink
        to="/cart"
        :class="['relative', navLinkBase, isCartActive ? navLinkActive : navLinkInactive]"
      >
        Košarica
        <span
          v-if="cartCount > 0"
          class="ml-2 inline-flex min-w-5 items-center justify-center rounded-full bg-(--fipu_blue) px-1.5 py-0.5 text-[11px] font-extrabold leading-none text-slate-950"
        >
          {{ cartCount }}
        </span>
      </RouterLink>
    </nav>

    <div class="h-6 w-px bg-black/10"></div>

    <button
      v-if="!auth.isAuthenticated"
      type="button"
      class="rounded-md bg-slate-950 px-3 py-2 text-sm font-semibold text-white transition hover:bg-slate-900 active:scale-[0.99] cursor-pointer"
      @click="openLogin"
    >
      Prijava
    </button>

    <div v-else class="flex items-center gap-2">
      <RouterLink
        to="/profile"
        :class="[
          'flex items-center gap-2 rounded-md px-2 py-1 transition hover:bg-black/5',
          isProfileActive ? 'bg-black/5' : '',
        ]"
      >
        <img
          v-if="auth.user?.picture"
          :src="auth.user.picture"
          alt=""
          class="h-8 w-8 rounded-full border border-black/10"
          referrerpolicy="no-referrer"
        />
        <div class="hidden text-right sm:block">
          <div class="text-xs font-semibold text-slate-900">
            {{ auth.user?.email || auth.user?.name || 'Profil' }}
          </div>
        </div>
      </RouterLink>
      <button
        type="button"
        class="rounded-md px-3 py-2 text-sm font-semibold text-slate-700 transition hover:bg-black/5 hover:text-slate-950 active:scale-[0.99] cursor-pointer"
        @click="logout"
      >
        Odjava
      </button>
    </div>

    <LoginModal :open="loginOpen" :login-url="loginUrl" @close="closeLogin" />
  </div>
</template>
