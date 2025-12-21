<template>
  <div class="modal fade" id="createContestModal" tabindex="-1">
    <div class="modal-dialog modal-fullscreen">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">Create New Contest</h5>
          <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
        </div>
        <div class="modal-body">
          <form @submit.prevent="handleSubmit">
            <div class="row">
              <div class="col-md-6 mb-3">
                <label for="contestName" class="form-label">Contest Name *</label>
                <input type="text"
class="form-control"
id="contestName"
v-model="formData.name"
required />
              </div>
              <div class="col-md-6 mb-3">
                <label for="projectName" class="form-label">Project Name *</label>
                <input type="text"
class="form-control"
id="projectName"
v-model="formData.project_name"
required />
              </div>
            </div>

            <div class="mb-3">
              <label for="contestDescription" class="form-label">Description</label>
              <textarea class="form-control"
id="contestDescription"
rows="3"
v-model="formData.description"></textarea>
            </div>
            <div class="mb-3">
              <label for="contestRules" class="form-label">Contest Rules *</label>
              <textarea class="form-control"
id="contestRules"
rows="4"
                placeholder="Write rules about how articles must be submitted."
v-model="formData.rules_text"
                required></textarea>
            </div>
            <div class="mb-3">
              <label for="allowedType" class="form-label">Allowed Submission Type</label>
              <select id="allowedType" class="form-control" v-model="formData.allowed_submission_type">
                <option value="new">New Article Only</option>
                <option value="expansion">Improved Article Only</option>
                <option value="both">Both(New Article + Improved Article)</option>
              </select>
            </div>

            <div class="row">
              <div class="col-md-6 mb-3">
                <label for="startDate" class="form-label">Start Date *</label>
                <input type="date"
class="form-control"
id="startDate"
v-model="formData.start_date"
required />
              </div>
              <div class="col-md-6 mb-3">
                <label for="endDate" class="form-label">End Date *</label>
                <input type="date"
class="form-control"
id="endDate"
v-model="formData.end_date"
required />
              </div>
            </div>

            <!-- Jury Members with Autocomplete -->
            <div class="mb-3">
              <label for="juryInput" class="form-label">
                Jury Members *
                <span class="badge bg-info">Type to search users</span>
              </label>

              <!-- Selected Jury Members Display -->
              <div class="mb-2 p-2 border rounded bg-light jury-selection-box" style="min-height: 40px;">
                <small v-if="selectedJury.length === 0" class="jury-placeholder-text">
                  No jury members selected yet
                </small>
                <span v-for="username in selectedJury"
:key="username"
class="badge bg-primary me-2 mb-2"
                  style="font-size: 0.9rem; cursor: pointer;">
                  {{ username }}
                  <i class="fas fa-times ms-1" @click="removeJury(username)"></i>
                </span>
              </div>

              <!-- Jury Input with Autocomplete -->
              <div style="position: relative;">
                <input type="text"
class="form-control"
id="juryInput"
v-model="jurySearchQuery"
@input="searchJury"
                  placeholder="Type username to search..."
autocomplete="off" />
                <!-- Autocomplete Dropdown -->
                <!--
                  Note: we avoid hard-coded light backgrounds here so that
                  the dropdown looks correct in both light and dark modes.
                  Colors now come from CSS variables defined in the styles below.
                -->
                <div v-if="jurySearchResults.length > 0 && jurySearchQuery.length >= 2"
                  class="jury-autocomplete position-absolute w-100 border rounded-bottom"
                  style="max-height: 200px; overflow-y: auto; z-index: 1000; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                  <div v-for="user in jurySearchResults"
:key="user.username"
class="p-2 border-bottom cursor-pointer"
                    style="cursor: pointer;"
@click="addJury(user.username)">
                    <i class="fas fa-user me-2 text-primary"></i>
                    <strong>{{ user.username }}</strong>
                  </div>
                </div>
              </div>
            </div>

            <div class="row">
              <div class="col-md-6 mb-3">
                <label for="marksAccepted" class="form-label">Points for Accepted Submissions</label>
                <input type="number"
class="form-control"
id="marksAccepted"
                  v-model.number="formData.marks_setting_accepted"
min="0" />
              </div>
              <div class="col-md-6 mb-3">
                <label for="marksRejected" class="form-label">Points for Rejected Submissions</label>
                <input type="number"
class="form-control"
id="marksRejected"
                  v-model.number="formData.marks_setting_rejected"
min="0" />
              </div>
            </div>

            <div class="row">
              <div class="col-md-6 mb-3">
                <label for="minByteCount" class="form-label">
                  Minimum Byte Count <span class="text-muted">(Optional)</span>
                </label>
                <input type="number"
class="form-control"
id="minByteCount"
                  v-model.number="formData.min_byte_count"
min="0"
                  placeholder="e.g., 1000" />
                <small class="form-text text-muted">Articles must have at least this many bytes</small>
              </div>
              <div class="col-md-6 mb-3">
                <label for="maxByteCount" class="form-label">
                  Maximum Byte Count <span class="text-muted">(Optional)</span>
                </label>
                <input type="number"
class="form-control"
id="maxByteCount"
                  v-model.number="formData.max_byte_count"
min="0"
                  placeholder="e.g., 50000" />
                <small class="form-text text-muted">Articles must not exceed this many bytes</small>
              </div>
            </div>

            <div class="mb-3">
              <label for="codeLink" class="form-label">
                Code Repository Link <span class="text-muted">(Optional)</span>
              </label>
              <input type="text"
class="form-control"
id="codeLink"
v-model="formData.code_link"
                placeholder="https://github.com/..." />
            </div>


          </form>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
          <button type="button"
class="btn btn-primary"
@click="handleSubmit"
:disabled="loading">
            <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
            Create Contest
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, onMounted } from 'vue'
import { useStore } from '../store'
import { showAlert } from '../utils/alerts'
import api from '../services/api'

export default {
  name: 'CreateContestModal',
  emits: ['created'],
  setup(props, { emit }) {
    const store = useStore()
    const loading = ref(false)
    const selectedJury = ref([])
    const jurySearchQuery = ref('')
    const jurySearchResults = ref([])
    let searchTimeout = null

    const formData = reactive({
      name: '',
      project_name: '',
      description: '',
      start_date: '',
      end_date: '',
      jury_members: [],
      marks_setting_accepted: 10,
      marks_setting_rejected: 0,
      code_link: null,
      rules_text: '',
      allowed_submission_type: 'both',
      min_byte_count: null,
      max_byte_count: null
    })

    // Set default dates
    onMounted(() => {
      const today = new Date()
      const tomorrow = new Date(today)
      tomorrow.setDate(tomorrow.getDate() + 1)
      const nextWeek = new Date(today)
      nextWeek.setDate(nextWeek.getDate() + 7)

      formData.start_date = tomorrow.toISOString().split('T')[0]
      formData.end_date = nextWeek.toISOString().split('T')[0]
    })

    // Search for users (jury members)
    const searchJury = async () => {
      const query = jurySearchQuery.value.trim()

      if (query.length < 2) {
        jurySearchResults.value = []
        return
      }

      // Debounce search
      if (searchTimeout) {
        clearTimeout(searchTimeout)
      }

      searchTimeout = setTimeout(async () => {
        try {
          const response = await api.get(`/user/search?q=${encodeURIComponent(query)}&limit=10`)
          // Filter out already selected users
          jurySearchResults.value = (response.users || []).filter(
            user => !selectedJury.value.includes(user.username)
          )
        } catch (error) {
          console.error('User search error:', error)
          jurySearchResults.value = []
        }
      }, 300)
    }

    // Add jury member
    const addJury = (username) => {
      if (!selectedJury.value.includes(username)) {
        selectedJury.value.push(username)
        formData.jury_members = [...selectedJury.value]
        jurySearchQuery.value = ''
        jurySearchResults.value = []
      }
    }

    // Remove jury member
    const removeJury = (username) => {
      selectedJury.value = selectedJury.value.filter(u => u !== username)
      formData.jury_members = [...selectedJury.value]
    }

    // Handle form submission
    const handleSubmit = async () => {
      // Validation
      if (!formData.name.trim()) {
        showAlert('Contest name is required', 'warning')
        return
      }
      if (!formData.project_name.trim()) {
        showAlert('Project name is required', 'warning')
        return
      }
      if (!formData.start_date) {
        showAlert('Start date is required', 'warning')
        return
      }
      if (!formData.end_date) {
        showAlert('End date is required', 'warning')
        return
      }
      if (selectedJury.value.length === 0) {
        showAlert('At least one jury member is required', 'warning')
        return
      }
      if (new Date(formData.start_date) >= new Date(formData.end_date)) {
        showAlert('End date must be after start date', 'warning')
        return
      }

      // Validate byte count range
      if (formData.min_byte_count !== null && formData.max_byte_count !== null) {
        if (formData.min_byte_count > formData.max_byte_count) {
          showAlert('Minimum byte count must be less than or equal to maximum byte count', 'warning')
          return
        }
      }

      loading.value = true
      try {
        const contestData = {
          ...formData,
          jury_members: selectedJury.value,
          code_link: formData.code_link?.trim() || null,
          rules: {
            text: formData.rules_text.trim()
          },
          // Byte count fields: null if not set or invalid, otherwise use the value (including 0)
          min_byte_count: (
            formData.min_byte_count === null ||
            formData.min_byte_count === undefined ||
            isNaN(formData.min_byte_count)
          )
            ? null
            : Number(formData.min_byte_count),
          max_byte_count: (
            formData.max_byte_count === null ||
            formData.max_byte_count === undefined ||
            isNaN(formData.max_byte_count)
          )
            ? null
            : Number(formData.max_byte_count)
        }

        const result = await store.createContest(contestData)
        if (result.success) {
          showAlert('Contest created successfully!', 'success')
          emit('created')
          // Close modal
          const modalElement = document.getElementById('createContestModal')
          const modal = bootstrap.Modal.getInstance(modalElement)
          if (modal) {
            modal.hide()
          }
          // Reset form
          resetForm()
        } else {
          showAlert(result.error || 'Failed to create contest', 'danger')
        }
      } catch (error) {
        showAlert('Failed to create contest: ' + error.message, 'danger')
      } finally {
        loading.value = false
      }
    }

    // Reset form
    const resetForm = () => {
      formData.name = ''
      formData.project_name = ''
      formData.description = ''
      formData.code_link = null
      selectedJury.value = []
      formData.jury_members = []
      formData.rules_text = ''
      formData.min_byte_count = null
      formData.max_byte_count = null

      // Reset dates
      const today = new Date()
      const tomorrow = new Date(today)
      tomorrow.setDate(tomorrow.getDate() + 1)
      const nextWeek = new Date(today)
      nextWeek.setDate(nextWeek.getDate() + 7)
      formData.start_date = tomorrow.toISOString().split('T')[0]
      formData.end_date = nextWeek.toISOString().split('T')[0]
    }

    return {
      formData,
      selectedJury,
      jurySearchQuery,
      jurySearchResults,
      loading,
      searchJury,
      addJury,
      removeJury,
      handleSubmit
    }
  }
}
</script>

<style scoped>
/* Create Contest Modal Styling with Wikipedia Colors */

/* Modal header - solid color, no gradient */
.modal-header {
  background-color: var(--wiki-primary);
  color: white;
  border-bottom: none;
  padding: 1.25rem 1.5rem;
  transition: background-color 0.2s ease;
}

.modal-title {
  font-weight: 600;
  font-size: 1.5rem;
}

.modal-header .btn-close {
  filter: invert(1) brightness(1.2);
  opacity: 0.9;
}

[data-theme="dark"] .modal-header .btn-close {
  filter: invert(1) brightness(2);
}

/* Modal body */
.modal-body {
  background-color: var(--wiki-modal-bg);
  color: var(--wiki-text);
  transition: background-color 0.3s ease, color 0.3s ease;
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
}

[data-theme="dark"] .form-control {
  border-width: 1px;
  border-style: solid;
}

/* Textarea specific styling */
textarea.form-control {
  resize: vertical;
  min-height: 80px;
}

.form-control:focus {
  border-color: var(--wiki-primary);
  box-shadow: 0 0 0 0.2rem rgba(0, 102, 153, 0.25);
  background-color: var(--wiki-input-bg);
  color: var(--wiki-text);
  outline: none;
}

[data-theme="dark"] .form-control:focus {
  box-shadow: 0 0 0 0.2rem rgba(93, 184, 230, 0.3);
  border-color: var(--wiki-primary);
}

/* Placeholder text styling for dark mode */
.form-control::placeholder {
  color: var(--wiki-text-muted);
  opacity: 0.7;
  transition: color 0.3s ease;
}

[data-theme="dark"] .form-control::placeholder {
  opacity: 0.6;
}

/* Jury input placeholder - more visible */
#juryInput::placeholder {
  color: #666666 !important;
  opacity: 1 !important;
  font-weight: 500;
}

[data-theme="dark"] #juryInput::placeholder {
  color: #ffffff !important;
  opacity: 0.9 !important;
}

/* Date input styling */
input[type="date"].form-control {
  color-scheme: light;
}

[data-theme="dark"] input[type="date"].form-control {
  color-scheme: dark;
}

/* Badge styling */
.badge {
  font-weight: 500;
  padding: 0.4em 0.8em;
}

.badge.bg-primary {
  background-color: var(--wiki-primary) !important;
}

.badge.bg-info {
  background-color: var(--wiki-primary) !important;
  color: white;
}

/* Badge text-dark class - ensure visibility in dark mode */
.badge.text-dark {
  color: var(--wiki-dark) !important;
  transition: color 0.3s ease;
}

[data-theme="dark"] .badge.text-dark {
  color: #f0f0f0 !important;
}

/* Jury members display - professional */
.bg-light {
  background-color: var(--wiki-hover-bg) !important;
  border-color: var(--wiki-primary) !important;
  border: 1px solid var(--wiki-border);
  border-radius: 4px;
  padding: 1rem;
  transition: background-color 0.2s ease, border-color 0.2s ease;
}

[data-theme="dark"] .bg-light {
  background-color: rgba(93, 184, 230, 0.1) !important;
}

/* Jury selection box text - more visible */
.jury-selection-box .jury-placeholder-text {
  color: #333333 !important;
  font-weight: 500;
}

[data-theme="dark"] .jury-selection-box .jury-placeholder-text {
  color: #ffffff !important;
}

.badge.bg-primary {
  background-color: var(--wiki-primary) !important;
  color: white;
  cursor: pointer;
  transition: all 0.2s ease;
}

.badge.bg-primary:hover {
  background-color: var(--wiki-primary-hover) !important;
}

/* Autocomplete dropdown - professional */
.jury-autocomplete {
  border: 1px solid var(--wiki-border);
  border-top: none;
  border-radius: 0 0 4px 4px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  background-color: var(--wiki-card-bg);
  transition: background-color 0.2s ease, border-color 0.2s ease;
}

[data-theme="dark"] .jury-autocomplete {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
}

.jury-autocomplete .p-2 {
  transition: background-color 0.2s ease;
  color: var(--wiki-text);
}

.jury-autocomplete .p-2:hover {
  background-color: var(--wiki-hover-bg) !important;
}

.jury-autocomplete .text-primary {
  color: var(--wiki-primary) !important;
}

/* Button styling */
.btn-primary {
  background-color: var(--wiki-primary);
  border-color: var(--wiki-primary);
  font-weight: 500;
  transition: all 0.2s ease;
}

.btn-primary:hover {
  background-color: var(--wiki-primary-hover);
  border-color: var(--wiki-primary-hover);
  box-shadow: 0 2px 4px rgba(0, 102, 153, 0.2);
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-secondary {
  background-color: var(--wiki-text-muted);
  border-color: var(--wiki-text-muted);
  transition: all 0.2s ease;
}

.btn-secondary:hover {
  background-color: var(--wiki-text-muted);
  border-color: var(--wiki-text-muted);
}

[data-theme="dark"] .btn-secondary {
  background-color: #5a6268;
  border-color: #5a6268;
}

[data-theme="dark"] .btn-secondary:hover {
  background-color: #6c757d;
  border-color: #6c757d;
}

/* Modal footer */
.modal-footer {
  border-top: 1px solid var(--wiki-border);
  padding: 1rem 1.5rem;
  background-color: var(--wiki-modal-bg);
  transition: background-color 0.3s ease, border-color 0.3s ease;
}

/* Text muted */
.text-muted {
  color: var(--wiki-text-muted) !important;
  transition: color 0.3s ease;
}

/* Spinner */
.spinner-border-sm {
  width: 1rem;
  height: 1rem;
  border-width: 0.15em;
  border-color: currentColor;
  border-right-color: transparent;
}

/* Full screen modal styling */
.modal-fullscreen {
  width: 100vw;
  max-width: 100%;
  height: 100vh;
  margin: 0;
  padding: 0;
}

.modal-fullscreen .modal-content {
  height: 100vh;
  border: 0;
  border-radius: 0;
  display: flex;
  flex-direction: column;
}

.modal-fullscreen .modal-body {
  flex: 1;
  overflow-y: auto;
  padding: 2rem;
}

/* Better spacing for full screen layout */
.modal-fullscreen .modal-body .row {
  margin-bottom: 1rem;
}

.modal-fullscreen .modal-body .mb-3 {
  margin-bottom: 1.5rem !important;
}

/* Ensure form uses available space well */
.modal-fullscreen .modal-body form {
  max-width: 1200px;
  margin: 0 auto;
}
</style>
