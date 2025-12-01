<template>
  <div>
    <!-- Hero Section -->
    <div class="hero-section text-center">
      <div class="container">
        <h1 class="display-4 mb-4">Welcome to WikiContest</h1>
        <p class="lead mb-4">A platform for hosting and participating in collaborative online competitions</p>
        <router-link class="btn btn-cta btn-lg me-3" to="/login">Browse Contests</router-link>
        <router-link class="btn btn-outline-light btn-lg" to="/register">Get Started</router-link>
      </div>
    </div>
    
    <!-- Features Section -->
    <div class="container py-5">
      <div class="row">
        <div class="col-12 col-sm-6 col-md-4 mb-3 mb-md-4">
          <div class="card h-100 text-center">
            <div class="card-body">
              <i class="fas fa-users fa-3x text-primary mb-3"></i>
              <h5 class="card-title">For Participants</h5>
              <p class="card-text">Submit your articles and compete with others in various contests.</p>
            </div>
          </div>
        </div>
        <div class="col-12 col-sm-6 col-md-4 mb-3 mb-md-4">
          <div class="card h-100 text-center">
            <div class="card-body">
              <i class="fas fa-plus-circle fa-3x text-success mb-3"></i>
              <h5 class="card-title">For Organizers</h5>
              <p class="card-text">Create contests, set rules, and manage submissions easily.</p>
            </div>
          </div>
        </div>
        <div class="col-12 col-sm-6 col-md-4 mb-3 mb-md-4">
          <div class="card h-100 text-center">
            <div class="card-body">
              <i class="fas fa-gavel fa-3x text-warning mb-3"></i>
              <h5 class="card-title">For Judges</h5>
              <p class="card-text">Review submissions and maintain fair competition standards.</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Home'
}
</script>

<style scoped>
/* Home Page Styling with Wikipedia Colors */

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
  margin-bottom: 1.5rem;
}

.hero-section .lead {
  font-size: 1.25rem;
  opacity: 0.95;
  margin-bottom: 2rem;
}

/* Button styling */
.btn-cta {
  background: #339966;
  border: none;
  color: white;
  font-weight: 500;
  padding: 0.75rem 2rem;
  font-size: 1.1rem;
  transition: all 0.2s ease;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
}

.btn-cta:hover {
  background: #2d8555;
  transform: translateY(-2px);
  box-shadow: 0 6px 12px rgba(0, 0, 0, 0.3);
  color: white;
}

.btn-outline-light {
  border: 2px solid white;
  color: white;
  font-weight: 500;
  padding: 0.75rem 2rem;
  font-size: 1.1rem;
  transition: all 0.2s ease;
}

.btn-outline-light:hover {
  background: white;
  color: #006699;
  transform: translateY(-2px);
  box-shadow: 0 6px 12px rgba(0, 0, 0, 0.3);
}

/* Features section */
.card {
  border: 1px solid var(--wiki-border);
  border-radius: 0.75rem;
  transition: all 0.3s ease;
  height: 100%;
  overflow: hidden;
  background-color: var(--wiki-card-bg);
}

[data-theme="dark"] .card {
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.3);
}

.card:hover {
  transform: translateY(-8px);
  box-shadow: 0 12px 24px rgba(0, 102, 153, 0.15);
  border-color: var(--wiki-primary);
}

[data-theme="dark"] .card:hover {
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.5);
}

.card-body {
  padding: 2rem;
}

.card-title {
  color: var(--wiki-dark);
  font-weight: 600;
  margin-top: 1rem;
  margin-bottom: 1rem;
  transition: color 0.3s ease;
}

.card-text {
  color: var(--wiki-text-muted);
  line-height: 1.6;
  transition: color 0.3s ease;
}

/* Icon styling */
.text-primary {
  color: var(--wiki-primary) !important;
}

.text-success {
  color: var(--wiki-success) !important;
}

.text-warning {
  color: var(--wiki-danger) !important;
}

.fa-3x {
  margin-bottom: 1rem;
  transition: transform 0.3s ease;
}

.card:hover .fa-3x {
  transform: scale(1.1);
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .container {
    padding-left: 1rem;
    padding-right: 1rem;
  }
  
  .hero-section {
    padding: 60px 0;
  }
  
  .hero-section h1 {
    font-size: 2rem;
  }
  
  .hero-section .lead {
    font-size: 1rem;
  }
  
  .btn-cta,
  .btn-outline-light {
    display: block;
    width: 100%;
    margin-bottom: 1rem;
  }
  
  .card-body {
    padding: 1.5rem;
  }
  
  /* Better spacing for mobile */
  .row {
    margin-left: -0.5rem;
    margin-right: -0.5rem;
  }
  
  .row > * {
    padding-left: 0.5rem;
    padding-right: 0.5rem;
  }
}

@media (max-width: 576px) {
  .hero-section {
    padding: 40px 0;
  }
  
  .hero-section h1 {
    font-size: 1.75rem;
  }
  
  .hero-section .lead {
    font-size: 0.9rem;
  }
  
  .card-body {
    padding: 1.25rem;
  }
  
  .fa-3x {
    font-size: 2rem !important;
  }
  
  .card-title {
    font-size: 1.1rem;
  }
}
</style>

