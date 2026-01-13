<template>
  <div class="jury-dashboard mt-4">

    <!-- Statistics summary cards showing contest counts and submission totals -->
    <div class="stats-row mb-4">
      <!-- Total contests assigned to this jury member -->
      <div class="stat-card">
        <div class="stat-icon total">
          <i class="fas fa-trophy"></i>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ totalContests }}</div>
          <div class="stat-label">Total Contests</div>
        </div>
      </div>

      <!-- Currently active contests requiring review -->
      <div class="stat-card">
        <div class="stat-icon current">
          <i class="fas fa-clock"></i>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ currentContests }}</div>
          <div class="stat-label">Current Contests</div>
        </div>
      </div>

      <!-- Total submissions across all assigned contests -->
      <div class="stat-card">
        <div class="stat-icon submissions">
          <i class="fas fa-file-alt"></i>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ totalSubmissions }}</div>
          <div class="stat-label">Total Submissions</div>
        </div>
      </div>
    </div>

    <!-- Main card containing contest list table -->
    <div class="card">
      <!-- Header with title and contest count badge -->
      <div class="card-header d-flex align-items-center justify-content-between">
        <div>
          <h5 class="mb-0 d-flex align-items-center">
            <i class="fas fa-gavel me-2"></i>
            Jury Dashboard
          </h5>
          <small class="opacity-75">
            Contests assigned for review
          </small>
        </div>

        <!-- Display total number of assigned contests -->
        <span v-if="juryContests.length" class="badge bg-light text-dark px-3 py-2">
          {{ juryContests.length }} contests
        </span>
      </div>

      <div class="card-body">

        <!-- Loading state with spinner -->
        <div v-if="loading" class="loading-box">
          <div class="spinner-border text-primary"></div>
          <p class="mt-2 text-muted mb-0">
            Loading assigned contests…
          </p>
        </div>

        <!-- Empty state when no contests are assigned -->
        <div v-else-if="juryContests.length === 0" class="empty-box">
          <i class="fas fa-inbox"></i>
          <p class="mt-3 mb-1 fw-semibold">
            No contests assigned yet
          </p>
          <small>
            You'll see contests here once you are added as a jury member.
          </small>
        </div>

        <!-- Contest list table with details and actions -->
        <div v-else class="table-responsive">
          <table class="table jury-table align-middle">
            <thead>
              <tr>
                <th>Contest</th>
                <th>Project</th>
                <th>Status</th>
                <th>Submissions</th>
                <th>Created</th>
                <th class="text-end">Action</th>
              </tr>
            </thead>

            <tbody>
              <!-- Loop through each assigned contest -->
              <tr v-for="contest in juryContests" :key="contest.id">
                <!-- Contest name and slug -->
                <td>
                  <div class="fw-semibold">
                    {{ contest.name }}
                  </div>
                  <small class="text-muted">
                    {{ contest.slug }}
                  </small>
                </td>

                <!-- Project name or placeholder -->
                <td class="text-muted">
                  {{ contest.project_name || '—' }}
                </td>

                <!-- Status pill with color-coded indicator -->
                <td>
                  <span :class="`status-pill ${contest.status}`">
                    <span class="dot"></span>
                    {{ contest.status }}
                  </span>
                </td>

                <!-- Number of submissions for this contest -->
                <td class="fw-semibold">
                  {{ contest.submission_count }}
                </td>

                <!-- Contest creation date formatted -->
                <td class="text-muted">
                  {{ formatDate(contest.created_at) }}
                </td>

                <!-- Action button to navigate to contest -->
                <td class="text-end">
                  <button class="btn btn-sm btn-primary-soft" @click="goToContest(contest)">
                    <i class="fas fa-arrow-right me-1"></i>
                    {{ contest.status === 'past' ? 'Go to Contest' : 'Review' }}
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

      </div>
    </div>
  </div>
</template>


<script>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '../services/api'

export default {
  name: 'JuryDashboard',

  setup() {
    const router = useRouter()
    const juryContests = ref([])
    const loading = ref(false)

    // Calculate total number of assigned contests
    const totalContests = computed(() => juryContests.value.length)

    // Count only contests with current status
    const currentContests = computed(() =>
      juryContests.value.filter(c => c.status === 'current').length
    )

    // Sum all submissions across all assigned contests
    const totalSubmissions = computed(() =>
      juryContests.value.reduce((sum, c) => sum + (c.submission_count || 0), 0)
    )

    // Calculate pending reviews for current contests only
    const pendingReviews = computed(() =>
      juryContests.value
        .filter(c => c.status === 'current')
        .reduce((sum, c) => sum + (c.submission_count || 0), 0)
    )

    // Fetch jury contests from API and sort by status priority
    const loadJuryContests = async () => {
      loading.value = true
      try {
        const data = await api.get('/user/dashboard')
        // Sort: current first, then upcoming, then past
        const contests = data.jury_contests || []
        juryContests.value = contests.sort((a, b) => {
          const order = { current: 1, upcoming: 2, past: 3 }
          return (order[a.status] || 4) - (order[b.status] || 4)
        })
      } catch (error) {
        console.error('Failed to load jury contests', error)
        juryContests.value = []
      } finally {
        loading.value = false
      }
    }

    // Navigate to contest detail page using slug or name
    const goToContest = (contest) => {
      router.push({
        name: 'ContestView',
        params: { name: contest.slug || contest.name }
      })
    }

    // Format date to localized string with Indian locale
    const formatDate = (date) => {
      if (!date) return ''
      return new Date(date).toLocaleDateString('en-IN', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      })
    }

    // Load contests when component mounts
    onMounted(loadJuryContests)

    return {
      juryContests,
      loading,
      totalContests,
      currentContests,
      totalSubmissions,
      pendingReviews,
      goToContest,
      formatDate
    }
  }
}
</script>

<style scoped>

/* Responsive grid layout for stat cards */
.stats-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 1.25rem;
}

/* Individual stat card with hover effect */
.stat-card {
  background: var(--card-bg, white);
  border-radius: 12px;
  padding: 1.5rem;
  display: flex;
  align-items: center;
  gap: 1rem;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.06);
  transition: all 0.3s ease;
  border: 1px solid var(--border-color, #e9ecef);
}

/* Lift effect on hover */
.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
}

/* Icon container with Wikipedia blue background */
.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  color: white;
  background: var(--wiki-primary);
}

/* Content area for value and label */
.stat-content {
  flex: 1;
}

/* Large numeric value display */
.stat-value {
  font-size: 2rem;
  font-weight: 700;
  color: var(--text-primary, #1a1a1a);
  line-height: 1;
}

/* Descriptive label below value */
.stat-label {
  font-size: 0.875rem;
  color: var(--text-muted, #6c757d);
  margin-top: 0.25rem;
  font-weight: 500;
}

/* Card with rounded corners and shadow */
.jury-dashboard .card {
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.06);
  background: var(--card-bg, white);
  border: 1px solid var(--border-color, #e9ecef);
}

/* Header with Wikipedia primary color */
.jury-dashboard .card-header {
  background: var(--wiki-primary);
  color: #fff;
}

/* Centered loading indicator */
.loading-box {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 3rem 0;
}

/* Empty state message */
.empty-box {
  text-align: center;
  padding: 3rem 1rem;
  color: var(--text-muted, #6c757d);
}

/* Large icon for empty state */
.empty-box i {
  font-size: 2.2rem;
  color: var(--wiki-primary);
}


/* Table header with uppercase styling */
.jury-table thead th {
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--text-muted, #6c757d);
  background-color: var(--table-header-bg, #f8f9fa);
}

/* Row hover and lift effect */
.jury-table tbody tr {
  transition: all 0.2s ease;
}

.jury-table tbody tr:hover {
  background-color: var(--table-hover-bg, #f5f8ff);
  transform: translateY(-1px);
}

/* Base pill styling with dot indicator */
.status-pill {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 4px 10px;
  font-size: 0.75rem;
  font-weight: 600;
  border-radius: 20px;
  text-transform: capitalize;
}

/* Colored dot inside status pill */
.status-pill .dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
}

/* Current status: green colors */
.status-pill.current {
  background: var(--status-current-bg, #e6f4ea);
  color: var(--status-current-text, #198754);
}

.status-pill.current .dot {
  background: var(--status-current-text, #198754);
}

/* Upcoming status: blue colors */
.status-pill.upcoming {
  background: var(--status-upcoming-bg, #e7f1ff);
  color: var(--wiki-primary);
}

.status-pill.upcoming .dot {
  background: var(--wiki-primary);
}

/* Past status: gray colors */
.status-pill.past {
  background: var(--status-past-bg, #ececec);
  color: var(--status-past-text, #6c757d);
}

.status-pill.past .dot {
  background: var(--status-past-text, #6c757d);
}

/* Soft primary button with hover transition */
.btn-primary-soft {
  background-color: var(--btn-soft-bg, rgba(13, 110, 253, 0.1));
  color: var(--wiki-primary);
  border: none;
  transition: all 0.2s ease;
}

/* Hover: solid primary color with lift */
.btn-primary-soft:hover {
  background-color: var(--wiki-primary);
  color: #fff;
  transform: translateY(-1px);
}

/* Tablet: 2-column grid for stats */
@media (max-width: 768px) {
  .stats-row {
    grid-template-columns: repeat(2, 1fr);
  }

  /* Reduce padding on smaller screens */
  .stat-card {
    padding: 1rem;
  }

  /* Smaller icon size */
  .stat-icon {
    width: 50px;
    height: 50px;
    font-size: 1.25rem;
  }

  /* Smaller value font */
  .stat-value {
    font-size: 1.5rem;
  }

  /* Smaller table text */
  .jury-table {
    font-size: 0.9rem;
  }
}

/* Mobile: single column for stats */
@media (max-width: 576px) {
  .stats-row {
    grid-template-columns: 1fr;
  }
}

/* Dark mode stat cards */
[data-theme="dark"] .stat-card,
.dark-mode .stat-card {
  background: var(--card-bg, #1e1e1e);
  border-color: var(--border-color, #333);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}

/* Dark mode hover with stronger shadow */
[data-theme="dark"] .stat-card:hover,
.dark-mode .stat-card:hover {
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.4);
}

/* Dark mode text colors */
[data-theme="dark"] .stat-value,
.dark-mode .stat-value {
  color: var(--text-primary, #ffffff);
}

[data-theme="dark"] .stat-label,
.dark-mode .stat-label {
  color: var(--text-muted, #a0a0a0);
}

/* Dark mode main card */
[data-theme="dark"] .jury-dashboard .card,
.dark-mode .jury-dashboard .card {
  background: var(--card-bg, #1e1e1e);
  border-color: var(--border-color, #333);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
}

/* Dark mode table header */
[data-theme="dark"] .jury-table thead th,
.dark-mode .jury-table thead th {
  background-color: var(--table-header-bg, #2a2a2a);
  color: var(--text-muted, #a0a0a0);
}

/* Dark mode table row hover */
[data-theme="dark"] .jury-table tbody tr:hover,
.dark-mode .jury-table tbody tr:hover {
  background-color: var(--table-hover-bg, #2a2a2a);
}

/* Dark mode empty state */
[data-theme="dark"] .empty-box,
.dark-mode .empty-box {
  color: var(--text-muted, #a0a0a0);
}

/* Dark mode button */
[data-theme="dark"] .btn-primary-soft,
.dark-mode .btn-primary-soft {
  background-color: var(--btn-soft-bg, rgba(13, 110, 253, 0.2));
}
</style>
