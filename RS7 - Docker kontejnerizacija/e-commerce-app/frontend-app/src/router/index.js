import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'products',
      component: () => import('../pages/ProductGallery.vue'),
    },
    {
      path: '/cart',
      name: 'cart',
      component: () => import('../pages/Cart.vue'),
    },
    {
      path: '/checkout',
      name: 'checkout',
      component: () => import('../pages/Checkout.vue'),
    },
    {
      path: '/profile',
      name: 'profile',
      component: () => import('../pages/Profile.vue'),
    },
    {
      path: '/auth/callback',
      name: 'auth-callback',
      component: () => import('../pages/AuthCallback.vue'),
    },
    {
      path: '/product/:id',
      name: 'product',
      component: () => import('../pages/SingleProduct.vue'),
    },
  ],
  scrollBehavior() {
    return { top: 0 }
  },
})

export default router
