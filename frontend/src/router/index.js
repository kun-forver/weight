import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'Dashboard',
    component: () => import('../views/Dashboard.vue'),
    meta: { requiresAuth: true, requiresUser: true },
  },
  {
    path: '/food',
    name: 'Food',
    component: () => import('../views/Food.vue'),
    meta: { requiresAuth: true, requiresUser: true },
  },
  {
    path: '/weight',
    name: 'Weight',
    component: () => import('../views/Weight.vue'),
    meta: { requiresAuth: true, requiresUser: true },
  },
  {
    path: '/pk',
    name: 'PK',
    component: () => import('../views/PK.vue'),
    meta: { requiresAuth: true, requiresUser: true },
  },
  {
    path: '/profile',
    name: 'Profile',
    component: () => import('../views/Profile.vue'),
    meta: { requiresAuth: true, requiresUser: true },
  },
  {
    path: '/admin',
    name: 'Admin',
    component: () => import('../views/Admin.vue'),
    meta: { requiresAuth: true, requiresAdmin: true },
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/Login.vue'),
    meta: { guestOnly: true },
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('../views/Register.vue'),
    meta: { guestOnly: true },
  },
  {
    path: '/forgot-password',
    name: 'ForgotPassword',
    component: () => import('../views/ForgotPassword.vue'),
    meta: { guestOnly: true },
  },
  {
    path: '/reset-password',
    name: 'ResetPassword',
    component: () => import('../views/ResetPassword.vue'),
    meta: { guestOnly: true },
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/',
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior() {
    return { top: 0 }
  },
})

// Navigation guard
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('access_token')
  const user = JSON.parse(localStorage.getItem('user') || 'null')
  const isAuthenticated = !!token
  const isAdmin = user && user.role === 'admin'

  if (to.meta.requiresAuth && !isAuthenticated) {
    next('/login')
  } else if (to.meta.guestOnly && isAuthenticated) {
    next(isAdmin ? '/admin' : '/')
  } else if (to.meta.requiresAdmin && !isAdmin) {
    next('/')
  } else if (to.meta.requiresUser && isAdmin) {
    next('/admin')
  } else if (to.path === '/' && isAdmin) {
    next('/admin')
  } else {
    next()
  }
})

export default router
