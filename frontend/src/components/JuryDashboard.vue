<template>
  <div class="jury-dashboard card mt-4">
    <!-- Header -->
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

      <span v-if="juryContests.length"
            class="badge bg-light text-dark px-3 py-2">
        {{ juryContests.length }} contests
      </span>
    </div>

    <div class="card-body">

      <!-- Loading -->
      <div v-if="loading" class="loading-box">
        <div class="spinner-border text-primary"></div>
        <p class="mt-2 text-muted mb-0">
          Loading assigned contests…
        </p>
      </div>

      <!-- Empty State -->
      <div v-else-if="juryContests.length === 0" class="empty-box">
        <i class="fas fa-inbox"></i>
        <p class="mt-3 mb-1 fw-semibold">
          No contests assigned yet
        </p>
        <small>
          You’ll see contests here once you are added as a jury member.
        </small>
      </div>

      <!-- Table -->
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
            <tr v-for="contest in juryContests" :key="contest.id">
              <td>
                <div class="fw-semibold">
                  {{ contest.name }}
                </div>
                <small class="text-muted">
                  {{ contest.slug }}
                </small>
              </td>

              <td class="text-muted">
                {{ contest.project_name || '—' }}
              </td>

              <td>
                <span :class="`status-pill ${contest.status}`">
                  <span class="dot"></span>
                  {{ contest.status }}
                </span>
              </td>

              <td class="fw-semibold">
                {{ contest.submission_count }}
              </td>

              <td class="text-muted">
                {{ formatDate(contest.created_at) }}
              </td>

              <td class="text-end">
                <button
                  class="btn btn-sm btn-primary-soft"
                  @click="goToContest(contest)">
                  <i class="fas fa-arrow-right me-1"></i>
                  Review
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

    </div>
  </div>
</template>


<script>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '../services/api'

export default {
  name: 'JuryDashboard',

  setup() {
    const router = useRouter()
    const juryContests = ref([])
    const loading = ref(false)

    const loadJuryContests = async () => {
      loading.value = true
      try {
        const data = await api.get('/user/dashboard')
        juryContests.value = data.jury_contests || []
      } catch (error) {
        console.error('Failed to load jury contests', error)
        juryContests.value = []
      } finally {
        loading.value = false
      }
    }

    const goToContest = (contest) => {
      router.push({
        name: 'ContestView',
        params: { name: contest.slug || contest.name }
      })
    }

    const formatDate = (date) => {
      if (!date) return ''
      return new Date(date).toLocaleDateString('en-IN', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      })
    }

    const statusColor = (status) => {
      switch (status) {
        case 'current':
          return 'success'
        case 'upcoming':
          return 'info'
        case 'past':
          return 'secondary'
        default:
          return 'primary'
      }
    }

    onMounted(loadJuryContests)

    return {
      juryContests,
      loading,
      goToContest,
      formatDate,
      statusColor
    }
  }
}
</script>

<style scoped>
/* Card */
.jury-dashboard {
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.06);
}

/* Header */
.jury-dashboard .card-header {
  background: var(--wiki-primary);
  color: #fff;
}

/* Loading */
.loading-box {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 3rem 0;
}

/* Empty */
.empty-box {
  text-align: center;
  padding: 3rem 1rem;
  color: #6c757d;
}

.empty-box i {
  font-size: 2.2rem;
  color: var(--wiki-primary);
}

/* Table */
.jury-table thead th {
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: #6c757d;
  background-color: #f8f9fa;
}

.jury-table tbody tr {
  transition: all 0.2s ease;
}

.jury-table tbody tr:hover {
  background-color: #f5f8ff;
  transform: translateY(-1px);
}

/* Status pill */
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

.status-pill .dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
}

.status-pill.current {
  background: #e6f4ea;
  color: #198754;
}

.status-pill.current .dot {
  background: #198754;
}

.status-pill.upcoming {
  background: #e7f1ff;
  color: var(--wiki-primary)
}

.status-pill.upcoming .dot {
  background: var(--wiki-primary)
}

.status-pill.past {
  background: #ececec;
  color: #6c757d;
}

.status-pill.past .dot {
  background: #6c757d;
}

/* Button */
.btn-primary-soft {
  background-color: rgba(13, 110, 253, 0.1);
  color: var(--wiki-primary);
  border: none;
  transition: all 0.2s ease;
}

.btn-primary-soft:hover {
  background-color: #0d6efd;
  color: #fff;
  transform: translateY(-1px);
}

/* Responsive */
@media (max-width: 768px) {
  .jury-table {
    font-size: 0.9rem;
  }
}

</style>
