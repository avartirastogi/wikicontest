/**
 * Vue Router Configuration
 * 
 * This file defines all routes for the WikiContest application.
 * Routes are protected based on authentication requirements.
 */

import { createRouter, createWebHistory } from 'vue-router'
// Import store function - will be used in navigation guard
let storeModule = null

// Import page components
import Home from '../views/Home.vue'
import Login from '../views/Login.vue'
import Register from '../views/Register.vue'
import Contests from '../views/Contests.vue'
import Dashboard from '../views/Dashboard.vue'
import Profile from '../views/Profile.vue'

// Define routes
const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home
  },
  {
    path: '/login',
    name: 'Login',
    component: Login
  },
  {
    path: '/register',
    name: 'Register',
    component: Register
  },
  {
    path: '/contests',
    name: 'Contests',
    component: Contests,
    // Require authentication to view contests
    meta: { requiresAuth: true }
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: Dashboard,
    // Require authentication
    meta: { requiresAuth: true }
  },
  {
    path: '/profile',
    name: 'Profile',
    component: Profile,
    // Require authentication
    meta: { requiresAuth: true }
  },
  {
    // Catch all 404 routes
    path: '/:pathMatch(.*)*',
    redirect: '/'
  }
]

// Create router instance
const router = createRouter({
  history: createWebHistory(),
  routes
})

// Navigation guard to check authentication
router.beforeEach(async (to, from, next) => {
  // Dynamically import store to avoid circular dependencies
  if (!storeModule) {
    storeModule = await import('../store')
  }
  const { useStore } = storeModule
  const store = useStore()
  
  // Check if user is already authenticated in store (from login response)
  // This prevents unnecessary API calls right after login
  const hasUserInStore = store.isAuthenticated && store.currentUser
  
  // Always check authentication status from server (async)
  // This ensures we have the latest auth state from the server
  // But if we already have a user in store, we can use that as a fallback
  let isAuthenticated = false
  try {
    isAuthenticated = await store.checkAuth()
  } catch (error) {
    // If checkAuth fails but we have a user in store (e.g., just logged in),
    // use the store state as fallback
    // This handles cases where cookie might not be set yet after login
    if (hasUserInStore) {
      console.log('Auth check failed but user exists in store, using store state')
      isAuthenticated = true
    } else {
      // No user in store and checkAuth failed - user is not authenticated
      isAuthenticated = false
    }
  }
  
  // Check if route requires authentication
  if (to.meta.requiresAuth && !isAuthenticated) {
    // Redirect to login with return URL
    next({ 
      name: 'Login', 
      query: { redirect: to.fullPath } 
    })
  } else {
    // Allow access to login/register pages even if authenticated
    // The Login component will show a message if user is already logged in
    next()
  }
})

export default router

