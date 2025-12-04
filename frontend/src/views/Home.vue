<template>
  <div>

    <!-- HERO SECTION - Professional Clean Design -->
    <section class="hero">
      <div class="container">
        <div class="hero-content">
          <h1 class="hero-title">WikiContest</h1>
          <p class="hero-subtitle">Collaborate. Compete. Create Knowledge.</p>
          <p class="hero-description">A professional platform for managing Wikipedia article contests and fostering collaborative knowledge creation.</p>

          <div class="hero-buttons">
            <router-link class="btn btn-primary btn-lg" to="/login">Browse Contests</router-link>
            <router-link class="btn btn-outline-primary btn-lg" to="/register">Get Started</router-link>
          </div>
        </div>
      </div>
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

/* ==========================================================
   Professional Hero Section - Clean & Minimal
   ========================================================== */

/* Hero section - professional solid background */
.hero {
  background-color: var(--wiki-primary);
  color: #ffffff;
  padding: 5rem 0;
  margin-top: 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

[data-theme="dark"] .hero {
  background-color: #1a2332;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

/* Hero content container */
.hero-content {
  text-align: center;
  max-width: 800px;
  margin: 0 auto;
  padding: 0 1rem;
}

/* Hero title - professional typography */
.hero-title {
  font-size: 3rem;
  font-weight: 700;
  margin-bottom: 1rem;
  color: #ffffff;
  letter-spacing: -0.02em;
}

/* Hero subtitle */
.hero-subtitle {
  font-size: 1.5rem;
  font-weight: 500;
  margin-bottom: 0.75rem;
  color: rgba(255, 255, 255, 0.95);
}

/* Hero description */
.hero-description {
  font-size: 1.1rem;
  line-height: 1.6;
  margin-bottom: 2.5rem;
  color: rgba(255, 255, 255, 0.85);
  max-width: 600px;
  margin-left: auto;
  margin-right: auto;
}

/* Hero buttons container */
.hero-buttons {
  display: flex;
  gap: 1rem;
  justify-content: center;
  flex-wrap: wrap;
}

/* Professional button styling */
.hero-buttons .btn {
  padding: 0.75rem 2rem;
  font-weight: 600;
  border-radius: 4px;
  transition: all 0.2s ease;
  text-decoration: none;
}

.hero-buttons .btn-primary {
  background-color: #ffffff;
  color: var(--wiki-primary);
  border: 1px solid #ffffff;
}

.hero-buttons .btn-primary:hover {
  background-color: rgba(255, 255, 255, 0.95);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.hero-buttons .btn-outline-primary {
  background-color: transparent;
  color: #ffffff;
  border: 2px solid rgba(255, 255, 255, 0.8);
}

.hero-buttons .btn-outline-primary:hover {
  background-color: rgba(255, 255, 255, 0.1);
  border-color: #ffffff;
  color: #ffffff;
}

/* ==========================================================
   Features Section - Professional Card Design
   ========================================================== */

.features {
  background-color: var(--wiki-light-bg);
  padding: 4rem 0;
}

[data-theme="dark"] .features {
  background-color: var(--wiki-bg);
}

/* Professional feature cards */
.feature-card {
  background-color: var(--wiki-card-bg);
  border: 1px solid var(--wiki-border);
  border-radius: 6px;
  padding: 2rem;
  text-align: center;
  height: 100%;
  transition: all 0.2s ease;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
}

[data-theme="dark"] .feature-card {
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.3);
}

/* Subtle hover effect */
.feature-card:hover {
  border-color: var(--wiki-primary);
  box-shadow: 0 4px 12px rgba(0, 102, 153, 0.12);
  transform: translateY(-2px);
}

[data-theme="dark"] .feature-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4);
}

/* Professional icon styling */
.icon {
  font-size: 2.5rem;
  margin-bottom: 1rem;
  color: var(--wiki-primary);
  transition: color 0.2s ease;
}

.feature-card:hover .icon {
  color: var(--wiki-primary-hover);
}

/* Card title */
.feature-card h3 {
  font-size: 1.25rem;
  font-weight: 600;
  margin-bottom: 0.75rem;
  color: var(--wiki-dark);
  letter-spacing: -0.01em;
}

/* Card description */
.feature-card p {
  font-size: 0.95rem;
  line-height: 1.6;
  color: var(--wiki-text-muted);
  margin: 0;
}

/* ==========================================================
   Responsive Design
   ========================================================== */

@media (max-width: 768px) {
  .hero {
    padding: 3.5rem 0;
  }

  .hero-title {
    font-size: 2.25rem;
  }

  .hero-subtitle {
    font-size: 1.25rem;
  }

  .hero-description {
    font-size: 1rem;
    margin-bottom: 2rem;
  }

  .hero-buttons {
    flex-direction: column;
    align-items: stretch;
  }

  .hero-buttons .btn {
    width: 100%;
  }

  .features {
    padding: 3rem 0;
  }

  .feature-card {
    padding: 1.5rem;
  }
}

@media (max-width: 576px) {
  .hero-title {
    font-size: 1.875rem;
  }

  .hero-subtitle {
    font-size: 1.125rem;
  }

  .feature-card {
    padding: 1.25rem;
  }

  .icon {
    font-size: 2rem;
  }
}

</style>