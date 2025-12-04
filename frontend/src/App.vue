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

/* ================================
   WIKIMEDIA UI UPGRADE – PREMIUM
   ================================ */

/* --- Brand Colors --- */
:root {
  --crimson: #990000;
  --emerald: #339966;
  --seablue: #006699;
  --outerspace: #484848;

  /* UI Shades */
  --nav-bg-light: #ffffff;
  --nav-bg-dark: #1b1b1b;
  --hover-bg-light: rgba(0,0,0,0.05);
  --hover-bg-dark: rgba(255,255,255,0.1);

  --text-dark: #2b2b2b;
  --text-light: #f1f1f1;

  --border-light: rgba(0,0,0,0.12);
  --border-dark: rgba(255,255,255,0.15);

  --transition: 0.25s ease;
}

/* Typography Upgrade */
body, button, input {
  font-family: "Inter", "Segoe UI", system-ui, sans-serif;
  letter-spacing: 0.2px;
}

/* =======================
   NAVBAR (Enhanced UI)
   ======================= */
.navbar {
  background: var(--nav-bg-light) !important;
  border-bottom: 1px solid var(--border-light);
  backdrop-filter: blur(12px);
  padding: 0.6rem 0;
  transition: background var(--transition), border var(--transition);
  z-index: 1000 !important;
}

[data-theme="dark"] .navbar {
  background: rgba(20,20,20,0.85) !important;
  border-bottom: 1px solid var(--border-dark);
}

/* Brand logo */
.navbar-brand {
  font-size: 1.6rem;
  font-weight: 700;
  color: var(--seablue) !important;
  letter-spacing: -0.5px;
  display: flex;
  align-items: center;
  gap: 6px;
  transition: var(--transition);
}

.navbar-brand:hover {
  color: var(--emerald) !important;
  transform: translateY(-1px);
}

/* Navigation links */
.nav-link {
  font-weight: 600;
  color: var(--outerspace) !important;
  padding: 0.6rem 1rem !important;
  border-radius: 6px;
  transition: var(--transition);
}

[data-theme="dark"] .nav-link {
  color: #e6e6e6 !important;
}

.nav-link:hover {
  background: var(--hover-bg-light);
  color: var(--seablue) !important;
}

[data-theme="dark"] .nav-link:hover {
  background: var(--hover-bg-dark);
}

/* =======================
   Buttons Upgrade
   ======================= */
.btn-primary {
  background: var(--seablue);
  border: none;
  font-weight: 600;
  transition: var(--transition);
}

.btn-primary:hover {
  background: #00527a;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 102, 153, 0.35);
}

.btn-outline-primary {
  border-color: var(--seablue);
  color: var(--seablue);
  font-weight: 600;
}

.btn-outline-primary:hover {
  background: var(--seablue);
  color: #fff;
}

/* Theme Toggle Button */
.theme-toggle {
  border-radius: 10px;
  transition: var(--transition);
}

.theme-toggle:hover {
  background: var(--hover-bg-light);
}

[data-theme="dark"] .theme-toggle:hover {
  background: var(--hover-bg-dark);
}

/* =======================
   Dropdown Menu (Modern)
   ======================= */
.dropdown-menu {
  border-radius: 12px;
  padding: 0.4rem 0;
  border: 1px solid var(--border-light);
  box-shadow: 0 8px 25px rgba(0,0,0,0.15);
  background: #fff;
  z-index: 2000 !important;
}

[data-theme="dark"] .dropdown-menu {
  background: #1d1d1d;
  border: 1px solid var(--border-dark);
}

.dropdown-item {
  padding: 0.65rem 1.3rem;
  font-weight: 500;
  transition: var(--transition);
}

.dropdown-item:hover {
  background: var(--hover-bg-light);
  color: var(--seablue);
}

[data-theme="dark"] .dropdown-item:hover {
  background: var(--hover-bg-dark);
}

/* Logout item special */
.dropdown-item.text-danger:hover {
  background: rgba(153,0,0,0.08);
}

/* =======================
   Global Card UI Upgrade
   ======================= */
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

/* =======================
   Responsive Enhancements
   ======================= */
@media (max-width: 768px) {
  .navbar-brand {
    font-size: 1.3rem;
  }

  .dropdown-menu {
    width: 100%;
  }
}
</style>
