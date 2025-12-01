<template>
  <div class="container py-5">
    <h2 class="mb-4">Profile</h2>
    <div v-if="currentUser" class="card">
      <div class="card-body">
        <h5 class="card-title">User Information</h5>
        <p><strong>Username:</strong> {{ currentUser.username }}</p>
        <p><strong>Email:</strong> {{ currentUser.email }}</p>
        <p><strong>User ID:</strong> {{ currentUser.id }}</p>
      </div>
    </div>
    <div v-else class="alert alert-warning">
      Please login to view your profile.
    </div>
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
/* Profile Page Styling with Wikipedia Colors */

/* Page header */
h2 {
  color: var(--wiki-dark);
  font-weight: 700;
  margin-bottom: 2rem;
  padding-bottom: 0.5rem;
  border-bottom: 3px solid var(--wiki-primary);
  transition: color 0.3s ease, border-color 0.3s ease;
}

/* Card styling */
.card {
  border: 1px solid var(--wiki-border);
  border-radius: 0.75rem;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  background-color: var(--wiki-card-bg);
  transition: all 0.3s ease;
}

[data-theme="dark"] .card {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}

.card:hover {
  box-shadow: 0 8px 20px rgba(0, 102, 153, 0.15);
  border-color: var(--wiki-primary);
}

[data-theme="dark"] .card:hover {
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.5);
}

.card-body {
  padding: 2rem;
}

.card-title {
  color: var(--wiki-primary);
  font-weight: 600;
  font-size: 1.5rem;
  margin-bottom: 1.5rem;
  padding-bottom: 0.75rem;
  border-bottom: 2px solid rgba(0, 102, 153, 0.2);
  transition: color 0.3s ease;
}

/* User information */
p {
  color: var(--wiki-text);
  font-size: 1.1rem;
  margin-bottom: 1rem;
  padding: 0.5rem 0;
  transition: color 0.3s ease;
}

p strong {
  color: var(--wiki-primary);
  font-weight: 600;
  display: inline-block;
  min-width: 120px;
  transition: color 0.3s ease;
}

/* Alert styling */
.alert-warning {
  background-color: rgba(153, 0, 0, 0.1);
  border: 1px solid var(--wiki-danger);
  border-left: 4px solid var(--wiki-danger);
  color: var(--wiki-danger);
  border-radius: 0.5rem;
  padding: 1rem 1.5rem;
  font-weight: 500;
}

[data-theme="dark"] .alert-warning {
  background-color: rgba(204, 102, 102, 0.15);
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .container {
    padding-left: 1rem;
    padding-right: 1rem;
  }
  
  h2 {
    font-size: 1.75rem;
    margin-bottom: 1.5rem;
  }
  
  .card-body {
    padding: 1.5rem;
  }
  
  .card-title {
    font-size: 1.25rem;
  }
  
  p {
    font-size: 1rem;
  }
  
  p strong {
    display: block;
    margin-bottom: 0.25rem;
    min-width: auto;
  }
}

@media (max-width: 576px) {
  h2 {
    font-size: 1.5rem;
    margin-bottom: 1rem;
  }
  
  .card-body {
    padding: 1.25rem;
  }
  
  .card-title {
    font-size: 1.1rem;
    margin-bottom: 1rem;
  }
  
  p {
    font-size: 0.95rem;
  }
}
</style>

