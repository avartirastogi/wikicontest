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
    <div v-else class="row" id="contestList">
      <div v-if="currentContests.length === 0" class="col-12">
        <div class="alert alert-info text-center">
          <i class="fas fa-info-circle me-2"></i>
          No {{ activeCategory }} contests available.
        </div>
      </div>
      <div 
        v-for="contest in currentContests" 
        :key="contest.id"
        class="col-12 col-sm-6 col-md-6 col-lg-4 mb-3 mb-md-4"
      >
        <div class="card h-100">
          <div class="card-body d-flex flex-column">
            <h5 class="card-title">{{ contest.name }}</h5>
            <p class="card-text flex-grow-1">
              <strong>Project:</strong> {{ contest.project_name }}<br>
              <strong>Created by:</strong> {{ contest.created_by }}<br>
              <strong>Submissions:</strong> {{ contest.submission_count || 0 }}
            </p>
            <p v-if="contest.description" class="card-text text-muted">
              {{ truncateText(contest.description, 100) }}
            </p>
            <div class="d-flex justify-content-between align-items-center flex-wrap gap-2 mt-auto">
              <span class="badge bg-primary status-badge">{{ contest.status }}</span>
              <button 
                class="btn btn-sm btn-outline-primary" 
                @click="viewContest(contest.id)"
              >
                View Details
              </button>
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

/* Create contest button */
.btn-primary {
  background-color: var(--wiki-primary);
  border-color: var(--wiki-primary);
  font-weight: 500;
  transition: all 0.2s ease;
  white-space: nowrap; /* Prevent text wrapping */
  padding: 0.5rem 1rem; /* Compact padding */
}

.btn-primary:hover {
  background-color: var(--wiki-primary-hover);
  border-color: var(--wiki-primary-hover);
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 102, 153, 0.3);
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

/* Contest cards */
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
  transform: translateY(-5px);
  box-shadow: 0 8px 20px rgba(0, 102, 153, 0.15);
  border-color: var(--wiki-primary);
}

[data-theme="dark"] .card:hover {
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.5);
}

.card-body {
  padding: 1.5rem;
}

.card-title {
  color: var(--wiki-primary);
  font-weight: 600;
  font-size: 1.25rem;
  margin-bottom: 1rem;
  transition: color 0.3s ease;
}

.card-text {
  color: var(--wiki-text);
  line-height: 1.6;
  transition: color 0.3s ease;
}

.card-text strong {
  color: var(--wiki-dark);
  font-weight: 600;
  transition: color 0.3s ease;
}

/* Status badge */
.status-badge {
  background-color: var(--wiki-primary) !important;
  color: white;
  font-weight: 500;
  padding: 0.4em 0.8em;
  border-radius: 0.5rem;
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

[data-theme="dark"] .alert-info {
  background-color: rgba(77, 166, 204, 0.15);
}

.alert-info i {
  color: var(--wiki-primary);
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
  
  .card-body {
    padding: 1.25rem;
  }
  
  .card-title {
    font-size: 1.1rem;
  }
  
  .nav-tabs .nav-link {
    padding: 0.5rem 0.75rem;
    font-size: 0.9rem;
    margin-right: 0.25rem;
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
  h2 {
    font-size: 1.5rem;
  }
  
  .card-body {
    padding: 1rem;
  }
  
  .card-title {
    font-size: 1rem;
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
    font-size: 0.8rem;
    padding: 0.25rem 0.5rem;
  }
  
  /* Make create button more compact on mobile */
  .btn-primary {
    font-size: 0.9rem;
    padding: 0.5rem 0.75rem;
  }
}
</style>

