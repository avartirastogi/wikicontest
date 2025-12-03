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
   Modern Profile Page UI
   =============================== */

.profile-container {
  max-width: 700px;
  margin: auto;
  padding: 3rem 1rem;
  animation: fadeUp 0.8s ease-out;
}

/* ===============================
   Page Title
   =============================== */
.page-title {
  text-align: center;
  font-size: 2.4rem;
  font-weight: 800;
  letter-spacing: -0.5px;
  margin-bottom: 2.8rem;
  color: var(--seablue);
  position: relative;
}

.page-title::after {
  content: "";
  width: 80px;
  height: 4px;
  background: var(--emerald);
  position: absolute;
  bottom: -10px;
  left: 50%;
  transform: translateX(-50%);
  border-radius: 50px;
  animation: underlineGrow 1s ease-in-out forwards;
}

/* Underline Animation */
@keyframes underlineGrow {
  from { width: 0; opacity: 0; }
  to { width: 80px; opacity: 1; }
}

/* ===============================
   Profile Card – Glassmorphism
   =============================== */
.profile-card {
  backdrop-filter: blur(14px);
  background: rgba(255,255,255,0.13);
  border-radius: 20px;
  padding: 2.5rem;
  border: 1px solid rgba(255,255,255,0.25);
  box-shadow: 0 15px 35px rgba(0,0,0,0.15);
  animation: floatCard 6s ease-in-out infinite alternate;
  transition: 0.3s ease;
}

[data-theme="dark"] .profile-card {
  background: rgba(0,0,0,0.25);
  border: 1px solid rgba(255,255,255,0.12);
}

/* Subtle float animation */
@keyframes floatCard {
  0% { transform: translateY(0px); }
  100% { transform: translateY(-8px); }
}

/* ===============================
   Profile Header with Avatar
   =============================== */
.profile-header {
  text-align: center;
  margin-bottom: 2.2rem;
}

.avatar {
  width: 90px;
  height: 90px;
  margin: auto;
  border-radius: 50%;
  background: var(--seablue);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 2.2rem;
  margin-bottom: 1rem;
  box-shadow: 0 10px 25px rgba(0,0,0,0.25);
  transition: 0.3s;
}

.avatar:hover {
  transform: scale(1.1);
  background: var(--emerald);
}

.profile-header h3 {
  font-size: 1.8rem;
  font-weight: 700;
}

.tagline {
  font-size: 1rem;
  opacity: 0.75;
  margin-top: 5px;
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
  border-radius: 14px;
  margin-bottom: 1rem;
  background: rgba(255,255,255,0.25);
  border: 1px solid rgba(0,0,0,0.07);
  transition: 0.3s ease;
}

[data-theme="dark"] .info-item {
  background: rgba(255,255,255,0.08);
  border-color: rgba(255,255,255,0.15);
}

.info-item i {
  font-size: 1.6rem;
  margin-right: 1rem;
  color: var(--seablue);
  transition: 0.3s ease;
}

.info-item:hover {
  transform: translateX(6px);
  background: rgba(0,102,153,0.15);
  border-color: var(--seablue);
}

.info-item:hover i {
  color: var(--emerald);
  transform: scale(1.2);
}

.info-item strong {
  color: var(--seablue);
  font-size: 1.1rem;
}

/* ===============================
   Alert Message
   =============================== */
.alert-message {
  background: rgba(153, 0, 0, 0.15);
  color: var(--crimson);
  padding: 1.5rem;
  border-radius: 12px;
  border-left: 5px solid var(--crimson);
  text-align: center;
  font-size: 1.1rem;
  font-weight: 600;
  animation: fadeUp 0.7s ease-out;
}

.alert-message i {
  margin-right: 8px;
  font-size: 1.2rem;
}

/* ===============================
   Entrance Animation
   =============================== */
@keyframes fadeUp {
  from { opacity: 0; transform: translateY(18px); }
  to { opacity: 1; transform: translateY(0); }
}

/* Smooth fade + scale */
.fade-scale-enter-active {
  transition: .4s ease;
}
.fade-scale-enter-from {
  opacity: 0;
  transform: scale(0.95);
}

</style>