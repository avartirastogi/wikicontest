<template>
  <div>

    <!-- HERO SECTION -->
    <section class="hero">
      <div class="hero-inner">
        <h1 class="hero-title">WikiContest</h1>
        <p class="hero-subtitle">Collaborate. Compete. Create Knowledge.</p>

        <div class="hero-buttons">
          <router-link class="btn-primary" to="/login">Browse Contests</router-link>
          <router-link class="btn-secondary" to="/register">Get Started</router-link>
        </div>
      </div>

      <!-- Animated Shapes -->
      <div class="shape shape1"></div>
      <div class="shape shape2"></div>
      <div class="shape shape3"></div>
    </section>

    <!-- FEATURES -->
    <section class="features container py-5">
      <div class="row g-4">

        <div class="col-12 col-md-4">
          <div class="feature-card">
            <i class="fas fa-users icon"></i>
            <h3>Participants</h3>
            <p>Submit articles, collaborate, and compete in global contests.</p>
          </div>
        </div>

        <div class="col-12 col-md-4">
          <div class="feature-card">
            <i class="fas fa-plus-circle icon"></i>
            <h3>Organizers</h3>
            <p>Create contests, manage tasks, and engage communities.</p>
          </div>
        </div>

        <div class="col-12 col-md-4">
          <div class="feature-card">
            <i class="fas fa-gavel icon"></i>
            <h3>Judges</h3>
            <p>Review submissions and ensure fair evaluation.</p>
          </div>
        </div>

      </div>
    </section>

  </div>
</template>


<script>
export default {
  name: 'Home'
}
</script>

<style scoped>

/* ======= COLOR VARIABLES ======= */
:root {
  --crimson: #990000;
  --emerald: #2ecc71;
  --seablue: #2980b9;
  --outerspace: #303030;
  --white: #ffffff;
}

/* ===== HERO SECTION ===== */
.hero {
  position: relative;
  padding: 60px 0px 60px;
  text-align: center;
  overflow: hidden;
  color: #fff;
  margin-top: 10px;

  /* Smooth modern gradient */
  background: linear-gradient(135deg, #0e4d92, #1e9c6c, #0e4d92);
  background-size: 280% 280%;
  animation: gradientSlide 16s ease infinite;
}

/* Glass center layer */
.hero-inner {
  position: relative;
  z-index: 50;
  padding: 2rem 2.5rem;

  backdrop-filter: blur(12px);
  background: rgba(255,255,255,0.05);

  animation: fadeUp 1.2s ease forwards;
  opacity: 0;
}

@keyframes fadeUp {
  from { opacity: 0; transform: translateY(25px); }
  to   { opacity: 1; transform: translateY(0); }
}

@keyframes gradientSlide {
  0% { background-position: 0% 40%; }
  50% { background-position: 100% 60%; }
  100% { background-position: 0% 40%; }
}

/* HERO TEXT */
.hero-title {
  font-size: 3.4rem;
  font-weight: 800;
  letter-spacing: .5px;
  text-shadow: 0 8px 25px rgba(0,0,0,0.35);
}

.hero-subtitle {
  font-size: 1.3rem;
  margin-top: 12px;
  opacity: 0.9;
}

/* ===== Buttons - micro interaction ===== */
.hero-buttons {
  margin-top: 2.4rem;
  display: flex;
  gap: 15px;
  justify-content: center;
}

.btn-primary,
.btn-secondary {
  padding: 13px 36px;
  font-size: 1.1rem;
  border-radius: 50px;
  font-weight: 600;
  display: inline-block;
  transition: 0.3s ease;
  transform-origin: center;
}

/* 3D soft hover */
.btn-primary:hover,
.btn-secondary:hover {
  transform: translateY(-4px) scale(1.03);
  filter: drop-shadow(0 6px 15px rgba(0,0,0,0.25));
}

.btn-primary {
  background: #2ecc71;
  color: white;
}

.btn-secondary {
  border: 2px solid white;
  color: white;
}

.btn-secondary:hover {
  background: white;
  color: #0e4d92;
}

/* ===== Floating Parallax Shapes ===== */
.shape {
  position: absolute;
  border-radius: 50%;
  filter: blur(70px);
  opacity: 0.35;
  animation: floaty infinite ease-in-out alternate;
}

@keyframes floaty {
  0% { transform: translateY(0) translateX(0) scale(1); }
  100% { transform: translateY(-60px) translateX(60px) scale(1.2); }
}

/* Modern blob positions */
.shape1 {
  width: 330px; height: 330px;
  top: -100px; left: -60px;
  background: #2ecc71;
  animation-duration: 13s;
}

.shape2 {
  width: 420px; height: 420px;
  bottom: -120px; right: -40px;
  background: #0e4d92;
  animation-duration: 18s;
}

.shape3 {
  width: 250px; height: 250px;
  top: 40%; left: -30px;
  background: #8e44ad;
  animation-duration: 16s;
}

/* BONUS: Ambient particles */
.hero::before {
  content: "";
  position: absolute;
  inset: 0;
  background-image: radial-gradient(rgba(255,255,255,0.15) 1px, transparent 1px);
  background-size: 28px 28px;
  opacity: 0.12;
  animation: particleMove 20s linear infinite;
}

@keyframes particleMove {
  0% { transform: translateY(0px); }
  100% { transform: translateY(-160px); }
}

/* ===== FEATURES SECTION ===== */
/* FEATURE CARDS — Enhanced, Equal Height, Equal Width */
.features {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 2rem;
}

/* Perfect same-size cards */
.feature-card {
  background: #fff;
  border-radius: 20px;
  padding: 2rem;
  text-align: center;
  width: 100%;
  height: 100%;

  /* Ensures equal height for all cards */
  min-height: 200px;

  /* Flex layout to auto center content */
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: flex-start;

  border-top: 6px solid var(--seablue);

  box-shadow: 0 5px 18px rgba(0,0,0,0.1);
  transition: all .35s ease;
}

/* Hover effect */
.feature-card:hover {
  transform: translateY(-12px) scale(1.03);
  box-shadow: 0 18px 40px rgba(0,0,0,0.18);
  border-top-color: var(--emerald);
}

/* Icons */
.icon {
  font-size: 3.2rem;
  margin-bottom: 15px;
  color: var(--seablue);
  transition: 0.3s ease;
}

/* Icon hover animation */
.feature-card:hover .icon {
  color: var(--emerald);
  transform: scale(1.18);
}

/* Title inside card */
.feature-card h3 {
  font-size: 1.45rem;
  margin-bottom: 0.8rem;
  font-weight: 700;
  letter-spacing: 0.3px;
  color: var(--outerspace);
}

/* Description text */
.feature-card p {
  font-size: 1.05rem;
  opacity: 0.9;
  line-height: 1.5rem;
  color: #505050;
  padding: 0 0.5rem;
}

/* RESPONSIVE TUNING */
@media (max-width: 992px) {
  .feature-card {
    min-height: 280px;
  }
}

@media (max-width: 768px) {
  .feature-card {
    min-height: 260px;
    padding: 1.7rem;
  }
}

@media (max-width: 576px) {
  .features {
    gap: 1.5rem;
  }

  .feature-card {
    min-height: 240px;
    padding: 1.5rem;
  }
}


/* Responsive */
@media (max-width: 768px) {
  .hero-title { font-size: 2.5rem; }
  .hero-inner { padding: 1.4rem; }
  .hero-buttons { flex-direction: column; }
}

</style>