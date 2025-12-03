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
/* ==========================================================
   🌟 Modern Premium Dashboard UI (ZERO BREAK CHANGES)
   ========================================================== */

/* Smooth fade entry */
.container {
  animation: fadePage 0.55s ease-out;
}
@keyframes fadePage {
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: translateY(0); }
}

/* Header Premium */
h2.page-header {
  font-size: 2.1rem;
  font-weight: 800;
  color: var(--wiki-dark);
  border-bottom: 3px solid var(--wiki-primary);
  padding-bottom: 8px;
  margin-bottom: 1.8rem;
  letter-spacing: 0.4px;
  transition: 0.3s ease;
}

/* Section Titles */
h4 {
  color: var(--wiki-primary);
  font-size: 1.4rem;
  font-weight: 700;
  margin-bottom: 1rem;
  letter-spacing: 0.3px;
}

/* ==========================================================
   🌟 Modern Glass Cards 
   ========================================================== */

.card {
  border-radius: 16px;
  border: 1px solid rgba(255,255,255,0.25);
  background: rgba(255, 255, 255, 0.16) !important;
  backdrop-filter: blur(18px) saturate(150%);
  -webkit-backdrop-filter: blur(18px) saturate(150%);
  box-shadow: 0 8px 28px rgba(0,0,0,0.08);
  transition: 0.3s ease;
}

[data-theme="dark"] .card {
  background: rgba(30, 30, 30, 0.35) !important;
}

/* Card Hover */
.card:hover {
  transform: translateY(-6px);
  box-shadow: 0 18px 40px rgba(0,0,0,0.15);
}

/* Card Body */
.card-body {
  padding: 1.8rem;
}

/* Card Small Title */
.card-title {
  color: var(--wiki-text-muted);
  font-weight: 600;
  margin-bottom: 1rem;
  font-size: 0.95rem;
  letter-spacing: 0.5px;
}

/* Big Numbers */
h2.text-primary,
h2.text-success,
h2.text-warning {
  font-size: 2.8rem !important;
  font-weight: 800;
  text-shadow: 0 2px 8px rgba(0,0,0,0.15);
}

/* ==========================================================
   🌟 Submissions / Score Items
   ========================================================== */

.d-flex.justify-content-between {
  background: rgba(255,255,255,0.18);
  border-radius: 10px;
  padding: 10px 15px;
  transition: 0.25s ease;
}

.d-flex.justify-content-between:hover {
  background: rgba(0, 140, 186, 0.15);
  transform: translateX(4px);
}

/* Contest Name */
h6 {
  font-weight: 700;
  color: var(--wiki-primary);
}

/* Badges */
.badge {
  padding: 0.45em 0.9em;
  border-radius: 10px;
  font-weight: 500;
  transition: 0.2s ease;
}
.badge:hover {
  transform: scale(1.1);
}

/* ==========================================================
   🌟 List Group (Your Contests)
   ========================================================== */

.list-group-item {
  background: rgba(255,255,255,0.18);
  border: none;
  border-bottom: 1px solid rgba(255,255,255,0.25);
  padding: 1.2rem 1.4rem;
  transition: 0.25s ease;
}

.list-group-item:hover {
  background: rgba(255,255,255,0.28);
  border-left: 4px solid var(--wiki-primary);
  padding-left: calc(1.4rem - 4px);
}

/* Below title */
.list-group-item small {
  color: var(--wiki-text-muted);
}

/* ==========================================================
   🌟 Spinner Animation
   ========================================================== */

.spinner-border.text-primary {
  width: 3rem;
  height: 3rem;
  border-width: 0.28em;
  animation: spinnerPulse 1s infinite ease-in-out;
}
@keyframes spinnerPulse {
  0% { filter: drop-shadow(0 0 0 rgba(0,140,186,0.4)); }
  50% { filter: drop-shadow(0 0 8px rgba(0,140,186,0.7)); }
  100% { filter: drop-shadow(0 0 0 rgba(0,140,186,0.4)); }
}

/* ==========================================================
   🌟 Mobile Friendly
   ========================================================== */

@media(max-width: 768px){
  h2.page-header { font-size: 1.7rem; }
  h4 { font-size: 1.2rem; }
  .card-body { padding: 1.25rem; }
  h2.text-primary,
  h2.text-success,
  h2.text-warning {
    font-size: 2.1rem !important;
  }
}

</style>

