<template>
  <div class="profile-container">

    <h2 class="page-title">Your Profile</h2>

    <transition name="fade-scale">

      <div v-if="currentUser" class="profile-card">

        <div class="profile-header">
          <div class="avatar">
            <i class="fas fa-user"></i>
          </div>
          <div class="username-with-badge">
            <h3>{{ displayUsername }}</h3>
            <span
              class="role-badge"
              :class="userRole === 'superadmin' ? 'badge-superadmin' : 'badge-user'"
            >
              {{ formattedRole }}
            </span>
          </div>
          <p class="tagline">Wikimedia Contributor</p>
        </div>

        <div class="info-section">
          <div class="info-item">
            <i class="fas fa-user-circle"></i>
            <span><strong>Username</strong> : {{ displayUsername }}</span>
          </div>

          <div class="info-item">
            <i class="fas fa-envelope"></i>
            <span><strong>Email</strong> : {{ displayEmail }}</span>
          </div>

          <div class="info-item">
            <i class="fas fa-id-card"></i>
            <span><strong>User ID</strong> : {{ displayUserId }}</span>
          </div>

          <div class="info-item">
            <i class="fas fa-shield-alt"></i>
            <span>
              <strong>Role</strong> :
              <span
                class="role-text"
                :class="userRole === 'superadmin' ? 'role-superadmin' : 'role-user'"
              >
                {{ formattedRole }}
              </span>
            </span>
          </div>
        </div>

      </div>

      <div v-else class="alert-message">
        <i class="fas fa-exclamation-triangle"></i>
        Please login to view your profile.
      </div>

    </transition>

  </div>
</template>


<script>
import { computed, onMounted, watch, onActivated } from 'vue'
import { useRoute } from 'vue-router'
import { useStore } from '../store'

export default {
  name: 'Profile',
  setup() {
    const store = useStore()
    const route = useRoute()
    const currentUser = computed(() => store.currentUser)

    // Function to refresh user data from backend
    const refreshUserData = async () => {
      console.log('🔄 Refreshing user data...')
      try {
        // Force a fresh auth check to get latest role from database
        await store.checkAuth()
        // Wait for reactive state to update
        await new Promise(resolve => setTimeout(resolve, 300))

        // Log what we got
        console.log('🔄 After refresh - currentUser:', JSON.stringify(currentUser.value, null, 2))
        console.log('🔄 After refresh - role:', currentUser.value?.role)
      } catch (error) {
        console.error('🔄 Error refreshing user data:', error)
      }
    }

    // Refresh user data when profile page loads to ensure we have latest role info
    onMounted(async () => {
      console.log('📄 Profile page mounted')
      console.log('📄 Current user before refresh:', JSON.stringify(currentUser.value, null, 2))
      console.log('📄 Current user role before refresh:', currentUser.value?.role)

      // Refresh user data
      await refreshUserData()

      // Debug: log current user to see what data we have
      console.log('📄 Profile mounted - currentUser after refresh:', JSON.stringify(currentUser.value, null, 2))
      console.log('📄 Profile mounted - currentUser.role after refresh:', currentUser.value?.role)
      console.log('📄 Store currentUser:', JSON.stringify(store.currentUser, null, 2))
      console.log('📄 Store state.currentUser:', JSON.stringify(store.state?.currentUser, null, 2))

      // Final verification - log the exact role value
      if (currentUser.value) {
        console.log('📄 FINAL ROLE CHECK:')
        console.log('  - currentUser.value.role:', currentUser.value.role)
        console.log('  - typeof:', typeof currentUser.value.role)
        console.log('  - String value:', String(currentUser.value.role))
        console.log('  - userRole computed:', userRole.value)
        console.log('  - formattedRole computed:', formattedRole.value)
      }
    })

    // Also refresh when route is activated (for keep-alive scenarios)
    onActivated(async () => {
      console.log('📄 Profile page activated - refreshing data')
      await refreshUserData()
    })

    // Watch for route changes to refresh data when navigating to profile
    watch(() => route.path, async (newPath) => {
      if (newPath === '/profile') {
        console.log('📄 Route changed to profile - refreshing data')
        await refreshUserData()
      }
    }, { immediate: false })

    // Watch currentUser changes to log when role updates
    watch(() => currentUser.value?.role, (newRole, oldRole) => {
      console.log('📄 Role changed:', { oldRole, newRole })
      if (currentUser.value?.username === 'Adityakumar0545' && newRole !== 'superadmin') {
        console.error(' [ERROR] Adityakumar0545 role is not superadmin! Current:', newRole)
      }
    })

    // Watch store.state.currentUser.role directly for immediate updates
    watch(() => store.state?.currentUser?.role, (newRole) => {
      console.log('📄 Store state role changed to:', newRole)
      if (newRole === 'superadmin') {
        console.log('Superadmin role detected in store state!')
      }
    }, { immediate: true })


    // Format role text for display (capitalize first letter)
    // CRITICAL: Check multiple sources to ensure we get the latest role
    const formattedRole = computed(() => {
      // Try to get role from multiple sources
      const role = currentUser.value?.role ||
                   store.currentUser?.role ||
                   store.state?.currentUser?.role ||
                   'user'

      if (!role || role === 'N/A') {
        return 'User'
      }

      // Normalize and capitalize first letter
      const normalizedRole = String(role).toLowerCase().trim()
      return normalizedRole.charAt(0).toUpperCase() + normalizedRole.slice(1)
    })

    // Get role for badge class styling
    // CRITICAL: Check multiple sources to ensure we get the latest role
    const userRole = computed(() => {
      // Try to get role from multiple sources
      const role = currentUser.value?.role ||
                   store.currentUser?.role ||
                   store.state?.currentUser?.role ||
                   'user'

      if (!role || role === 'N/A') {
        return 'user'
      }

      return String(role).toLowerCase().trim()
    })

    // Computed properties for displaying user info with fallbacks
    const displayUsername = computed(() => {
      return currentUser.value?.username ||
             store.currentUser?.username ||
             store.state?.currentUser?.username ||
             'N/A'
    })

    const displayEmail = computed(() => {
      return currentUser.value?.email ||
             store.currentUser?.email ||
             store.state?.currentUser?.email ||
             'N/A'
    })

    const displayUserId = computed(() => {
      return currentUser.value?.id ||
             store.currentUser?.id ||
             store.state?.currentUser?.id ||
             'N/A'
    })

    return {
      currentUser,
      formattedRole,
      userRole,
      displayUsername,
      displayEmail,
      displayUserId
    }
  }
}
</script>

<style scoped>
/* ===============================
   Professional Profile Page UI
   =============================== */

.profile-container {
  max-width: 700px;
  margin: auto;
  padding: 3rem 1rem;
}

/* ===============================
   Page Title - Professional
   =============================== */
.page-title {
  text-align: center;
  font-size: 2rem;
  font-weight: 600;
  letter-spacing: -0.02em;
  margin-bottom: 2rem;
  color: var(--wiki-dark);
  border-bottom: 2px solid var(--wiki-primary);
  padding-bottom: 0.5rem;
}

/* ===============================
   Profile Card - Professional
   =============================== */
.profile-card {
  background-color: var(--wiki-card-bg);
  border-radius: 4px;
  padding: 2rem;
  border: 1px solid var(--wiki-border);
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.04);
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
}

[data-theme="dark"] .profile-card {
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
}

/* ===============================
   Profile Header with Avatar
   =============================== */
.profile-header {
  text-align: center;
  margin-bottom: 2.2rem;
}

.avatar {
  width: 80px;
  height: 80px;
  margin: auto;
  border-radius: 50%;
  background: var(--wiki-primary);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 2rem;
  margin-bottom: 1rem;
  box-shadow: 0 2px 4px rgba(0, 102, 153, 0.2);
  transition: background-color 0.2s ease;
}

.avatar:hover {
  background: var(--wiki-primary-hover);
}

.username-with-badge {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.profile-header h3 {
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--wiki-dark);
  margin-bottom: 0.25rem;
}

/* ===============================
   Role Badge Styles
   =============================== */
.role-badge {
  display: inline-block;
  padding: 0.35rem 0.75rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  transition: all 0.2s ease;
}

/* User role badge - blue color for visibility */
.badge-user {
  background-color: rgba(0, 123, 255, 0.15);
  color: #007bff;
  border: 1px solid rgba(0, 123, 255, 0.4);
  font-weight: 600;
}

[data-theme="dark"] .badge-user {
  background-color: rgba(0, 123, 255, 0.2);
  color: #4da3ff;
  border-color: rgba(0, 123, 255, 0.5);
}

/* Superadmin role badge - red color for visibility */
.badge-superadmin {
  background-color: rgba(220, 53, 69, 0.15);
  color: #dc3545;
  border: 1px solid rgba(220, 53, 69, 0.4);
  font-weight: 700;
}

[data-theme="dark"] .badge-superadmin {
  background-color: rgba(220, 53, 69, 0.25);
  color: #ff6b7a;
  border-color: rgba(220, 53, 69, 0.5);
}

.tagline {
  font-size: 0.95rem;
  color: var(--wiki-text-muted);
  margin-top: 0.25rem;
}

/* ===============================
   User Info Section
   =============================== */
.info-section {
  margin-top: 1rem;
}

.info-item {
  display: flex;
  align-items: center;
  padding: 1rem;
  border-radius: 4px;
  margin-bottom: 0.75rem;
  background-color: var(--wiki-light-bg);
  border: 1px solid var(--wiki-border);
  transition: all 0.2s ease;
}

[data-theme="dark"] .info-item {
  background-color: rgba(93, 184, 230, 0.05);
  border-color: var(--wiki-border);
}

.info-item i {
  font-size: 1.25rem;
  margin-right: 1rem;
  color: var(--wiki-primary);
  transition: color 0.2s ease;
}

.info-item:hover {
  background-color: var(--wiki-hover-bg);
  border-color: var(--wiki-primary);
}

.info-item:hover i {
  color: var(--wiki-primary-hover);
}

.info-item strong {
  color: var(--wiki-dark);
  font-size: 0.95rem;
  font-weight: 600;
}

/* Role text styling in info section */
.role-text {
  font-weight: 600;
  padding: 0.2rem 0.5rem;
  border-radius: 4px;
  display: inline-block;
}

.role-user {
  color: #007bff;
  background-color: rgba(0, 123, 255, 0.15);
  font-weight: 600;
}

[data-theme="dark"] .role-user {
  color: #4da3ff;
  background-color: rgba(0, 123, 255, 0.2);
}

.role-superadmin {
  color: #dc3545;
  background-color: rgba(220, 53, 69, 0.15);
  font-weight: 700;
}

[data-theme="dark"] .role-superadmin {
  color: #ff6b7a;
  background-color: rgba(220, 53, 69, 0.25);
}

/* ===============================
   Alert Message - Professional
   =============================== */
.alert-message {
  background-color: rgba(153, 0, 0, 0.1);
  color: var(--wiki-danger);
  padding: 1.25rem;
  border-radius: 4px;
  border-left: 4px solid var(--wiki-danger);
  border: 1px solid var(--wiki-danger);
  text-align: center;
  font-size: 1rem;
  font-weight: 500;
}

[data-theme="dark"] .alert-message {
  background-color: rgba(230, 128, 128, 0.15);
}

.alert-message i {
  margin-right: 8px;
  font-size: 1.1rem;
}

/* ===============================
   Transitions - Subtle
   =============================== */
.fade-scale-enter-active {
  transition: opacity 0.3s ease;
}
.fade-scale-enter-from {
  opacity: 0;
}

</style>
