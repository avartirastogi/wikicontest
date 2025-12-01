<template>
  <div class="section">
    <div class="container py-5">
      <div class="row justify-content-center">
        <div class="col-md-6">
          <div class="card">
            <div class="card-body">
              <h3 class="card-title text-center mb-4">Register</h3>
              <form @submit.prevent="handleRegister">
                <div class="mb-3">
                  <label for="registerUsername" class="form-label">Username</label>
                  <input 
                    type="text" 
                    class="form-control" 
                    id="registerUsername" 
                    v-model="username"
                    required
                  >
                </div>
                <div class="mb-3">
                  <label for="registerEmail" class="form-label">Email</label>
                  <input 
                    type="email" 
                    class="form-control" 
                    id="registerEmail" 
                    v-model="email"
                    required
                  >
                </div>
                <div class="mb-3">
                  <label for="registerPassword" class="form-label">Password</label>
                  <input 
                    type="password" 
                    class="form-control" 
                    id="registerPassword" 
                    v-model="password"
                    required
                  >
                </div>
                <button 
                  type="submit" 
                  class="btn btn-primary w-100"
                  :disabled="loading"
                >
                  <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
                  Register
                </button>
              </form>
              <div class="text-center mt-3">
                <p>Already have an account? 
                  <router-link to="/login">Login here</router-link>
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue'
import { useStore } from '../store'
import { useRouter } from 'vue-router'
import { showAlert } from '../utils/alerts'

export default {
  name: 'Register',
  setup() {
    const store = useStore()
    const router = useRouter()
    
    const username = ref('')
    const email = ref('')
    const password = ref('')
    const loading = ref(false)

    const handleRegister = async () => {
      loading.value = true
      try {
        const result = await store.register({ 
          username: username.value, 
          email: email.value, 
          password: password.value 
        })
        if (result.success) {
          showAlert('Registration successful! Please login.', 'success')
          router.push('/login')
        } else {
          showAlert(result.error || 'Registration failed', 'danger')
        }
      } catch (error) {
        showAlert(error.message || 'Registration failed', 'danger')
      } finally {
        loading.value = false
      }
    }

    return {
      username,
      email,
      password,
      loading,
      handleRegister
    }
  }
}
</script>

<style scoped>
/* Register Page Styling with Wikipedia Colors */

.section {
  min-height: calc(100vh - 200px);
  display: flex;
  align-items: center;
}

/* Card styling */
.card {
  border: 1px solid var(--wiki-border);
  border-radius: 0.75rem;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  background-color: var(--wiki-card-bg);
  overflow: hidden;
  transition: background-color 0.3s ease, border-color 0.3s ease;
}

[data-theme="dark"] .card {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}

.card-body {
  padding: 2.5rem;
}

.card-title {
  color: var(--wiki-primary);
  font-weight: 700;
  font-size: 2rem;
  margin-bottom: 2rem;
  transition: color 0.3s ease;
}

/* Form styling */
.form-label {
  color: var(--wiki-dark);
  font-weight: 500;
  margin-bottom: 0.5rem;
  transition: color 0.3s ease;
}

.form-control {
  border-color: var(--wiki-input-border);
  background-color: var(--wiki-input-bg);
  color: var(--wiki-text);
  transition: all 0.2s ease;
  padding: 0.75rem;
}

.form-control:focus {
  border-color: var(--wiki-primary);
  box-shadow: 0 0 0 0.2rem rgba(0, 102, 153, 0.25);
  background-color: var(--wiki-input-bg);
  color: var(--wiki-text);
}

/* Button styling */
.btn-primary {
  background-color: var(--wiki-primary);
  border-color: var(--wiki-primary);
  font-weight: 500;
  padding: 0.75rem;
  transition: all 0.2s ease;
}

.btn-primary:hover {
  background-color: var(--wiki-primary-hover);
  border-color: var(--wiki-primary-hover);
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(0, 102, 153, 0.3);
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* Text styling */
.text-muted {
  color: var(--wiki-text-muted) !important;
}

/* Link styling */
a {
  color: var(--wiki-primary);
  font-weight: 500;
  transition: color 0.2s ease;
}

a:hover {
  color: var(--wiki-primary-hover);
  text-decoration: underline;
}

/* Spinner */
.spinner-border-sm {
  width: 1rem;
  height: 1rem;
  border-width: 0.15em;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .container {
    padding-left: 1rem;
    padding-right: 1rem;
  }
  
  .section {
    min-height: calc(100vh - 150px);
    padding: 1rem 0;
  }
  
  .card-body {
    padding: 1.5rem;
  }
  
  .card-title {
    font-size: 1.5rem;
  }
}

@media (max-width: 576px) {
  .section {
    min-height: auto;
    padding: 0.5rem 0;
  }
  
  .card-body {
    padding: 1.25rem;
  }
  
  .card-title {
    font-size: 1.25rem;
    margin-bottom: 1.5rem;
  }
  
  .form-control {
    font-size: 16px; /* Prevents zoom on iOS */
  }
}
</style>

