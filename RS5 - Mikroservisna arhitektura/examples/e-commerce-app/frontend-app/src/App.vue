<script setup>
import Header from './components/Header.vue'
import Footer from './components/Footer.vue'
import ToastStack from './components/ToastStack.vue'
</script>

<template>
  <div class="min-h-screen bg-(--c-bg) text-slate-900">
    <Header />
    <main class="flex-1">
      <RouterView />
    </main>
    <Footer />
    <ToastStack />
  </div>
</template>
