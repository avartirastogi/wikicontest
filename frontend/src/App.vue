<template>
  <div id="app">
    <!-- Navigation Bar -->
    <nav class="navbar navbar-expand-lg navbar-light bg-light">
      <div class="container">
        <router-link class="navbar-brand" to="/">
          <i class="fas fa-trophy me-2"></i>WikiContest
        </router-link>
        <button 
          class="navbar-toggler" 
          type="button" 
          data-bs-toggle="collapse" 
          data-bs-target="#navbarNav"
        >
          <span class="navbar-toggler-icon"></span>
        </button>
        <div class="collapse navbar-collapse" id="navbarNav">
          <ul class="navbar-nav me-auto">
            <li class="nav-item">
              <router-link class="nav-link" to="/">Home</router-link>
            </li>
            <li class="nav-item" v-if="isAuthenticated">
              <router-link class="nav-link" to="/contests">Contests</router-link>
            </li>
            <li class="nav-item" v-if="isAuthenticated">
              <router-link class="nav-link" to="/dashboard">Dashboard</router-link>
            </li>
          </ul>
          <ul class="navbar-nav">
            <!-- Theme Toggle Button - Always visible -->
            <li class="nav-item me-2">
              <button 
                class="btn btn-outline-secondary theme-toggle" 
                type="button"
                @click="toggleTheme"
                :title="theme === 'light' ? 'Switch to dark mode' : 'Switch to light mode'"
              >
                <i :class="theme === 'light' ? 'fas fa-moon' : 'fas fa-sun'"></i>
              </button>
            </li>
            <!-- Show login/register buttons when not authenticated -->
            <template v-if="!isAuthenticated">
              <li class="nav-item">
                <router-link class="btn btn-outline-primary me-2" to="/login" style="text-decoration: none; display: inline-block;">Login</router-link>
              </li>
              <li class="nav-item">
                <router-link class="btn btn-primary" to="/register" style="text-decoration: none; display: inline-block;">Register</router-link>
              </li>
            </template>
            <!-- Show user menu when authenticated -->
            <template v-else>
              <li class="nav-item">
                <div class="dropdown">
                  <button 
                    class="btn btn-outline-secondary dropdown-toggle" 
                    type="button" 
                    id="userDropdown" 
                    data-bs-toggle="dropdown"
                  >
                    <i class="fas fa-user me-1"></i>{{ currentUser?.username || 'User' }}
                  </button>
                  <ul class="dropdown-menu dropdown-menu-end">
                    <li>
                      <router-link class="dropdown-item" to="/profile">
                        <i class="fas fa-user me-2"></i>Profile
                      </router-link>
                    </li>
                    <li>
                      <router-link class="dropdown-item" to="/dashboard">
                        <i class="fas fa-tachometer-alt me-2"></i>Dashboard
                      </router-link>
                    </li>
                    <li><hr class="dropdown-divider"></li>
                    <li>
                      <a class="dropdown-item text-danger" href="#" @click.prevent="handleLogout">
                        <i class="fas fa-sign-out-alt me-2"></i>Logout
                      </a>
                    </li>
                  </ul>
                </div>
              </li>
            </template>
          </ul>
        </div>
      </div>
    </nav>

    <!-- Alert Container -->
    <AlertContainer />

    <!-- Main Content Area -->
    <main class="container-fluid">
      <router-view />
    </main>
  </div>
</template>

<script>
import { computed, onMounted } from 'vue'
import { useStore } from './store'
import { useRouter } from 'vue-router'
import AlertContainer from './components/AlertContainer.vue'

export default {
  name: 'App',
  components: {
    AlertContainer
  },
  setup() {
    const store = useStore()
    const router = useRouter()

    // Use store's computed properties directly - they are already reactive
    // Don't wrap them in another computed() - that breaks reactivity
    const isAuthenticated = store.isAuthenticated
    const currentUser = store.currentUser
    const theme = store.theme

    // Toggle theme function
    const toggleTheme = () => {
      store.toggleTheme()
    }

    // Check authentication on app mount
    // This runs after initial render, so buttons will show immediately
    onMounted(async () => {
      // Apply theme on mount (in case store hasn't initialized it yet)
      if (typeof document !== 'undefined') {
        const savedTheme = localStorage.getItem('theme') || 'light'
        store.setTheme(savedTheme)
      }
      
      try {
        // Force a fresh auth check - this will clear state if not authenticated
        await store.checkAuth()
      } catch (error) {
        // Silently fail - user is not authenticated
        // This is normal for users who aren't logged in
        // checkAuth already clears state on error
        console.log('Auth check completed - user not logged in')
      }
    })

    // Logout handler
    const handleLogout = async () => {
      try {
        // Logout clears state immediately
        const result = await store.logout()
        
        // Small delay to ensure cookies are cleared on backend
        await new Promise(resolve => setTimeout(resolve, 200))
        
        // Force a fresh auth check to verify logout worked
        // This ensures state is definitely cleared
        await store.checkAuth()
        
        // Show success message
        const { showAlert } = await import('./utils/alerts')
        showAlert('Logged out successfully', 'success')
        
        // Redirect to home - state is already cleared
        router.push('/')
      } catch (error) {
        // Even if logout fails, ensure state is cleared
        // Force checkAuth to clear any stale state
        await store.checkAuth()
        
        const { showAlert } = await import('./utils/alerts')
        showAlert('Logged out (session cleared)', 'info')
        router.push('/')
      }
    }

    return {
      isAuthenticated,
      currentUser,
      theme,
      toggleTheme,
      handleLogout
    }
  }
}
</script>

<style>
/* Wikipedia/Wikimedia Brand Colors:
 * Sea Blue: #006699 (primary)
 * Illuminating Emerald: #339966 (success)
 * Crimson Red: #990000 (danger/warning)
 * Outer Space: #484848 (text/dark)
 */

:root {
  --bs-primary: #006699;
  --bs-primary-rgb: 0, 102, 153;
}

/* Navbar styling with Wikipedia colors - subtle border */
.navbar {
  background-color: var(--wiki-navbar-bg) !important;
  border-bottom: 1px solid var(--wiki-border);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
  transition: background-color 0.3s ease, border-color 0.3s ease;
}

[data-theme="dark"] .navbar {
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.5);
  border-bottom-width: 1px;
  border-bottom-style: solid;
}

.navbar-brand {
  font-weight: bold;
  color: var(--wiki-dark) !important;
  font-size: 1.5rem;
  transition: color 0.2s ease;
}

.navbar-brand:hover {
  color: var(--wiki-primary) !important;
}

.navbar-brand i {
  color: #006699;
}

.nav-link {
  color: var(--wiki-dark) !important;
  font-weight: 500;
  transition: color 0.2s ease, background-color 0.2s ease;
  padding: 0.5rem 1rem !important;
}

.nav-link:hover {
  color: var(--wiki-primary) !important;
  background-color: var(--wiki-hover-bg);
  border-radius: 0.25rem;
}

/* Theme toggle button */
.theme-toggle {
  min-width: 40px;
  padding: 0.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
}

.theme-toggle i {
  font-size: 1.1rem;
}

/* Primary button - Wikipedia blue */
.btn-primary {
  background: var(--wiki-primary);
  border: none;
  color: white;
  font-weight: 500;
  transition: all 0.2s ease;
}

.btn-primary:hover {
  background: var(--wiki-primary-hover);
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(0, 102, 153, 0.3);
}

.btn-primary:active {
  transform: translateY(0);
}

/* CTA button - Wikipedia green */
.btn-cta {
  background: #339966;
  border: none;
  color: white;
  font-weight: 500;
  transition: all 0.2s ease;
}

.btn-cta:hover {
  background: #2d8555;
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(51, 153, 102, 0.3);
  color: white;
}

/* Text colors */
.text-primary {
  color: var(--wiki-primary) !important;
}

.text-success {
  color: var(--wiki-success) !important;
}

.text-warning {
  color: var(--wiki-danger) !important;
}

/* Badge colors */
.badge.bg-primary {
  background-color: var(--wiki-primary) !important;
  color: white;
}

.badge.bg-success {
  background-color: var(--wiki-success) !important;
  color: white;
}

.badge.bg-warning {
  background-color: var(--wiki-danger) !important;
  color: white;
}

.badge.bg-danger {
  background-color: var(--wiki-danger) !important;
  color: white;
}

.badge.bg-info {
  background-color: var(--wiki-primary) !important;
  color: white;
}

/* Card styling */
.card {
  box-shadow: 0 2px 8px rgba(72, 72, 72, 0.1);
  border: 1px solid var(--wiki-border);
  background-color: var(--wiki-card-bg);
  transition: all 0.3s ease;
}

[data-theme="dark"] .card {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
}

.card:hover {
  transform: translateY(-3px);
  box-shadow: 0 6px 16px rgba(72, 72, 72, 0.15);
}

[data-theme="dark"] .card:hover {
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.5);
}

.card-title {
  color: var(--wiki-dark);
  font-weight: 600;
}

/* Hero section */
.hero-section {
  background: linear-gradient(135deg, #006699 0%, #339966 100%);
  color: white;
  padding: 100px 0;
  position: relative;
  overflow: hidden;
}

.hero-section::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: url('data:image/svg+xml,<svg width="100" height="100" xmlns="http://www.w3.org/2000/svg"><circle cx="50" cy="50" r="2" fill="rgba(255,255,255,0.1)"/></svg>');
  opacity: 0.3;
}

.hero-section .container {
  position: relative;
  z-index: 1;
}

.hero-section h1 {
  font-weight: 700;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.2);
}

.hero-section .lead {
  font-size: 1.25rem;
  opacity: 0.95;
}

/* Dropdown menu styling */
.dropdown-menu {
  min-width: 200px;
  border: 1px solid var(--wiki-border);
  background-color: var(--wiki-card-bg);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  border-radius: 0.5rem;
  padding: 0.5rem 0;
  transition: background-color 0.3s ease, border-color 0.3s ease;
}

[data-theme="dark"] .dropdown-menu {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.5);
}

.dropdown-item {
  padding: 0.5rem 1.5rem;
  transition: all 0.2s ease;
  color: var(--wiki-dark);
}

.dropdown-item:hover {
  background-color: var(--wiki-hover-bg);
  color: var(--wiki-primary);
}

.dropdown-item.text-danger {
  color: var(--wiki-danger) !important;
}

.dropdown-item.text-danger:hover {
  background-color: rgba(153, 0, 0, 0.1);
  color: var(--wiki-danger) !important;
}

[data-theme="dark"] .dropdown-item.text-danger:hover {
  background-color: rgba(204, 102, 102, 0.2);
}

.dropdown-item i {
  width: 20px;
  text-align: center;
}

.dropdown-divider {
  margin: 0.5rem 0;
  border-color: var(--wiki-border);
}

/* Spinner colors */
.spinner-border.text-primary {
  color: var(--wiki-primary) !important;
}

/* List group styling */
.list-group-item {
  border-color: var(--wiki-border);
  background-color: var(--wiki-card-bg);
  color: var(--wiki-text);
  transition: all 0.2s ease;
}

.list-group-item:hover {
  background-color: var(--wiki-hover-bg);
  border-left: 3px solid var(--wiki-primary);
  padding-left: calc(1rem - 3px);
}

.list-group-item-action {
  color: var(--wiki-dark);
}

.list-group-item-action:hover {
  color: var(--wiki-primary);
}

/* Mobile responsive improvements */
@media (max-width: 768px) {
  /* Navbar improvements */
  .navbar-brand {
    font-size: 1.25rem;
  }
  
  .navbar-nav {
    margin-top: 1rem;
  }
  
  .nav-link {
    padding: 0.75rem 1rem !important;
  }
  
  /* Better button spacing in navbar */
  .navbar-nav .btn {
    margin: 0.25rem 0;
    width: 100%;
    text-align: center;
  }
  
  /* Dropdown menu full width on mobile */
  .dropdown-menu {
    width: 100%;
    margin-top: 0.5rem;
  }
  
  /* Better container padding */
  .container-fluid {
    padding-left: 0.5rem;
    padding-right: 0.5rem;
  }
}

@media (max-width: 576px) {
  .navbar-brand {
    font-size: 1.1rem;
  }
  
  .navbar-nav .btn {
    font-size: 0.9rem;
    padding: 0.5rem 0.75rem;
  }
}
</style>
