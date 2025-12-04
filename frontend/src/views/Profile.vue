<template>
  <div class="profile-container">

    <h2 class="page-title">Your Profile</h2>

    <transition name="fade-scale">

      <div v-if="currentUser" class="profile-card">

        <div class="profile-header">
          <div class="avatar">
            <i class="fas fa-user"></i>
          </div>
          <h3>{{ currentUser.username }}</h3>
          <p class="tagline">Wikimedia Contributor</p>
        </div>

        <div class="info-section">
          <div class="info-item">
            <i class="fas fa-user-circle"></i>
            <span><strong>Username</strong> : {{ currentUser.username }}</span>
          </div>

          <div class="info-item">
            <i class="fas fa-envelope"></i>
            <span><strong>Email</strong> : {{ currentUser.email }}</span>
          </div>

          <div class="info-item">
            <i class="fas fa-id-card"></i>
            <span><strong>User ID</strong> : {{ currentUser.id }}</span>
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
import { computed } from 'vue'
import { useStore } from '../store'

export default {
  name: 'Profile',
  setup() {
    const store = useStore()
    const currentUser = computed(() => store.currentUser)

    return {
      currentUser
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

.profile-header h3 {
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--wiki-dark);
  margin-bottom: 0.25rem;
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