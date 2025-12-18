import { computed, ref } from 'vue'
import { defineStore } from 'pinia'

const STORAGE_KEY = 'vue-shop.auth'

function safeJsonParse(value) {
  try {
    return JSON.parse(value)
  } catch {
    return null
  }
}

function base64UrlDecodeToString(base64Url) {
  // base64url -> base64
  let base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/')
  // pad
  while (base64.length % 4 !== 0) base64 += '='
  return decodeURIComponent(
    Array.from(atob(base64))
      .map((c) => `%${c.charCodeAt(0).toString(16).padStart(2, '0')}`)
      .join(''),
  )
}

export const useAuthStore = defineStore('auth', () => {
  const session = ref(null)

  const isAuthenticated = computed(() => {
    const token = session.value?.token
    return Boolean(token?.access_token)
  })

  const user = computed(() => session.value?.userinfo ?? null)

  function getAuthServiceUrl() {
    return import.meta.env.VITE_AUTH_SERVICE_URL
  }

  function initFromStorage() {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (!raw) return
    const parsed = safeJsonParse(raw)
    if (parsed) session.value = parsed
  }

  function persist() {
    if (!session.value) {
      localStorage.removeItem(STORAGE_KEY)
      return
    }
    localStorage.setItem(STORAGE_KEY, JSON.stringify(session.value))
  }

  function setSession(newSession) {
    session.value = newSession
    persist()
  }

  function clearSession() {
    session.value = null
    persist()
  }

  function parseSessionFromHash(hash) {
    const h = (hash || '').startsWith('#') ? hash.slice(1) : hash || ''
    const params = new URLSearchParams(h)
    const encoded = params.get('session')
    if (!encoded) return null

    const json = base64UrlDecodeToString(encoded)
    const parsed = safeJsonParse(json)
    if (!parsed?.token) return null
    return parsed
  }

  function loginRedirectUrl(nextUrl) {
    const base = getAuthServiceUrl()
    const url = new URL('/login', base)
    url.searchParams.set('next', nextUrl)
    return url.toString()
  }

  function logoutRedirectUrl(nextUrl) {
    const base = getAuthServiceUrl()
    const url = new URL('/logout', base)
    if (nextUrl) url.searchParams.set('returnTo', nextUrl)
    return url.toString()
  }

  return {
    session,
    user,
    isAuthenticated,
    initFromStorage,
    setSession,
    clearSession,
    parseSessionFromHash,
    loginRedirectUrl,
    logoutRedirectUrl,
  }
})
