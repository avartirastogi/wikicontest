<template>
  <div class="container py-5">
    <!-- Back button -->
    <div class="mb-4">
      <button
        class="btn btn-outline-secondary"
        @click="goBack"
      >
        <i class="fas fa-arrow-left me-2"></i>Back to Contests
      </button>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="alert alert-danger">
      <i class="fas fa-exclamation-circle me-2"></i>{{ error }}
      <button class="btn btn-sm btn-outline-danger ms-3" @click="goBack">Go Back</button>
    </div>

    <!-- Contest Details -->
    <div v-else-if="contest" class="contest-view">
      <!-- Header Section -->
      <div class="contest-header-section mb-4">
        <h1 class="contest-title">{{ contest.name }}</h1>
        <div class="contest-meta">
          <span class="badge bg-primary me-2">{{ getStatusLabel(contest.status) }}</span>
          <span class="text-muted">
            <i class="fas fa-calendar-alt me-1"></i>
            Created {{ formatDate(contest.created_at) }}
          </span>
        </div>
      </div>

      <!-- Main Content -->
      <div class="row">
        <!-- Contest Details Column -->
        <div :class="canViewSubmissions ? 'col-md-6' : 'col-md-12'">
          <div class="card mb-4">
            <div class="card-header">
              <h5 class="mb-0"><i class="fas fa-info-circle me-2"></i>Contest Details</h5>
            </div>
            <div class="card-body">
              <p><strong>Project:</strong> {{ contest.project_name }}</p>
              <p><strong>Created by:</strong> {{ contest.created_by }}</p>
              <p><strong>Status:</strong> <span class="badge bg-primary">{{ contest.status }}</span></p>
              <p v-if="contest.start_date"><strong>Start Date:</strong> {{ formatDate(contest.start_date) }}</p>
              <p v-if="contest.end_date"><strong>End Date:</strong> {{ formatDate(contest.end_date) }}</p>
            </div>
          </div>
        </div>

        <!-- Scoring Column (for jury and contest creators) -->
        <div v-if="canViewSubmissions" class="col-md-6">
          <div class="card mb-4">
            <div class="card-header">
              <h5 class="mb-0"><i class="fas fa-chart-line me-2"></i>Scoring</h5>
            </div>
            <div class="card-body">
              <p><strong>Accepted:</strong> {{ contest.marks_setting_accepted }} points</p>
              <p><strong>Rejected:</strong> {{ contest.marks_setting_rejected }} points</p>
              <p><strong>Submissions:</strong> {{ contest.submission_count }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Description Section -->
      <div v-if="contest.description" class="card mb-4 description-section">
        <div class="card-header">
          <h5 class="mb-0"><i class="fas fa-align-left me-2"></i>Description</h5>
        </div>
        <div class="card-body">
          <p class="description-text">{{ contest.description }}</p>
        </div>
      </div>

      <!-- Jury Members Section -->
      <div v-if="contest.jury_members && contest.jury_members.length > 0" class="card mb-4">
        <div class="card-header">
          <h5 class="mb-0"><i class="fas fa-users me-2"></i>Jury Members</h5>
        </div>
        <div class="card-body">
          <p>{{ contest.jury_members.join(', ') }}</p>
        </div>
      </div>

      <!-- Submissions Section (for jury and contest creators) -->
      <div v-if="canViewSubmissions" class="card mb-4">
        <div class="card-header">
          <div class="d-flex justify-content-between align-items-center">
            <h5 class="mb-0"><i class="fas fa-file-alt me-2"></i>Submissions</h5>
            <button
              v-if="loadingSubmissions || refreshingMetadata"
              class="btn btn-sm btn-outline-secondary"
              disabled
            >
              <span class="spinner-border spinner-border-sm me-2"></span>{{ loadingSubmissions ? 'Loading...' : 'Refreshing...' }}
            </button>
            <button
              v-else
              class="btn btn-sm btn-outline-light"
              @click="refreshMetadata"
              :disabled="submissions.length === 0"
              title="Refresh article metadata (word count, author, etc.) from MediaWiki and reload submissions"
              style="color: white; border-color: white;"
            >
              <i class="fas fa-database me-1"></i>Refresh Metadata
            </button>
          </div>
        </div>
        <div class="card-body">
          <div v-if="submissions.length === 0 && !loadingSubmissions" class="alert alert-info">
            <i class="fas fa-info-circle me-2"></i>No submissions yet for this contest.
          </div>

          <div v-else-if="submissions.length > 0" class="table-responsive">
            <table class="table table-sm table-hover">
              <thead>
                <tr>
                  <th>Article Title</th>
                  <th>Article Author</th>
                  <th>Submitted By</th>
                  <th>Status</th>
                  <th>Score</th>
                  <th>Submitted At</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                  <tr v-for="submission in submissions" :key="submission.id">
                  <td>
                    <a
                      href="#"
                      @click.prevent="showArticlePreview(submission.article_link, submission.article_title)"
                      class="text-decoration-none article-title-link"
                      :title="submission.article_link"
                    >
                      {{ submission.article_title }}
                      <i class="fas fa-eye ms-1" style="font-size: 0.8em;"></i>
                    </a>
                    <div
                      v-if="submission.article_word_count && submission.article_word_count > 0"
                      class="text-muted small mt-1"
                    >
                      <i class="fas fa-file-alt me-1"></i>{{ formatWordCount(submission.article_word_count) }}
                    </div>
                    <div v-else-if="submission.article_word_count === 0" class="text-muted small mt-1">
                      <i class="fas fa-file-alt me-1"></i>Size: 0 bytes
                    </div>
                  </td>
                  <td>
                    <div v-if="submission.article_author">
                      <i class="fas fa-user me-1"></i>{{ submission.article_author }}
                    </div>
                    <div v-else class="text-muted small">Unknown</div>
                    <div v-if="submission.article_created_at" class="text-muted small mt-1">
                      <i class="fas fa-calendar me-1"></i>{{ formatDateShort(submission.article_created_at) }}
                    </div>
                  </td>
                  <td>{{ submission.username || 'Unknown' }}</td>
                  <td>
                    <span :class="`badge bg-${getStatusColor(submission.status)}`">
                      {{ submission.status }}
                    </span>
                  </td>
                  <td>{{ submission.score || 0 }}</td>
                  <td>{{ formatDate(submission.submitted_at) }}</td>
                  <td>
                    <button
                      @click="showArticlePreview(submission.article_link, submission.article_title)"
                      class="btn btn-sm btn-outline-primary"
                      title="Preview Article"
                    >
                      <i class="fas fa-eye"></i>
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- Action Buttons -->
      <div class="d-flex gap-2 mb-4">
        <!-- Debug info and auth status -->
        <div v-if="contest && !currentUser && !checkingAuth" class="alert alert-warning py-1 px-2 mb-0 me-auto">
          <i class="fas fa-exclamation-triangle me-1"></i>
          <strong>User not loaded!</strong>
          <button class="btn btn-sm btn-outline-warning ms-2" @click="forceAuthRefresh">
            <i class="fas fa-sync-alt me-1"></i>Refresh Auth
          </button>
        </div>

        <button
          v-if="canDeleteContest"
          class="btn btn-danger"
          @click="handleDeleteContest"
          :disabled="deletingContest"
        >
          <span v-if="deletingContest" class="spinner-border spinner-border-sm me-2"></span>
          <i v-else class="fas fa-trash me-2"></i>
          {{ deletingContest ? 'Deleting...' : 'Delete Contest' }}
        </button>
        <button
          v-if="contest?.status === 'current' && isAuthenticated && !canViewSubmissions"
          class="btn btn-primary"
          @click="handleSubmitArticle"
        >
          <i class="fas fa-paper-plane me-2"></i>Submit Article
        </button>
      </div>
    </div>

    <!-- Submit Article Modal -->
    <SubmitArticleModal
      v-if="submittingToContestId"
      :contest-id="submittingToContestId"
      @submitted="handleArticleSubmitted"
    />

    <!-- Article Preview Modal -->
    <ArticlePreviewModal
      :article-url="previewArticleUrl"
      :article-title="previewArticleTitle"
    />
  </div>
</template>

<script>
import { computed, ref, watch, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useStore } from '../store'
import api from '../services/api'
import { showAlert } from '../utils/alerts'
import SubmitArticleModal from '../components/SubmitArticleModal.vue'
import ArticlePreviewModal from '../components/ArticlePreviewModal.vue'

export default {
  name: 'ContestView',
  components: {
    SubmitArticleModal,
    ArticlePreviewModal
  },
  setup() {
    const router = useRouter()
    const route = useRoute()
    const store = useStore()

    // State
    const contest = ref(null)
    const loading = ref(true)
    const error = ref(null)
    const submissions = ref([])
    const loadingSubmissions = ref(false)
    const refreshingMetadata = ref(false)
    const deletingContest = ref(false)
    const canDeleteContest = ref(false)
    const checkingAuth = ref(false)
    const submittingToContestId = ref(null)
    const previewArticleUrl = ref('')
    const previewArticleTitle = ref('')

    // Get reactive references to auth state
    const currentUser = computed(() => {
      if (store.state && store.state.currentUser) {
        return store.state.currentUser
      }
      if (store.currentUser) {
        return store.currentUser
      }
      return null
    })

    const isAuthenticated = computed(() => {
      const user = currentUser.value
      return !!user && !!user.id && !!user.username
    })

    // Check if user can view submissions (jury member or contest creator)
    const canViewSubmissions = computed(() => {
      if (!isAuthenticated.value || !contest.value || !currentUser.value) {
        return false
      }

      const username = (currentUser.value.username || '').trim().toLowerCase()
      const contestData = contest.value

      // Check if user is contest creator (case-insensitive)
      const contestCreator = (contestData.created_by || '').trim().toLowerCase()
      if (contestCreator && username === contestCreator) {
        return true
      }

      // Check if user is jury member (case-insensitive)
      if (contestData.jury_members && Array.isArray(contestData.jury_members)) {
        const juryUsernames = contestData.jury_members.map(j => (j || '').trim().toLowerCase())
        return juryUsernames.includes(username)
      }

      return false
    })

    // Check if user can delete contest
    const checkDeletePermission = () => {
      canDeleteContest.value = false

      const userFromComputed = currentUser.value
      const userFromStore = store.currentUser
      const userFromState = (store.state && store.state.currentUser) || null
      const userToCheck = userFromComputed || userFromStore || userFromState

      if (!isAuthenticated.value || !contest.value || !userToCheck) {
        canDeleteContest.value = false
        return
      }

      const username = (userToCheck.username || '').trim()
      const contestCreator = (contest.value.created_by || '').trim()

      if (!username || !contestCreator) {
        canDeleteContest.value = false
        return
      }

      const usernameLower = username.toLowerCase()
      const creatorLower = contestCreator.toLowerCase()
      canDeleteContest.value = usernameLower === creatorLower
    }

    // Format date for display in Indian Standard Time (IST)
    // Converts UTC dates from backend to IST timezone for display
    const formatDate = (dateString) => {
      if (!dateString) return 'No date'
      try {
        // Ensure the date string is treated as UTC
        // If it doesn't end with 'Z', append it to indicate UTC timezone
        // This fixes the issue where naive UTC datetimes were being interpreted as local time
        let utcDateString = dateString
        if (!dateString.endsWith('Z') && !dateString.includes('+') && !dateString.includes('-', 10)) {
          // If no timezone indicator, assume it's UTC and append 'Z'
          utcDateString = dateString + 'Z'
        }
        
        // Convert to IST (Indian Standard Time) timezone
        // IST is UTC+5:30, timezone identifier is 'Asia/Kolkata'
        return new Date(utcDateString).toLocaleString('en-IN', {
          timeZone: 'Asia/Kolkata',
          year: 'numeric',
          month: 'long',
          day: 'numeric',
          hour: '2-digit',
          minute: '2-digit',
          hour12: true
        })
      } catch (e) {
        return dateString
      }
    }

    // Format date with full date and time in IST (for article creation date)
    // Shows complete date and time information including time in IST timezone
    const formatDateShort = (dateString) => {
      if (!dateString) return ''
      try {
        // Ensure the date string is treated as UTC
        // If it doesn't end with 'Z', append it to indicate UTC timezone
        // This fixes the issue where naive UTC datetimes were being interpreted as local time
        let utcDateString = dateString
        if (!dateString.endsWith('Z') && !dateString.includes('+') && !dateString.includes('-', 10)) {
          // If no timezone indicator, assume it's UTC and append 'Z'
          utcDateString = dateString + 'Z'
        }
        
        // Convert to IST (Indian Standard Time) timezone
        // IST is UTC+5:30, timezone identifier is 'Asia/Kolkata'
        // Show full date and time with month name, day, year, hour, and minute
        return new Date(utcDateString).toLocaleString('en-IN', {
          timeZone: 'Asia/Kolkata',
          year: 'numeric',
          month: 'long',
          day: 'numeric',
          hour: '2-digit',
          minute: '2-digit',
          hour12: true
        })
      } catch (e) {
        return dateString
      }
    }

    // Format word count for display
    const formatWordCount = (count) => {
      if (!count) return ''
      if (count >= 1000) {
        return `${(count / 1000).toFixed(1)}k words`
      }
      return `${count} words`
    }

    // Get status label
    const getStatusLabel = (status) => {
      const labels = {
        current: 'Active',
        upcoming: 'Upcoming',
        past: 'Past',
        unknown: 'Unknown'
      }
      return labels[status] || 'Unknown'
    }

    // Get status badge color
    const getStatusColor = (status) => {
      switch (status?.toLowerCase()) {
        case 'accepted':
          return 'success'
        case 'rejected':
          return 'danger'
        case 'pending':
          return 'warning'
        default:
          return 'secondary'
      }
    }

    // Load contest data by name (slug)
    const loadContest = async () => {
      const contestName = route.params.name
      if (!contestName) {
        error.value = 'Contest name is required'
        loading.value = false
        return
      }

      loading.value = true
      error.value = null

      try {
        // Fetch contest by slugified name
        const data = await api.get(`/contest/name/${contestName}`)
        contest.value = data

        // Check auth and permissions after loading contest
        await checkAuthAndPermissions()

        // Load submissions if user can view them
        if (canViewSubmissions.value) {
          loadSubmissions()
        }
      } catch (err) {
        console.error('Error loading contest:', err)
        error.value = 'Failed to load contest: ' + (err.message || 'Unknown error')
      } finally {
        loading.value = false
      }
    }

    // Check auth and permissions
    const checkAuthAndPermissions = async () => {
      checkingAuth.value = true
      canDeleteContest.value = false

      try {
        // Check if user is already in the store
        let loadedUser = store.currentUser || (store.state && store.state.currentUser) || currentUser.value

        // If user is not in store, try to load it via checkAuth
        if (!loadedUser) {
          await store.checkAuth()
          await new Promise(resolve => setTimeout(resolve, 150))
          loadedUser = store.currentUser || (store.state && store.state.currentUser) || currentUser.value
        }

        // Wait for reactive state to propagate
        await new Promise(resolve => setTimeout(resolve, 100))

        // Check delete permission
        checkDeletePermission()
      } catch (error) {
        console.error('Failed to check auth:', error)
        canDeleteContest.value = false
      } finally {
        checkingAuth.value = false
      }
    }

    // Load submissions for the contest
    const loadSubmissions = async () => {
      if (!contest.value || !canViewSubmissions.value) {
        return
      }

      loadingSubmissions.value = true
      try {
        const data = await api.get(`/contest/${contest.value.id}/submissions`)
        submissions.value = data || []

        // Debug: Log submission data to verify author and word count are present
        console.log('Loaded submissions:', submissions.value)
        submissions.value.forEach((sub, index) => {
          console.log(`Submission ${index + 1}:`, {
            id: sub.id,
            title: sub.article_title,
            author: sub.article_author,
            word_count: sub.article_word_count,
            created_at: sub.article_created_at
          })
        })
      } catch (error) {
        console.error('Failed to load submissions:', error)
        showAlert('Failed to load submissions: ' + error.message, 'danger')
        submissions.value = []
      } finally {
        loadingSubmissions.value = false
      }
    }

    // Refresh article metadata for all submissions in the contest
    const refreshMetadata = async () => {
      if (!contest.value || !canViewSubmissions.value || submissions.value.length === 0) {
        return
      }

      refreshingMetadata.value = true
      try {
        const response = await api.post(`/submission/contest/${contest.value.id}/refresh-metadata`)
        showAlert(
          `Metadata refreshed: ${response.updated} updated, ${response.failed} failed`,
          response.failed === 0 ? 'success' : 'warning'
        )
        
        // Reload submissions to show updated data
        await loadSubmissions()
      } catch (error) {
        console.error('Failed to refresh metadata:', error)
        showAlert('Failed to refresh metadata: ' + error.message, 'danger')
      } finally {
        refreshingMetadata.value = false
      }
    }

    // Handle delete contest
    const handleDeleteContest = async () => {
      if (!contest.value) return

      const confirmed = confirm(
        `Are you sure you want to delete the contest "${contest.value.name}"?\n\n` +
        'This action cannot be undone and will delete all associated submissions.'
      )

      if (!confirmed) return

      deletingContest.value = true
      try {
        await api.delete(`/contest/${contest.value.id}`)
        showAlert('Contest deleted successfully', 'success')

        // Navigate back to contests list
        router.push({ name: 'Contests' })
      } catch (error) {
        console.error('Failed to delete contest:', error)
        showAlert('Failed to delete contest: ' + error.message, 'danger')
      } finally {
        deletingContest.value = false
      }
    }

    // Handle submit article
    const handleSubmitArticle = () => {
      if (!store.isAuthenticated) {
        showAlert('Please login to submit an article', 'warning')
        return
      }
      submittingToContestId.value = contest.value.id

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
      // Reload contest to update submission count
      loadContest()
    }

    // Force auth refresh manually
    const forceAuthRefresh = async () => {
      checkingAuth.value = true
      try {
        await store.checkAuth()
        await new Promise(resolve => setTimeout(resolve, 200))
        checkDeletePermission()
      } catch (error) {
        console.error('Auth refresh failed:', error)
      } finally {
        checkingAuth.value = false
      }
    }

    // Go back to contests list
    const goBack = () => {
      router.push({ name: 'Contests' })
    }

    // Show article preview modal
    const showArticlePreview = (url, title) => {
      previewArticleUrl.value = url
      previewArticleTitle.value = title || 'Article'

      // Show modal using Bootstrap
      setTimeout(() => {
        const modalElement = document.getElementById('articlePreviewModal')
        if (modalElement) {
          const modal = new bootstrap.Modal(modalElement)
          modal.show()
        }
      }, 100)
    }

    // Watch for changes in currentUser to update delete permission
    watch(() => currentUser.value, (newUser) => {
      if (newUser && contest.value && !checkingAuth.value) {
        setTimeout(() => {
          checkDeletePermission()
        }, 50)
      } else if (!newUser && contest.value) {
        canDeleteContest.value = false
      }
    }, { deep: true })

    // Load contest on mount
    onMounted(() => {
      loadContest()
    })

    return {
      contest,
      loading,
      error,
      submissions,
      loadingSubmissions,
      deletingContest,
      canDeleteContest,
      checkingAuth,
      submittingToContestId,
      currentUser,
      isAuthenticated,
      canViewSubmissions,
      formatDate,
      formatDateShort,
      formatWordCount,
      getStatusLabel,
      getStatusColor,
      loadSubmissions,
      refreshMetadata,
      refreshingMetadata,
      handleDeleteContest,
      handleSubmitArticle,
      handleArticleSubmitted,
      forceAuthRefresh,
      goBack,
      showArticlePreview,
      previewArticleUrl,
      previewArticleTitle
    }
  }
}
</script>

<style scoped>
/* Contest View Styling with Wikipedia Colors */

.contest-view {
  max-width: 1200px;
  margin: 0 auto;
}

/* Header Section */
.contest-header-section {
  border-bottom: 2px solid var(--wiki-primary);
  padding-bottom: 1rem;
}

.contest-title {
  color: var(--wiki-dark);
  font-weight: 700;
  font-size: 2.5rem;
  margin-bottom: 0.5rem;
  transition: color 0.3s ease;
}

[data-theme="dark"] .contest-title {
  color: #ffffff !important;
}

.contest-meta {
  display: flex;
  align-items: center;
  gap: 1rem;
  flex-wrap: wrap;
}

/* Card Styling */
.card {
  border: 1px solid var(--wiki-border);
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  transition: box-shadow 0.2s ease;
}

[data-theme="dark"] .card {
  background-color: #2a2a2a;
  border-color: #444;
}

.card:hover {
  box-shadow: 0 4px 8px rgba(0, 102, 153, 0.15);
}

.card-header {
  background-color: var(--wiki-primary);
  color: white;
  border-bottom: none;
  padding: 1rem 1.5rem;
  font-weight: 600;
}

.card-body {
  padding: 1.5rem;
}

.card-body p {
  margin-bottom: 0.75rem;
  color: var(--wiki-text);
}

.card-body strong {
  color: var(--wiki-dark);
  font-weight: 600;
}

[data-theme="dark"] .card-body strong {
  color: #ffffff;
}

/* Badge Styling */
.badge {
  font-weight: 500;
  padding: 0.4em 0.8em;
  font-size: 0.85em;
}

.badge.bg-primary {
  background-color: var(--wiki-primary) !important;
}

/* Table Styling */
.table {
  margin-top: 0;
}

.table thead th {
  background-color: rgba(0, 102, 153, 0.1);
  color: var(--wiki-primary);
  font-weight: 600;
  border-bottom: 2px solid var(--wiki-primary);
  padding: 0.75rem;
}

[data-theme="dark"] .table thead th {
  background-color: rgba(93, 184, 230, 0.15);
  border-bottom-color: var(--wiki-primary);
}

.table tbody td {
  padding: 0.75rem;
  vertical-align: middle;
  color: var(--wiki-text);
}

.table tbody tr:hover {
  background-color: var(--wiki-hover-bg);
}

/* Link Styling */
.table a {
  color: var(--wiki-primary);
  font-weight: 500;
  transition: color 0.2s ease;
}

.table a:hover {
  color: var(--wiki-primary-hover);
  text-decoration: underline;
}

/* Article title link - clickable for preview */
.article-title-link {
  cursor: pointer;
  color: var(--wiki-primary);
  font-weight: 500;
  transition: color 0.2s ease;
}

.article-title-link:hover {
  color: var(--wiki-primary-hover);
  text-decoration: underline;
}

/* Button Styling */
.btn-outline-primary {
  border-color: var(--wiki-primary);
  color: var(--wiki-primary);
  transition: all 0.2s ease;
}

.btn-outline-primary:hover {
  background-color: var(--wiki-primary);
  border-color: var(--wiki-primary);
  color: white;
  transform: translateY(-1px);
  box-shadow: 0 2px 4px rgba(0, 102, 153, 0.3);
}

.btn-primary {
  background-color: var(--wiki-primary);
  border-color: var(--wiki-primary);
  transition: all 0.2s ease;
}

.btn-primary:hover {
  background-color: var(--wiki-primary-hover);
  border-color: var(--wiki-primary-hover);
  transform: translateY(-1px);
  box-shadow: 0 2px 4px rgba(0, 102, 153, 0.3);
}

.btn-danger {
  background-color: var(--wiki-danger);
  border-color: var(--wiki-danger);
  color: white;
  transition: all 0.2s ease;
}

.btn-danger:hover {
  background-color: var(--wiki-danger-hover);
  border-color: var(--wiki-danger-hover);
  color: white;
  box-shadow: 0 2px 4px rgba(153, 0, 0, 0.2);
}

[data-theme="dark"] .btn-danger {
  background-color: #990000;
  border-color: #990000;
}

[data-theme="dark"] .btn-danger:hover {
  background-color: #7a0000;
  border-color: #7a0000;
}

.btn-outline-secondary {
  border-color: var(--wiki-text-muted);
  color: var(--wiki-text-muted);
  transition: all 0.2s ease;
}

.btn-outline-secondary:hover {
  background-color: var(--wiki-text-muted);
  border-color: var(--wiki-text-muted);
  color: white;
}

/* Alert Styling */
.alert {
  border-radius: 0.5rem;
  border-left: 4px solid;
  padding: 0.75rem 1rem;
}

.alert-info {
  background-color: rgba(0, 102, 153, 0.1);
  border-color: var(--wiki-primary);
  color: var(--wiki-primary);
}

[data-theme="dark"] .alert-info {
  background-color: rgba(93, 184, 230, 0.2);
  border-color: var(--wiki-primary);
  color: var(--wiki-primary);
}

.alert-danger {
  background-color: rgba(153, 0, 0, 0.1);
  border-color: var(--wiki-danger);
  color: var(--wiki-danger);
}

.alert-warning {
  background-color: rgba(153, 0, 0, 0.1);
  border-color: var(--wiki-danger);
  color: var(--wiki-danger);
}

/* Spinner */
.spinner-border.text-primary {
  color: var(--wiki-primary) !important;
  width: 3rem;
  height: 3rem;
  border-width: 0.3em;
}

/* Description section - preserve formatting and line breaks */
.description-section {
  margin-top: 0;
}

.description-text {
  white-space: pre-line; /* Preserves line breaks and wraps text */
  line-height: 1.6;
  margin-bottom: 0;
  color: var(--wiki-text);
  word-wrap: break-word; /* Break long words if needed */
  transition: color 0.3s ease;
}

[data-theme="dark"] .description-text {
  color: var(--wiki-text);
}

/* Responsive */
@media (max-width: 768px) {
  .contest-title {
    font-size: 2rem;
  }

  .card-body {
    padding: 1rem;
  }

  .table {
    font-size: 0.9rem;
  }

  .table thead th,
  .table tbody td {
    padding: 0.5rem;
  }
}
</style>

