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
                    class="submission-item d-flex justify-content-between align-items-center mb-2 flex-wrap"
                    :class="{ 'submission-clickable': submission.reviewed_at }"
                    @click="handleSubmissionClick(submission)"
                  >
                    <span class="me-2 mb-1 submission-title">
                      {{ submission.article_title }}
                    </span>
                    <div class="d-flex align-items-center gap-2">
                      <span
                        :class="`badge bg-${getStatusColor(submission.status)}`"
                      >
                        {{ submission.status }}
                      </span>
                      <!-- View Feedback Button/Icon - Only for reviewed submissions -->
                      <button
                        v-if="submission.reviewed_at"
                        class="btn btn-sm btn-info feedback-btn"
                        @click.stop="openFeedbackModal(submission)"
                        title="View Feedback"
                      >
                        <i class="fas fa-comment-dots"></i>
                      </button>
                    </div>
                  </div>
                </div>
              </div>
              <p v-else class="text-muted no-submissions">No submissions yet.</p>
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
              <p v-else class="text-muted no-scores">No scores yet.</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Created Contests Table -->
      <div class="row mt-4">
        <div class="col-12">
          <h4 class="mb-3">Your Contests</h4>
          <div class="card">
            <div class="card-body p-0">
              <!-- Table with contests -->
              <div v-if="dashboardData.created_contests?.length > 0" class="table-responsive">
                <table class="table table-hover mb-0">
                  <thead>
                    <tr>
                      <th scope="col">Contest Name</th>
                      <th scope="col">Project</th>
                      <th scope="col">Status</th>
                      <th scope="col">Submissions</th>
                      <th scope="col">Created Date</th>
                      <th scope="col">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr
                      v-for="contest in dashboardData.created_contests"
                      :key="contest.id"
                      @click="viewContest(contest.id)"
                      class="table-row-clickable"
                    >
                      <td>
                        <strong>{{ contest.name }}</strong>
                      </td>
                      <td>{{ contest.project_name || 'N/A' }}</td>
                      <td>
                        <span
                          class="badge"
                          :class="`bg-${getStatusBadgeColor(contest.status)}`"
                        >
                          {{ contest.status || 'Unknown' }}
                        </span>
                      </td>
                      <td>{{ contest.submission_count || 0 }}</td>
                      <td>{{ formatDate(contest.created_at) }}</td>
                      <td>
                        <button
                          class="btn btn-sm btn-outline-primary"
                          @click.stop="viewContest(contest.id)"
                        >
                          <i class="fas fa-eye me-1"></i>View
                        </button>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
              <!-- Empty state message -->
              <div v-else class="text-center py-5 px-3">
                <p class="text-muted mb-0 no-contests">
                  <i class="fas fa-info-circle me-2"></i>
                  No contests created yet.
                </p>
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

    <!-- Submit Article Modal -->
    <SubmitArticleModal
      v-if="submittingToContestId"
      :contest-id="submittingToContestId"
      @submitted="handleArticleSubmitted"
    />

    <!-- Jury Feedback Modal -->
    <JuryFeedbackModal
      :submission="selectedSubmission"
      :reviewer-name="reviewerName"
      :loading-reviewer="loadingReviewer"
    />
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useStore } from '../store'
import api from '../services/api'
import { showAlert } from '../utils/alerts'
import { slugify } from '../utils/slugify'
import SubmitArticleModal from '../components/SubmitArticleModal.vue'
import JuryFeedbackModal from '../components/JuryFeedbackModal.vue'

export default {
  name: 'Dashboard',
  components: {
    SubmitArticleModal,
    JuryFeedbackModal
  },
  setup() {
    const router = useRouter()
    const store = useStore()
    const dashboardData = ref(null)
    const loading = ref(true)
    const error = ref(null)
    const submittingToContestId = ref(null)

    // Feedback modal state
    const selectedSubmission = ref(null)
    const reviewerName = ref('')
    const loadingReviewer = ref(false)

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
        accepted: 'success',
        rejected: 'danger',
        pending: 'warning'
      }
      return statusColors[status] || 'secondary'
    }

    // Get status badge color for contest status
    const getStatusBadgeColor = (status) => {
      const statusColors = {
        current: 'success',
        active: 'success',
        upcoming: 'warning',
        past: 'secondary',
        completed: 'info'
      }
      return statusColors[status?.toLowerCase()] || 'primary'
    }

    // Format date for display
    const formatDate = (dateString) => {
      if (!dateString) return 'N/A'
      try {
        const date = new Date(dateString)
        return date.toLocaleDateString('en-US', {
          year: 'numeric',
          month: 'short',
          day: 'numeric'
        })
      } catch (e) {
        return dateString
      }
    }

    // Handle submission click (only if reviewed)
    const handleSubmissionClick = (submission) => {
      if (submission.reviewed_at) {
        openFeedbackModal(submission)
      }
    }

    // Fetch reviewer username
    const fetchReviewerName = async (reviewerId) => {
      if (!reviewerId) {
        reviewerName.value = 'Jury Member'
        return
      }

      loadingReviewer.value = true
      try {
        // Use the new username endpoint to fetch reviewer name
        const userData = await api.get(`/user/${reviewerId}/username`)

        if (userData && userData.username) {
          reviewerName.value = userData.username
        } else {
          reviewerName.value = 'Jury Member'
        }
      } catch (err) {
        console.warn('Could not fetch reviewer name:', err)
        // Fallback to generic name if endpoint doesn't exist yet
        reviewerName.value = 'Jury Member'
      } finally {
        loadingReviewer.value = false
      }
    }

    // Open feedback modal
    const openFeedbackModal = async (submission) => {
      if (!submission || !submission.reviewed_at) {
        showAlert('This submission has not been reviewed yet', 'info')
        return
      }

      // Set selected submission
      selectedSubmission.value = submission

      // Fetch reviewer name if available
      if (submission.reviewed_by) {
        await fetchReviewerName(submission.reviewed_by)
      } else {
        reviewerName.value = 'Jury Member'
      }

      // Open modal
      const modalEl = document.getElementById('juryFeedbackModal')
      if (!modalEl) {
        console.error('JuryFeedbackModal DOM not found')
        return
      }

      const modal = new window.bootstrap.Modal(modalEl)
      modal.show()
    }

    // View contest details - navigate to full page view
    const viewContest = (contestId) => {
      // Find the contest object from dashboard data
      let contestData = null

      // Check in created contests
      if (dashboardData.value?.created_contests) {
        contestData = dashboardData.value.created_contests.find(c => c.id === contestId)
      }

      // If not found, try to get from store (all contests)
      if (!contestData) {
        const allContests = store.getContestsByCategory('current')
          .concat(store.getContestsByCategory('upcoming'))
          .concat(store.getContestsByCategory('past'))
        contestData = allContests.find(c => c.id === contestId)
      }

      // If still not found, try to fetch it
      if (!contestData) {
        // Fallback: fetch contest by ID to get the name
        api.get(`/contest/${contestId}`)
          .then(contest => {
            if (contest && contest.name) {
              const contestSlug = slugify(contest.name)
              router.push({ name: 'ContestView', params: { name: contestSlug } })
            } else {
              showAlert('Contest not found', 'danger')
            }
          })
          .catch(error => {
            console.error('Error loading contest:', error)
            showAlert('Failed to load contest details: ' + error.message, 'danger')
          })
        return
      }

      // If we have the contest data, navigate to full page
      if (contestData && contestData.name) {
        const contestSlug = slugify(contestData.name)
        router.push({ name: 'ContestView', params: { name: contestSlug } })
      } else {
        showAlert('Contest not found', 'danger')
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


    // Load data on mount
    onMounted(() => {
      loadDashboard()
    })

    return {
      dashboardData,
      loading,
      error,
      submittingToContestId,
      selectedSubmission,
      reviewerName,
      loadingReviewer,
      getStatusColor,
      getStatusBadgeColor,
      formatDate,
      viewContest,
      handleSubmitArticle,
      handleArticleSubmitted,
      handleSubmissionClick,
      openFeedbackModal
    }
  }
}
</script>

<style scoped>
/* ==========================================================
   Professional Dashboard UI - Clean Design
   ========================================================== */

/* Page header - professional styling */
h2.page-header {
  font-size: 2rem;
  font-weight: 600;
  color: var(--wiki-dark);
  border-bottom: 2px solid var(--wiki-primary);
  padding-bottom: 0.5rem;
  margin-bottom: 2rem;
  letter-spacing: -0.01em;
}

/* Ensure page header is visible in dark mode */
[data-theme="dark"] h2.page-header {
  color: #ffffff !important; /* White text for page header */
}

/* Section Titles */
h4 {
  color: var(--wiki-dark);
  font-size: 1.25rem;
  font-weight: 600;
  margin-bottom: 1rem;
  letter-spacing: -0.01em;
}

/* Ensure section titles are visible in dark mode */
[data-theme="dark"] h4 {
  color: #ffffff !important; /* White text for section titles */
}

/* ==========================================================
   Professional Cards
   ========================================================== */

.card {
  border-radius: 4px;
  border: 1px solid var(--wiki-border);
  background-color: var(--wiki-card-bg);
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.04);
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
}

[data-theme="dark"] .card {
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
}

/* Card hover - subtle */
.card:hover {
  border-color: var(--wiki-primary);
  box-shadow: 0 2px 8px rgba(0, 102, 153, 0.1);
}

[data-theme="dark"] .card:hover {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
}

/* Card Body */
.card-body {
  padding: 1.5rem;
}

/* Card title */
.card-title {
  color: var(--wiki-text-muted);
  font-weight: 500;
  margin-bottom: 0.75rem;
  font-size: 0.9rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

/* Ensure card titles are visible in dark mode */
[data-theme="dark"] .card-title {
  color: #b8b8b8 !important; /* Light gray for card titles in dark mode */
}

/* Statistics numbers - professional */
h2.text-primary,
h2.text-success,
h2.text-warning {
  font-size: 2.5rem !important;
  font-weight: 700;
  margin: 0;
}

/* Ensure text colors are visible in dark mode - maintain original colors */
[data-theme="dark"] h2.text-primary {
  color: #006699 !important; /* Original blue color */
}

[data-theme="dark"] h2.text-success {
  color: #339966 !important; /* Original green color */
}

[data-theme="dark"] h2.text-warning {
  color: #ffc107 !important; /* Original yellow/amber color */
}

/* ==========================================================
   Submissions Items with Feedback Feature
   ========================================================== */

.submission-item {
  background-color: var(--wiki-light-bg);
  border: 1px solid var(--wiki-border);
  border-radius: 4px;
  padding: 0.75rem 1rem;
  margin-bottom: 0.5rem;
  transition: all 0.2s ease;
}

[data-theme="dark"] .submission-item {
  background-color: rgba(93, 184, 230, 0.05);
}

/* Clickable submissions (reviewed) */
.submission-clickable {
  cursor: pointer;
}

.submission-clickable:hover {
  background-color: var(--wiki-hover-bg);
  border-color: var(--wiki-primary);
  transform: translateX(2px);
}

.submission-clickable:hover .submission-title {
  color: var(--wiki-primary);
}

/* Ensure text in submission items is visible in dark mode */
[data-theme="dark"] .submission-item span {
  color: #ffffff !important; /* White text for submission items */
}

/* Feedback button in submission items */
.feedback-btn {
  color: white;
  padding: 0.25rem 0.5rem;
  font-size: 0.875rem;
  transition: all 0.2s ease;
}

.feedback-btn:hover {
  transform: scale(1.05);
}

.feedback-btn i {
  font-size: 0.875rem;
}

/* Score items (no changes) */
.d-flex.justify-content-between:not(.submission-item) {
  background-color: var(--wiki-light-bg);
  border: 1px solid var(--wiki-border);
  border-radius: 4px;
  padding: 0.75rem 1rem;
  margin-bottom: 0.5rem;
  transition: all 0.2s ease;
}

[data-theme="dark"] .d-flex.justify-content-between:not(.submission-item) {
  background-color: rgba(93, 184, 230, 0.05);
}

/* Ensure text in score items is visible in dark mode */
[data-theme="dark"] .d-flex.justify-content-between:not(.submission-item) span {
  color: #ffffff !important; /* White text for score items */
}

.d-flex.justify-content-between:not(.submission-item):hover {
  background-color: var(--wiki-hover-bg);
  border-color: var(--wiki-primary);
}

/* Contest Name */
h6 {
  font-weight: 600;
  color: var(--wiki-dark);
  margin: 0;
  font-size: 1rem;
}

/* Ensure contest names are visible in dark mode */
[data-theme="dark"] h6 {
  color: #ffffff !important; /* White text for contest names */
}

/* Badges - professional */
.badge {
  padding: 0.35em 0.7em;
  border-radius: 4px;
  font-weight: 500;
  font-size: 0.85rem;
}

/* Ensure badge colors are visible in dark mode - maintain original colors */
[data-theme="dark"] .badge.bg-primary {
  background-color: #006699 !important; /* Original blue color */
  color: #ffffff !important; /* White text */
}

[data-theme="dark"] .badge.bg-success {
  background-color: #339966 !important; /* Original green color */
  color: #ffffff !important; /* White text */
}

[data-theme="dark"] .badge.bg-warning {
  background-color: #ffc107 !important; /* Original yellow/amber color */
  color: #000000 !important; /* Dark text on bright background */
}

[data-theme="dark"] .badge.bg-danger {
  background-color: #990000 !important; /* Original red color */
  color: #ffffff !important; /* White text */
}

/* ==========================================================
   Table - Professional
   ========================================================== */

.table {
  margin-bottom: 0;
  color: var(--wiki-dark);
  width: 100%;
  border-collapse: separate;
  border-spacing: 0;
}

.table thead th {
  background-color: var(--wiki-light-bg);
  border-bottom: 2px solid var(--wiki-border);
  font-weight: 600;
  text-transform: uppercase;
  font-size: 0.85rem;
  letter-spacing: 0.5px;
  color: var(--wiki-text-muted);
  padding: 1rem;
  position: sticky;
  top: 0;
  z-index: 10;
}

[data-theme="dark"] .table thead th {
  background-color: rgba(93, 184, 230, 0.1);
  border-bottom-color: var(--wiki-border);
  color: #ffffff !important; /* White text for table headers */
}

.table tbody td {
  padding: 1rem;
  vertical-align: middle;
  border-bottom: 1px solid var(--wiki-border);
  background-color: var(--wiki-card-bg);
}

[data-theme="dark"] .table tbody td {
  background-color: var(--wiki-card-bg);
  color: #ffffff !important; /* White text for better visibility */
}

/* Ensure table text is visible in dark mode */
[data-theme="dark"] .table tbody td strong {
  color: #ffffff !important; /* White text for contest names */
}

/* Ensure all table cell text is visible */
[data-theme="dark"] .table tbody td span {
  color: #ffffff !important; /* White text for all spans in table cells */
}

.table tbody tr {
  transition: all 0.2s ease;
  background-color: var(--wiki-card-bg);
}

.table-row-clickable {
  cursor: pointer;
}

.table-row-clickable:hover {
  background-color: var(--wiki-hover-bg);
}

.table-row-clickable:hover td {
  background-color: var(--wiki-hover-bg);
}

.table tbody tr:last-child td {
  border-bottom: none;
}

/* Table responsive wrapper */
.table-responsive {
  border-radius: 4px;
  overflow: hidden;
}

/* Table buttons */
.table .btn-sm {
  padding: 0.25rem 0.75rem;
  font-size: 0.875rem;
  border-radius: 4px;
}

.table .btn-outline-primary {
  border-color: var(--wiki-primary);
  color: var(--wiki-primary);
  transition: all 0.2s ease;
}

.table .btn-outline-primary:hover {
  background-color: var(--wiki-primary);
  border-color: var(--wiki-primary);
  color: white;
  transform: translateY(-1px);
  box-shadow: 0 2px 4px rgba(0, 102, 153, 0.2);
}

/* Ensure button colors are visible in dark mode - maintain original colors */
[data-theme="dark"] .table .btn-outline-primary {
  border-color: #006699 !important; /* Original blue color */
  color: #006699 !important; /* Original blue color */
}

[data-theme="dark"] .table .btn-outline-primary:hover {
  background-color: #006699 !important; /* Original blue color */
  border-color: #006699 !important; /* Original blue color */
  color: white !important;
}

/* ==========================================================
   Spinner - Professional
   ========================================================== */

.spinner-border.text-primary {
  width: 3rem;
  height: 3rem;
  border-width: 0.25em;
  color: var(--wiki-primary);
}

/* ==========================================================
   Responsive Design
   ========================================================== */

/* Ensure text-muted elements are visible in dark mode */
[data-theme="dark"] .text-muted {
  color: #b8b8b8 !important; /* Light gray for muted text in dark mode */
}

[data-theme="dark"] .no-submissions,
[data-theme="dark"] .no-scores,
[data-theme="dark"] .no-contests {
  color: #b8b8b8 !important; /* Light gray for empty state messages */
}

@media(max-width: 768px){
  h2.page-header {
    font-size: 1.75rem;
  }

  h4 {
    font-size: 1.125rem;
  }

  .card-body {
    padding: 1.25rem;
  }

  h2.text-primary,
  h2.text-success,
  h2.text-warning {
    font-size: 2rem !important;
  }

  .submission-item {
    flex-direction: column;
    align-items: flex-start !important;
  }

  .submission-item > div {
    margin-top: 0.5rem;
    width: 100%;
    justify-content: space-between;
  }
}

</style>
