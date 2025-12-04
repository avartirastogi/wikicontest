<template>
  <div class="container py-5">
    <div class="d-flex flex-column flex-sm-row justify-content-between align-items-start align-items-sm-center mb-4">
      <h2 class="mb-3 mb-sm-0">Contests</h2>
      <button 
        v-if="isAuthenticated"
        class="btn btn-primary" 
        @click="showCreateContestModal"
      >
        <i class="fas fa-plus me-2"></i>Create Contest
      </button>
    </div>
    
    <!-- Contest Categories Tabs -->
    <ul class="nav nav-tabs mb-4" id="contestTabs">
      <li class="nav-item">
        <button 
          class="nav-link" 
          :class="{ active: activeCategory === 'current' }"
          @click="setActiveCategory('current')"
        >
          Current
        </button>
      </li>
      <li class="nav-item">
        <button 
          class="nav-link" 
          :class="{ active: activeCategory === 'upcoming' }"
          @click="setActiveCategory('upcoming')"
        >
          Upcoming
        </button>
      </li>
      <li class="nav-item">
        <button 
          class="nav-link" 
          :class="{ active: activeCategory === 'past' }"
          @click="setActiveCategory('past')"
        >
          Past
        </button>
      </li>
    </ul>
    
    <!-- Loading State -->
    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
    </div>

    <!-- Contest List -->
    <div v-else id="contestList">
      <div v-if="currentContests.length === 0" class="alert alert-info text-center">
        <i class="fas fa-info-circle me-2"></i>
        No {{ activeCategory }} contests available.
      </div>
      <div v-else class="contest-list">
        <div 
          v-for="contest in currentContests" 
          :key="contest.id"
          class="contest-item"
          @click="viewContest(contest.id)"
        >
          <!-- Contest Card Layout -->
          <div class="contest-card">
            <!-- Header Row: Title and Timestamp -->
            <div class="contest-header">
              <div class="contest-title-section">
                <span 
                  class="contest-title-link"
                  @click.stop="viewContest(contest.id)"
                >
                  {{ contest.name }}
                </span>
              </div>
              <div class="contest-timestamp">
                {{ formatDate(contest.created_at) }}
              </div>
            </div>

            <!-- Tags Row: Status, Project, Submissions, Creator -->
            <div class="contest-tags">
              <!-- Status Badge -->
              <span 
                class="contest-tag status-tag"
                :class="getStatusClass(contest.status)"
              >
                <i :class="getStatusIcon(contest.status)"></i>
                {{ getStatusLabel(contest.status) }}
              </span>

              <!-- Project Tag -->
              <span class="contest-tag project-tag">
                <i class="fas fa-briefcase"></i>
                {{ contest.project_name }}
              </span>

              <!-- Submissions Count Badge -->
              <span class="contest-tag submissions-tag">
                <i class="fas fa-file-alt"></i>
                {{ contest.submission_count || 0 }} {{ contest.submission_count === 1 ? 'submission' : 'submissions' }}
              </span>

              <!-- Creator Tag -->
              <span class="contest-tag creator-tag">
                <i class="fas fa-user"></i>
                {{ contest.created_by }}
              </span>

              <!-- Date Range Tag (if dates available) -->
              <span v-if="contest.start_date || contest.end_date" class="contest-tag date-tag">
                <i class="fas fa-calendar-alt"></i>
                {{ formatDateRange(contest.start_date, contest.end_date) }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Contest Details Modal -->
    <!-- Always render modal so Bootstrap can find it, but pass null when no contest selected -->
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

    <!-- Create Contest Modal -->
    <CreateContestModal
      ref="createContestModal"
      @created="handleContestCreated"
    />
  </div>
</template>

<script>
import { ref, computed, onMounted, nextTick } from 'vue'
import { useStore } from '../store'
import { showAlert } from '../utils/alerts'
import api from '../services/api'
import CreateContestModal from '../components/CreateContestModal.vue'
import ContestModal from '../components/ContestModal.vue'
import SubmitArticleModal from '../components/SubmitArticleModal.vue'

export default {
  name: 'Contests',
  components: {
    CreateContestModal,
    ContestModal,
    SubmitArticleModal
  },
  setup() {
    const store = useStore()
    const activeCategory = ref('current')
    const loading = ref(false)
    const selectedContest = ref(null)
    const submittingToContestId = ref(null)
    const createContestModal = ref(null)

    // Computed property for current contests
    const currentContests = computed(() => {
      return store.getContestsByCategory(activeCategory.value)
    })

    const isAuthenticated = computed(() => store.isAuthenticated)

    // Set active category
    const setActiveCategory = (category) => {
      activeCategory.value = category
    }

    // Truncate text helper
    const truncateText = (text, maxLength) => {
      if (!text) return ''
      if (text.length <= maxLength) return text
      return text.substring(0, maxLength) + '...'
    }

    // Format date for display
    const formatDate = (dateString) => {
      if (!dateString) return ''
      try {
        const date = new Date(dateString)
        return date.toLocaleDateString('en-US', { 
          weekday: 'short', 
          month: 'short', 
          day: 'numeric',
          hour: 'numeric',
          minute: '2-digit'
        })
      } catch (e) {
        return dateString
      }
    }

    // Format date range
    const formatDateRange = (startDate, endDate) => {
      if (!startDate && !endDate) return ''
      
      const format = (dateStr) => {
        if (!dateStr) return ''
        try {
          const date = new Date(dateStr)
          return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
        } catch (e) {
          return dateStr
        }
      }

      if (startDate && endDate) {
        return `${format(startDate)} - ${format(endDate)}`
      } else if (startDate) {
        return `Starts: ${format(startDate)}`
      } else if (endDate) {
        return `Ends: ${format(endDate)}`
      }
      return ''
    }

    // Get status label
    const getStatusLabel = (status) => {
      const labels = {
        'current': 'Active',
        'upcoming': 'Upcoming',
        'past': 'Past',
        'unknown': 'Unknown'
      }
      return labels[status] || 'Unknown'
    }

    // Get status CSS class
    const getStatusClass = (status) => {
      const classes = {
        'current': 'status-active',
        'upcoming': 'status-upcoming',
        'past': 'status-past',
        'unknown': 'status-unknown'
      }
      return classes[status] || 'status-unknown'
    }

    // Get status icon
    const getStatusIcon = (status) => {
      const icons = {
        'current': 'fas fa-circle',
        'upcoming': 'fas fa-clock',
        'past': 'fas fa-check-circle',
        'unknown': 'fas fa-question-circle'
      }
      return icons[status] || 'fas fa-question-circle'
    }

    // View contest details
    const viewContest = async (contestId) => {
      try {
        const contest = await api.get(`/contest/${contestId}`)
        selectedContest.value = contest
        
        // Wait for Vue to render the modal component
        // Use nextTick to ensure DOM is updated
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
          console.log('Modal shown for contest:', contest.name)
        } else {
          console.error('Modal element not found! Contest:', contest)
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

    // Show create contest modal
    const showCreateContestModal = () => {
      if (!store.isAuthenticated) {
        showAlert('Please login to create a contest', 'warning')
        return
      }
      
      // Show modal using Bootstrap
      const modalElement = document.getElementById('createContestModal')
      if (modalElement) {
        const modal = new bootstrap.Modal(modalElement)
        modal.show()
      }
    }

    // Handle contest created
    const handleContestCreated = () => {
      // Contests will be reloaded automatically by store
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
      // Reload contests to update submission counts
      store.loadContests()
    }

    // Handle contest deleted
    const handleContestDeleted = () => {
      selectedContest.value = null
      // Reload contests to remove deleted contest
      store.loadContests()
    }

    // Load contests on mount
    onMounted(async () => {
      loading.value = true
      try {
        await store.loadContests()
      } catch (error) {
        showAlert('Failed to load contests: ' + error.message, 'danger')
      } finally {
        loading.value = false
      }
    })

    return {
      activeCategory,
      currentContests,
      loading,
      isAuthenticated,
      selectedContest,
      submittingToContestId,
      createContestModal,
      setActiveCategory,
      truncateText,
      formatDate,
      formatDateRange,
      getStatusLabel,
      getStatusClass,
      getStatusIcon,
      viewContest,
      showCreateContestModal,
      handleContestCreated,
      handleSubmitArticle,
      handleArticleSubmitted,
      handleContestDeleted
    }
  }
}
</script>

<style scoped>
/* Contests Page Styling with Wikipedia Colors */

/* Page header */
h2 {
  color: var(--wiki-dark);
  font-weight: 700;
  margin-bottom: 1.5rem;
  transition: color 0.3s ease;
}

/* Ensure page header is visible in dark mode */
[data-theme="dark"] h2 {
  color: #ffffff !important; /* White text for page header in dark mode */
}

/* Create contest button - professional */
.btn-primary {
  background-color: var(--wiki-primary);
  border-color: var(--wiki-primary);
  font-weight: 500;
  transition: all 0.2s ease;
  white-space: nowrap;
  padding: 0.5rem 1rem;
  border-radius: 4px;
}

.btn-primary:hover {
  background-color: var(--wiki-primary-hover);
  border-color: var(--wiki-primary-hover);
  box-shadow: 0 2px 4px rgba(0, 102, 153, 0.2);
}

/* Nav tabs - Wikipedia style - reduced line thickness */
.nav-tabs {
  border-bottom: 1px solid var(--wiki-border);
  margin-bottom: 2rem;
  transition: border-color 0.3s ease;
}

.nav-tabs .nav-link {
  color: var(--wiki-dark);
  border: none;
  border-bottom: 3px solid transparent;
  padding: 0.75rem 1.5rem;
  font-weight: 500;
  transition: all 0.2s ease;
  margin-right: 0.5rem;
}

/* Ensure nav links are visible in dark mode */
[data-theme="dark"] .nav-tabs .nav-link {
  color: #ffffff !important; /* White text for nav links in dark mode */
}

[data-theme="dark"] .nav-tabs .nav-link:hover {
  color: var(--wiki-primary) !important; /* Keep blue on hover */
}

[data-theme="dark"] .nav-tabs .nav-link.active {
  color: var(--wiki-primary) !important; /* Keep blue for active tab */
}

.nav-tabs .nav-link:hover {
  color: var(--wiki-primary);
  border-bottom-color: var(--wiki-primary);
  background-color: var(--wiki-hover-bg);
  border-radius: 0.5rem 0.5rem 0 0;
}

.nav-tabs .nav-link.active {
  color: var(--wiki-primary);
  background-color: transparent;
  border-bottom-color: var(--wiki-primary);
  border-bottom-width: 2px;
  font-weight: 600;
}

/* Contest list - enhanced card-based design */
.contest-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.contest-item {
  margin-bottom: 1rem;
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.contest-item:hover {
  transform: translateY(-2px);
}

/* Contest card container */
.contest-card {
  background-color: #ffffff;
  border: 1px solid var(--wiki-border);
  border-radius: 8px;
  padding: 1.25rem;
  transition: all 0.2s ease;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.contest-item:hover .contest-card {
  box-shadow: 0 4px 12px rgba(0, 102, 153, 0.15);
  border-color: var(--wiki-primary);
}

/* Dark mode card styling */
[data-theme="dark"] .contest-card {
  background-color: #2a2a2a;
  border-color: #444;
}

[data-theme="dark"] .contest-item:hover .contest-card {
  border-color: var(--wiki-primary);
  box-shadow: 0 4px 12px rgba(77, 166, 204, 0.2);
}

/* Contest header: ID, title, and timestamp */
.contest-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 0.75rem;
  gap: 1rem;
}

.contest-title-section {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex: 1;
}

.contest-id {
  font-weight: 700;
  color: var(--wiki-dark);
  font-size: 0.95rem;
  min-width: fit-content;
}

[data-theme="dark"] .contest-id {
  color: #ffffff;
}

/* Contest title - clickable link - larger size */
.contest-title-link {
  color: var(--wiki-primary);
  font-size: 1.4rem;
  font-weight: 600;
  cursor: pointer;
  text-decoration: none;
  transition: color 0.2s ease;
  flex: 1;
}

.contest-title-link:hover {
  color: var(--wiki-primary-hover);
  text-decoration: underline;
}

/* Dark mode title - white color for better visibility */
[data-theme="dark"] .contest-title-link {
  color: #ffffff !important; /* White text for better visibility in dark mode */
}

[data-theme="dark"] .contest-title-link:hover {
  color: #ffffff !important; /* Keep white on hover for consistency */
  text-decoration: underline;
}

/* Timestamp */
.contest-timestamp {
  color: #666;
  font-size: 0.875rem;
  white-space: nowrap;
  min-width: fit-content;
}

[data-theme="dark"] .contest-timestamp {
  color: #aaa;
}

/* Tags container */
.contest-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  align-items: center;
}

/* Base tag styling - smaller size */
.contest-tag {
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 500;
  white-space: nowrap;
  transition: all 0.2s ease;
}

.contest-tag i {
  font-size: 0.65rem;
}

/* Status tags with different colors - professional light backgrounds */
.status-tag {
  background-color: #f5f5f5;
  color: #424242;
  border: 1px solid #e0e0e0;
}

.status-active {
  background-color: #e8f5e9;
  color: #2e7d32;
  border: 1px solid #c8e6c9;
}

.status-upcoming {
  background-color: #fff9e6;
  color: #f57c00;
  border: 1px solid #ffe0b2;
}

.status-past {
  background-color: #f3e5f5;
  color: #7b1fa2;
  border: 1px solid #ce93d8;
}

.status-unknown {
  background-color: #fafafa;
  color: #616161;
  border: 1px solid #e0e0e0;
}

/* Dark mode status tags - maintain original colors with better visibility */
[data-theme="dark"] .status-tag {
  background-color: #f5f5f5 !important; /* Original light gray background */
  color: #424242 !important; /* Original dark gray text */
  border-color: #e0e0e0 !important; /* Original border color */
}

[data-theme="dark"] .status-active {
  background-color: #e8f5e9 !important; /* Original light green background */
  color: #2e7d32 !important; /* Original dark green text */
  border-color: #c8e6c9 !important; /* Original border color */
}

[data-theme="dark"] .status-upcoming {
  background-color: #fff9e6 !important; /* Original light yellow background */
  color: #f57c00 !important; /* Original orange text */
  border-color: #ffe0b2 !important; /* Original border color */
}

[data-theme="dark"] .status-past {
  background-color: #f3e5f5 !important; /* Original light purple background */
  color: #7b1fa2 !important; /* Original purple text */
  border-color: #ce93d8 !important; /* Original border color */
}

/* Project tag - professional light background */
.project-tag {
  background-color: #e3f2fd;
  color: #1565c0;
  border: 1px solid #90caf9;
}

[data-theme="dark"] .project-tag {
  background-color: #e3f2fd !important; /* Original light blue background */
  color: #1565c0 !important; /* Original dark blue text */
  border-color: #90caf9 !important; /* Original border color */
}

/* Submissions tag - professional light background */
.submissions-tag {
  background-color: #e8f5e9;
  color: #2e7d32;
  border: 1px solid #a5d6a7;
}

[data-theme="dark"] .submissions-tag {
  background-color: #e8f5e9 !important; /* Original light green background */
  color: #2e7d32 !important; /* Original dark green text */
  border-color: #a5d6a7 !important; /* Original border color */
}

/* Creator tag - professional light background */
.creator-tag {
  background-color: #f3e5f5;
  color: #7b1fa2;
  border: 1px solid #ce93d8;
}

[data-theme="dark"] .creator-tag {
  background-color: #f3e5f5 !important; /* Original light purple background */
  color: #7b1fa2 !important; /* Original purple text */
  border-color: #ce93d8 !important; /* Original border color */
}

/* Date tag - professional light background */
.date-tag {
  background-color: #fff3e0;
  color: #e65100;
  border: 1px solid #ffcc80;
  font-weight: 500;
}

[data-theme="dark"] .date-tag {
  background-color: #fff3e0 !important; /* Original light orange background */
  color: #e65100 !important; /* Original dark orange text */
  border-color: #ffcc80 !important; /* Original border color */
}


/* Status badge - professional */
.status-badge {
  background-color: var(--wiki-primary) !important;
  color: white;
  font-weight: 500;
  padding: 0.35em 0.7em;
  border-radius: 4px;
  font-size: 0.85rem;
}

/* View details button */
.btn-outline-primary {
  border-color: var(--wiki-primary);
  color: var(--wiki-primary);
  font-weight: 500;
  transition: all 0.2s ease;
}

.btn-outline-primary:hover {
  background-color: var(--wiki-primary);
  border-color: var(--wiki-primary);
  color: white;
  transform: translateY(-1px);
  box-shadow: 0 2px 4px rgba(0, 102, 153, 0.3);
}

/* Alert styling */
.alert-info {
  background-color: rgba(0, 102, 153, 0.1);
  border: 1px solid var(--wiki-primary);
  border-left: 4px solid var(--wiki-primary);
  color: var(--wiki-primary);
  border-radius: 0.5rem;
  padding: 1rem;
}

/* Dark mode - use white text for better visibility */
[data-theme="dark"] .alert-info {
  background-color: rgba(77, 166, 204, 0.15);
  color: #ffffff; /* White text for better visibility in dark mode */
}

.alert-info i {
  color: var(--wiki-primary);
}

/* Dark mode - white icon for better visibility */
[data-theme="dark"] .alert-info i {
  color: #ffffff; /* White icon for better visibility in dark mode */
}

/* Loading spinner */
.spinner-border.text-primary {
  color: var(--wiki-primary) !important;
  width: 3rem;
  height: 3rem;
  border-width: 0.3em;
}

/* Empty state */
.text-center {
  padding: 3rem 1rem;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .container {
    padding-left: 1rem;
    padding-right: 1rem;
  }
  
  h2 {
    font-size: 1.75rem;
  }
  
  .contest-card {
    padding: 1rem;
  }
  
  .contest-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }
  
  .contest-title-section {
    width: 100%;
  }
  
  .contest-title-link {
    font-size: 1.2rem;
  }
  
  .contest-timestamp {
    font-size: 0.8rem;
  }
  
  .contest-tags {
    gap: 0.35rem;
  }
  
  .contest-tag {
    font-size: 0.7rem;
    padding: 0.2rem 0.45rem;
  }
  
  .contest-tag i {
    font-size: 0.6rem;
  }
  
  .nav-tabs .nav-link {
    padding: 0.5rem 0.75rem;
    font-size: 0.9rem;
    margin-right: 0.25rem;
  }
}

@media (max-width: 576px) {
  h2 {
    font-size: 1.5rem;
  }
  
  .contest-card {
    padding: 0.875rem;
  }
  
  .contest-title-link {
    font-size: 1.1rem;
  }
  
  .contest-id {
    font-size: 0.85rem;
  }
  
  .contest-timestamp {
    font-size: 0.75rem;
  }
  
  .contest-tags {
    gap: 0.3rem;
  }
  
  .contest-tag {
    font-size: 0.65rem;
    padding: 0.2rem 0.4rem;
  }
  
  .contest-tag i {
    font-size: 0.6rem;
  }
  
  .nav-tabs {
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
  }
  
  .nav-tabs .nav-link {
    white-space: nowrap;
    padding: 0.5rem;
    font-size: 0.85rem;
  }
  
  .btn-sm {
    font-size: 0.75rem;
    padding: 0.25rem 0.5rem;
  }
  
  /* Make create button more compact on mobile */
  .btn-primary {
    font-size: 0.9rem;
    padding: 0.5rem 0.75rem;
  }
}
</style>

