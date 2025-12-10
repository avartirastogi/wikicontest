/**
 * Vue Router Configuration
 *
 * This file defines all routes for the WikiContest application.
 * Routes are protected based on authentication requirements.
 */

import { createRouter, createWebHistory } from 'vue-router'

// Import page components
import Home from '../views/Home.vue'
import Contests from '../views/Contests.vue'
import ContestView from '../views/ContestView.vue'
import Dashboard from '../views/Dashboard.vue'
import Profile from '../views/Profile.vue'
// Import store function - will be used in navigation guard
let storeModule = null

// Define routes
const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home
  },
  {
    path: '/contests',
    name: 'Contests',
    component: Contests,
    // Require authentication to view contests
    meta: { requiresAuth: true }
  },
  {
    path: '/contest/:name',
    name: 'ContestView',
    component: ContestView,
    // Require authentication to view contest details
    // name parameter is the slugified contest name (e.g., "price-sanford")
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
    // Redirect directly to MediaWiki OAuth authentication
    // Get API base URL for OAuth redirect
    const getApiBaseUrl = () => {
      // In development, use full URL to Flask backend
      if (import.meta.env.DEV) {
        return 'http://localhost:5000/api'
      }
      // In production, use relative URL
      return '/api'
    }
    
    // Store the intended destination for after OAuth
    if (to.fullPath !== '/') {
      sessionStorage.setItem('oauth_redirect', to.fullPath)
    }
    
    // Redirect to OAuth login endpoint
    window.location.href = `${getApiBaseUrl()}/user/oauth/login`
    return // Stop navigation
  } else {
    // Allow access to public pages
    next()
  }
})

export default router

