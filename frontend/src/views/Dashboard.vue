<template>
    <div class="container py-5">
      <h2 class="mb-4 page-header">Dashboard</h2>
    
    <!-- Loading State -->
    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
    </div>

    <!-- Dashboard Content -->
    <div v-else-if="dashboardData">
      <!-- Statistics Cards -->
      <div class="row mb-4">
        <div class="col-12 col-sm-6 col-md-4 mb-3 mb-md-4">
          <div class="card text-center h-100">
            <div class="card-body">
              <h5 class="card-title">Total Score</h5>
              <h2 class="text-primary">{{ dashboardData.total_score || 0 }}</h2>
            </div>
          </div>
        </div>
        <div class="col-12 col-sm-6 col-md-4 mb-3 mb-md-4">
          <div class="card text-center h-100">
            <div class="card-body">
              <h5 class="card-title">Created Contests</h5>
              <h2 class="text-success">{{ dashboardData.created_contests?.length || 0 }}</h2>
            </div>
          </div>
        </div>
        <div class="col-12 col-sm-6 col-md-4 mb-3 mb-md-4">
          <div class="card text-center h-100">
            <div class="card-body">
              <h5 class="card-title">Jury Member</h5>
              <h2 class="text-warning">{{ dashboardData.jury_contests?.length || 0 }}</h2>
            </div>
          </div>
        </div>
      </div>

      <!-- Submissions and Scores -->
      <div class="row">
        <!-- Recent Submissions -->
        <div class="col-12 col-md-6 mb-3 mb-md-4">
          <h4 class="mb-3">Recent Submissions</h4>
          <div class="card h-100">
            <div class="card-body">
              <div v-if="dashboardData.submissions_by_contest?.length > 0">
                <div 
                  v-for="contest in dashboardData.submissions_by_contest" 
                  :key="contest.contest_id"
                  class="mb-3"
                >
                  <h6>{{ contest.contest_name }}</h6>
                  <div 
                    v-for="submission in contest.submissions" 
                    :key="submission.id"
                    class="d-flex justify-content-between align-items-center mb-2 flex-wrap"
                  >
                    <span class="me-2 mb-1">{{ submission.article_title }}</span>
                    <span 
                      :class="`badge bg-${getStatusColor(submission.status)}`"
                    >
                      {{ submission.status }}
                    </span>
                  </div>
                </div>
              </div>
              <p v-else class="text-muted">No submissions yet.</p>
            </div>
          </div>
        </div>

        <!-- Contest Scores -->
        <div class="col-12 col-md-6 mb-3 mb-md-4">
          <h4 class="mb-3">Contest Scores</h4>
          <div class="card h-100">
            <div class="card-body">
              <div v-if="dashboardData.contest_wise_scores?.length > 0">
                <div 
                  v-for="score in dashboardData.contest_wise_scores" 
                  :key="score.contest_id"
                  class="d-flex justify-content-between align-items-center mb-2 flex-wrap"
                >
                  <span class="me-2 mb-1">{{ score.contest_name }}</span>
                  <span class="badge bg-primary">{{ score.contest_score }} points</span>
                </div>
              </div>
              <p v-else class="text-muted">No scores yet.</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Created Contests List -->
      <div v-if="dashboardData.created_contests?.length > 0" class="row mt-4">
        <div class="col-12">
          <h4 class="mb-3">Your Contests</h4>
          <div class="card">
            <div class="card-body">
              <div class="list-group">
                <div
                  v-for="contest in dashboardData.created_contests"
                  :key="contest.id"
                  class="list-group-item list-group-item-action"
                  @click="viewContest(contest.id)"
                  style="cursor: pointer;"
                >
                  <div class="d-flex justify-content-between align-items-center">
                    <div>
                      <h6 class="mb-1">{{ contest.name }}</h6>
                      <small class="text-muted">{{ contest.project_name }}</small>
                    </div>
                    <span class="badge bg-primary">{{ contest.status }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="alert alert-danger">
      {{ error }}
    </div>

    <!-- Contest Details Modal -->
    <ContestModal 
      :contest="selectedContest"
      @submit-article="handleSubmitArticle"
      @contest-deleted="handleContestDeleted"
    />

    <!-- Submit Article Modal -->
    <SubmitArticleModal
      v-if="submittingToContestId"
      :contest-id="submittingToContestId"
      @submitted="handleArticleSubmitted"
    />
  </div>
</template>

<script>
import { ref, onMounted, nextTick } from 'vue'
import { useStore } from '../store'
import api from '../services/api'
import { showAlert } from '../utils/alerts'
import ContestModal from '../components/ContestModal.vue'
import SubmitArticleModal from '../components/SubmitArticleModal.vue'

export default {
  name: 'Dashboard',
  components: {
    ContestModal,
    SubmitArticleModal
  },
  setup() {
    const store = useStore()
    const dashboardData = ref(null)
    const loading = ref(true)
    const error = ref(null)
    const selectedContest = ref(null)
    const submittingToContestId = ref(null)

    // Load dashboard data
    const loadDashboard = async () => {
      loading.value = true
      error.value = null
      try {
        const data = await api.get('/user/dashboard')
        dashboardData.value = data
      } catch (err) {
        error.value = err.message || 'Failed to load dashboard'
        showAlert(error.value, 'danger')
      } finally {
        loading.value = false
      }
    }

    // Get status color for badges
    const getStatusColor = (status) => {
      const statusColors = {
        'accepted': 'success',
        'rejected': 'danger',
        'pending': 'warning'
      }
      return statusColors[status] || 'secondary'
    }

    // View contest details - opens modal
    const viewContest = async (contestId) => {
      try {
        const contest = await api.get(`/contest/${contestId}`)
        selectedContest.value = contest
        
        // Wait for Vue to render the modal component
        await nextTick()
        
        // Small delay to ensure modal is fully rendered
        await new Promise(resolve => setTimeout(resolve, 100))
        
        // Show modal using Bootstrap
        const modalElement = document.getElementById('contestModal')
        if (modalElement) {
          // Check if modal instance already exists
          let modal = bootstrap.Modal.getInstance(modalElement)
          if (!modal) {
            // Create new modal instance
            modal = new bootstrap.Modal(modalElement, {
              backdrop: true,
              keyboard: true
            })
          }
          // Show the modal
          modal.show()
        } else {
          console.error('Modal element not found!')
          // Try one more time after a longer delay
          setTimeout(() => {
            const retryElement = document.getElementById('contestModal')
            if (retryElement) {
              const modal = new bootstrap.Modal(retryElement)
              modal.show()
            } else {
              showAlert('Failed to open contest details. Please refresh the page.', 'warning')
            }
          }, 200)
        }
      } catch (error) {
        console.error('Error loading contest:', error)
        showAlert('Failed to load contest details: ' + error.message, 'danger')
      }
    }

    // Handle submit article
    const handleSubmitArticle = (contestId) => {
      if (!store.isAuthenticated) {
        showAlert('Please login to submit an article', 'warning')
        return
      }
      submittingToContestId.value = contestId
      
      // Show submit modal using Bootstrap
      setTimeout(() => {
        const modalElement = document.getElementById('submitArticleModal')
        if (modalElement) {
          const modal = new bootstrap.Modal(modalElement)
          modal.show()
        }
      }, 100)
    }

    // Handle article submitted
    const handleArticleSubmitted = () => {
      submittingToContestId.value = null
      // Reload dashboard to update data
      loadDashboard()
    }

    // Handle contest deleted
    const handleContestDeleted = () => {
      selectedContest.value = null
      // Reload dashboard to remove deleted contest
      loadDashboard()
    }

    // Load data on mount
    onMounted(() => {
      loadDashboard()
    })

    return {
      dashboardData,
      loading,
      error,
      selectedContest,
      submittingToContestId,
      getStatusColor,
      viewContest,
      handleSubmitArticle,
      handleArticleSubmitted,
      handleContestDeleted
    }
  }
}
</script>

<style scoped>
/* Dashboard Styling with Wikipedia Colors */

/* Page header - only apply to main page header, not card h2 elements */
h2.page-header {
  color: var(--wiki-dark);
  font-weight: 700;
  margin-bottom: 2rem;
  padding-bottom: 0.5rem;
  border-bottom: 3px solid var(--wiki-primary);
  transition: color 0.3s ease, border-color 0.3s ease;
}

/* Ensure card h2 elements don't have borders */
.card h2 {
  border-bottom: none !important;
  padding-bottom: 0 !important;
  margin-bottom: 0 !important;
}

h4 {
  color: var(--wiki-primary);
  font-weight: 600;
  margin-bottom: 1rem;
  border-bottom: none;
  padding-bottom: 0;
  transition: color 0.3s ease;
}

/* Statistics cards - subtle border */
.card {
  border: 1px solid var(--wiki-border);
  border-radius: 0.75rem;
  transition: all 0.3s ease;
  height: 100%;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  background-color: var(--wiki-card-bg);
}

[data-theme="dark"] .card {
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.3);
}

.card:hover {
  transform: translateY(-3px);
  box-shadow: 0 4px 12px rgba(0, 102, 153, 0.1);
  border-color: var(--wiki-border);
}

[data-theme="dark"] .card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.5);
}

.card-body {
  padding: 2rem;
}

.card-title {
  color: var(--wiki-text-muted);
  font-weight: 500;
  font-size: 1rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 1rem;
  transition: color 0.3s ease;
}

/* Score numbers */
h2.text-primary {
  color: var(--wiki-primary) !important;
  font-weight: 700;
  font-size: 2.5rem;
}

h2.text-success {
  color: var(--wiki-success) !important;
  font-weight: 700;
  font-size: 2.5rem;
}

h2.text-warning {
  color: var(--wiki-danger) !important;
  font-weight: 700;
  font-size: 2.5rem;
}

/* Section cards */
.card h6 {
  color: var(--wiki-primary);
  font-weight: 600;
  margin-bottom: 1rem;
  padding-bottom: 0;
  border-bottom: none;
  transition: color 0.3s ease;
}

/* Badge styling */
.badge {
  font-weight: 500;
  padding: 0.4em 0.8em;
}

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

/* List group styling - remove borders between items */
.list-group {
  border: none;
}

.list-group-item {
  border: none;
  border-bottom: 1px solid var(--wiki-border);
  background-color: var(--wiki-card-bg);
  color: var(--wiki-text);
  transition: all 0.2s ease;
  padding: 1rem 1.5rem;
}

.list-group-item:last-child {
  border-bottom: none;
}

.list-group-item:hover {
  background-color: var(--wiki-hover-bg);
  border-left: 3px solid var(--wiki-primary);
  padding-left: calc(1.5rem - 3px);
  border-bottom-color: var(--wiki-border);
}

.list-group-item-action {
  color: var(--wiki-dark);
  text-decoration: none;
  transition: color 0.2s ease;
}

.list-group-item-action:hover {
  color: var(--wiki-primary);
}

.list-group-item h6 {
  color: var(--wiki-dark);
  font-weight: 600;
  margin-bottom: 0.25rem;
  transition: color 0.3s ease;
}

.list-group-item small {
  color: var(--wiki-text-muted);
  transition: color 0.3s ease;
}

/* Text colors */
.text-muted {
  color: var(--wiki-text-muted) !important;
}

/* Alert styling */
.alert-danger {
  background-color: rgba(153, 0, 0, 0.1);
  border: 1px solid var(--wiki-danger);
  border-left: 4px solid var(--wiki-danger);
  color: var(--wiki-danger);
  border-radius: 0.5rem;
}

[data-theme="dark"] .alert-danger {
  background-color: rgba(204, 102, 102, 0.15);
}

/* Spinner */
.spinner-border.text-primary {
  color: var(--wiki-primary) !important;
  width: 3rem;
  height: 3rem;
  border-width: 0.3em;
}

/* Submission items */
.d-flex.justify-content-between {
  padding: 0.75rem;
  border-radius: 0.25rem;
  transition: background-color 0.2s ease;
}

.d-flex.justify-content-between:hover {
  background-color: var(--wiki-hover-bg);
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .container {
    padding-left: 1rem;
    padding-right: 1rem;
  }
  
  .card-body {
    padding: 1.25rem;
  }
  
  h2.page-header {
    font-size: 1.75rem;
    margin-bottom: 1.5rem;
  }
  
  h2.text-primary,
  h2.text-success,
  h2.text-warning {
    font-size: 2rem;
  }
  
  h4 {
    font-size: 1.25rem;
  }
  
  .card-title {
    font-size: 0.9rem;
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
  .card-body {
    padding: 1rem;
  }
  
  h2.text-primary,
  h2.text-success,
  h2.text-warning {
    font-size: 1.75rem;
  }
  
  h2.page-header {
    font-size: 1.5rem;
  }
}
</style>

