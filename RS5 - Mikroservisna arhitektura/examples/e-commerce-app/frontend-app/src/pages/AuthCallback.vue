<script setup>
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const auth = useAuthStore()

onMounted(async () => {
  const session = auth.parseSessionFromHash(window.location.hash)

  if (session) {
    auth.setSession(session)
    window.history.replaceState({}, document.title, window.location.pathname)
  }

  await router.replace('/')
})
</script>

<template>
  <div class="mx-auto max-w-6xl px-4 py-10">
    <div class="rounded-2xl border border-black/10 bg-(--c-surface) p-6">
      <div class="text-sm font-semibold text-slate-950">Signing you in…</div>
      <div class="mt-1 text-sm text-slate-600">Processing login response from auth-service.</div>
    </div>
  </div>
</template>
