<template>
  <div class="modal fade" id="submitArticleModal" tabindex="-1">
    <div class="modal-dialog modal-dialog-centered">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">
            <i class="fas fa-paper-plane me-2"></i>Submit Article
          </h5>
          <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
        </div>
        <div class="modal-body">
          <form @submit.prevent="handleSubmit">
            <!-- Info message about URL submission -->
            <div class="alert alert-info mb-3">
              <i class="fas fa-info-circle me-2"></i>
              <strong>Note:</strong> Please submit the URL of your article.
              The system will automatically fetch article information including title and author.
            </div>

            <div class="mb-3">
              <label for="articleUrl" class="form-label">
                <i class="fas fa-link me-2 text-primary"></i>Article URL <span class="text-danger">*</span>
              </label>
              <input
                type="url"
                class="form-control"
                id="articleUrl"
                v-model="formData.article_link"
                placeholder="https://en.wikipedia.org/wiki/Article_Title"
                required
                autofocus
              />
              <small class="form-text text-muted">
                Enter the full URL of your MediaWiki article (e.g., Wikipedia, Wikiversity, etc.)
              </small>
            </div>

            <!-- Validation Checklist -->
            <div class="mb-3" v-if="contest && (contest.min_byte_count || contest.max_byte_count)">
              <label class="form-label">
                <i class="fas fa-check-circle me-2 text-primary"></i>Validation Checklist
              </label>
              <div class="card border-primary">
                <div class="card-body">
                  <div class="validation-item mb-2" v-for="(item, index) in validationChecklist" :key="index">
                    <div
                      class="d-flex align-items-center"
                      :class="{
                        'text-success': item.checked,
                        'text-danger': !item.checked && item.detail,
                        'text-muted': !item.checked && !item.detail
                      }"
                    >
                      <i
                        :class="
                          item.checked
                            ? 'fas fa-check-circle text-success me-2'
                            : item.detail
                            ? 'fas fa-times-circle text-danger me-2'
                            : 'fas fa-circle text-muted me-2'
                        "
                      ></i>
                      <span class="flex-grow-1">
                        {{ item.label }}
                        <span
                          v-if="item.detail"
                          :class="{
                            'text-danger small ms-2': !item.checked,
                            'text-muted small ms-2': item.checked
                          }"
                        >({{ item.detail }})</span>
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Progress Indicator -->
            <div v-if="submissionProgress.stage !== 'idle'" class="mb-3">
              <div class="card border-primary">
                <div class="card-body">
                  <h6 class="card-title mb-3">
                    <i class="fas fa-tasks me-2"></i>Submission Progress
                  </h6>

                  <!-- Progress Bar -->
                  <div class="progress mb-3" style="height: 25px;">
                    <div
                      class="progress-bar progress-bar-striped progress-bar-animated"
                      :class="progressBarClass"
                      role="progressbar"
                      :style="{ width: progressPercentage + '%' }"
                    >
                      {{ progressPercentage }}%
                    </div>
                  </div>

                  <!-- Progress Steps -->
                  <div class="progress-steps">
                    <div
                      v-for="(step, index) in progressSteps"
                      :key="index"
                      class="progress-step mb-2"
                      :class="{ 'active': step.active, 'completed': step.completed, 'failed': step.failed }"
                    >
                      <i
                        :class="step.icon"
                        class="me-2"
                        :style="{ color: step.iconColor }"
                      ></i>
                      <span>{{ step.label }}</span>
                      <span v-if="step.detail" class="text-muted ms-2 small">({{ step.detail }})</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <div v-if="error"
class="alert alert-danger"
role="alert"
style="white-space: pre-wrap; word-wrap: break-word;">
              <strong>Error:</strong><br/>{{ error }}
            </div>
          </form>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
            <i class="fas fa-times me-2"></i>Cancel
          </button>
          <button
            type="button"
            class="btn btn-primary"
            @click="handleSubmit"
            :disabled="loading || !canSubmit"
          >
            <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
            <i v-else class="fas fa-paper-plane me-2"></i>Submit Article
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { showAlert } from '../utils/alerts'
import api from '../services/api'

export default {
  name: 'SubmitArticleModal',
  props: {
    contestId: {
      type: Number,
      required: true
    }
  },
  emits: ['submitted'],
  setup(props, { emit }) {
    const loading = ref(false)
    const error = ref('')
    const contest = ref(null)

    const formData = reactive({
      article_link: ''
    })

    // Validation checklist state
    const validationChecklist = reactive([
      {
        label: 'Article URL is valid',
        checked: false,
        detail: null
      },
      {
        label: 'Article byte count is within required range',
        checked: false,
        detail: null
      }
    ])

    // Submission progress tracking
    const submissionProgress = reactive({
      stage: 'idle', // 'idle', 'fetching', 'validating', 'submitting', 'success', 'error'
      articleByteCount: null,
      contestByteRequirements: null
    })

    // Load contest details to get byte count requirements
    const loadContest = async () => {
      try {
        const data = await api.get(`/contest/${props.contestId}`)
        contest.value = data
        submissionProgress.contestByteRequirements = {
          min: data.min_byte_count,
          max: data.max_byte_count
        }
      } catch (err) {
        console.error('Error loading contest:', err)
      }
    }

    onMounted(() => {
      loadContest()
    })

    // Debounce timer for URL validation
    let validationTimer = null

    // Watch for URL changes and validate automatically
    // This provides real-time feedback as user enters the URL
    watch(
      () => formData.article_link,
      (newUrl) => {
        // Clear any existing timer
        if (validationTimer) {
          clearTimeout(validationTimer)
        }

        // Reset checklist when URL is cleared
        if (!newUrl || !newUrl.trim()) {
          validationChecklist[0].checked = false
          validationChecklist[0].detail = null
          validationChecklist[1].checked = false
          validationChecklist[1].detail = null
          return
        }

        // Debounce validation - wait 800ms after user stops typing
        // This prevents too many API calls while user is typing
        validationTimer = setTimeout(async () => {
          // Only validate if URL looks like a valid URL (starts with http)
          if (newUrl.trim().startsWith('http://') || newUrl.trim().startsWith('https://')) {
            // Wait for contest to be loaded before validating
            // This ensures we have byte count requirements available
            if (!contest.value) {
              await loadContest()
            }
            // Validate silently (without showing progress indicators)
            await validateArticle(false)
          } else {
            // URL format is invalid, just mark URL check as failed
            validationChecklist[0].checked = false
            validationChecklist[0].detail = 'URL must start with http:// or https://'
            validationChecklist[1].checked = false
            validationChecklist[1].detail = null
          }
        }, 800)
      }
    )

    // Progress steps based on current stage
    const progressSteps = computed(() => {
      const steps = [
        {
          label: 'Fetching article information',
          icon: 'fas fa-spinner fa-spin',
          iconColor: '#006699',
          active: submissionProgress.stage === 'fetching',
          completed: ['validating', 'submitting', 'success'].includes(submissionProgress.stage),
          failed: false,
          detail: submissionProgress.stage === 'fetching' ? 'Getting article details from MediaWiki...' : null
        },
        {
          label: 'Checking byte count requirements',
          icon: 'fas fa-check-circle',
          iconColor: '#28a745',
          active: submissionProgress.stage === 'validating',
          completed: ['submitting', 'success'].includes(submissionProgress.stage),
          failed: submissionProgress.stage === 'error' && error.value.includes('byte count'),
          detail: getByteCountDetail()
        },
        {
          label: 'Submitting article',
          icon: 'fas fa-paper-plane',
          iconColor: '#006699',
          active: submissionProgress.stage === 'submitting',
          completed: submissionProgress.stage === 'success',
          failed: submissionProgress.stage === 'error' && !error.value.includes('byte count'),
          detail: submissionProgress.stage === 'submitting' ? 'Creating submission...' : null
        }
      ]
      return steps
    })

    // Get byte count detail text
    const getByteCountDetail = () => {
      if (submissionProgress.stage === 'idle' || submissionProgress.stage === 'fetching') {
        return null
      }

      const req = submissionProgress.contestByteRequirements
      const count = submissionProgress.articleByteCount

      if (!req || (!req.min && !req.max)) {
        return 'No byte count restrictions'
      }

      if (count !== null) {
        const minText = req.min ? `min: ${req.min.toLocaleString()}` : ''
        const maxText = req.max ? `max: ${req.max.toLocaleString()}` : ''
        const rangeText = [minText, maxText].filter(Boolean).join(', ')
        return `Article: ${count.toLocaleString()} bytes | Required: ${rangeText}`
      }

      return 'Checking...'
    }

    // Progress percentage
    const progressPercentage = computed(() => {
      switch (submissionProgress.stage) {
        case 'fetching':
          return 33
        case 'validating':
          return 66
        case 'submitting':
          return 90
        case 'success':
          return 100
        case 'error':
          return 0
        default:
          return 0
      }
    })

    // Progress bar class
    const progressBarClass = computed(() => {
      if (submissionProgress.stage === 'error') {
        return 'bg-danger'
      }
      if (submissionProgress.stage === 'success') {
        return 'bg-success'
      }
      return 'bg-primary'
    })

    // Check if all validations have passed - used to enable/disable submit button
    const canSubmit = computed(() => {
      // If contest has no byte count requirements, only URL validation is needed
      if (!contest.value || (!contest.value.min_byte_count && !contest.value.max_byte_count)) {
        return validationChecklist[0].checked
      }
      // If contest has byte count requirements, both checks must pass
      return validationChecklist[0].checked && validationChecklist[1].checked
    })

    // Validate article before submission
    // showProgress: if true, shows progress indicators; if false, just updates checklist silently
    const validateArticle = async (showProgress = true) => {
      // Reset checklist
      validationChecklist[0].checked = false
      validationChecklist[0].detail = null
      validationChecklist[1].checked = false
      validationChecklist[1].detail = null

      // Check 1: Validate URL format
      if (!formData.article_link.trim()) {
        validationChecklist[0].checked = false
        validationChecklist[0].detail = 'URL is required'
        return false
      }
      if (!formData.article_link.startsWith('http://') && !formData.article_link.startsWith('https://')) {
        validationChecklist[0].checked = false
        validationChecklist[0].detail = 'URL must start with http:// or https://'
        return false
      }

      // URL is valid
      validationChecklist[0].checked = true
      validationChecklist[0].detail = 'Valid URL format'

      // Check 2: Fetch article info and validate byte count
      try {
        if (showProgress) {
          submissionProgress.stage = 'fetching'
        }
        // Note: baseURL is already '/api', so we use '/mediawiki/article-info' not '/api/mediawiki/article-info'
        // Make API call to fetch article information
        const articleInfo = await api.get('/mediawiki/article-info', {
          params: { url: formData.article_link.trim() }
        })

        // Check if API returned an error in the response
        if (articleInfo.error) {
          throw new Error(articleInfo.error)
        }

        // Get byte count from article info (word_count is actually byte count)
        const articleByteCount = articleInfo.word_count || articleInfo.size || null
        submissionProgress.articleByteCount = articleByteCount

        // Check if contest has byte count requirements
        // If contest is not loaded yet, try to load it
        if (!contest.value || !submissionProgress.contestByteRequirements) {
          await loadContest()
        }

        const req = submissionProgress.contestByteRequirements

        // If article byte count is null, we can't validate
        if (articleByteCount === null) {
          validationChecklist[1].checked = false
          validationChecklist[1].detail = 'Could not determine article size'
          return false
        }

        // Validate byte count against contest requirements
        // Only validate if contest has byte count requirements
        if (req && (req.min !== null || req.max !== null)) {
          let isValid = true
          let errorMessage = null

          // Check minimum byte count - show exact error message matching backend format
          if (req.min !== null && articleByteCount < req.min) {
            isValid = false
            errorMessage = `Article byte count (${articleByteCount.toLocaleString()}) is below the minimum required (${req.min.toLocaleString()} bytes)`
          }
          // Check maximum byte count - show exact error message matching backend format
          if (req.max !== null && articleByteCount > req.max) {
            isValid = false
            errorMessage = `Article byte count (${articleByteCount.toLocaleString()}) exceeds the maximum allowed (${req.max.toLocaleString()} bytes)`
          }

          if (isValid) {
            validationChecklist[1].checked = true
            const minText = req.min ? `min: ${req.min.toLocaleString()}` : ''
            const maxText = req.max ? `max: ${req.max.toLocaleString()}` : ''
            const rangeText = [minText, maxText].filter(Boolean).join(', ')
            validationChecklist[1].detail = `${articleByteCount.toLocaleString()} bytes (Required: ${rangeText})`
            return true
          } else {
            validationChecklist[1].checked = false
            // Show the exact error message with article byte count
            validationChecklist[1].detail = errorMessage
            return false
          }
        } else {
          // No byte count requirements
          validationChecklist[1].checked = true
          validationChecklist[1].detail = `${articleByteCount.toLocaleString()} bytes (No restrictions)`
          return true
        }
      } catch (err) {
        validationChecklist[1].checked = false
        if (showProgress) {
          submissionProgress.stage = 'error'
        }

        // Provide better error messages based on error type
        let errorMsg = 'Failed to fetch article information'

        // Check for different error types
        const status = err.status || err.response?.status
        const errorData = err.response?.data || {}
        const errorMessage = errorData.error || err.message || ''

        // Log error for debugging
        console.error('Article validation error:', {
          status,
          message: errorMessage,
          error: err
        })

        if (status === 404) {
          // Check if it's an article not found or endpoint issue
          if (errorMessage.toLowerCase().includes('article not found') ||
              errorMessage.toLowerCase().includes('page not found')) {
            errorMsg = 'Article not found - please check the URL'
          } else {
            errorMsg = 'Article not found or endpoint unavailable'
          }
        } else if (status === 0 || err.message?.includes('Network Error') ||
                   err.message?.includes('Failed to fetch') ||
                   err.message?.includes('Network request failed')) {
          errorMsg = 'Network error - please check your connection'
        } else if (status === 502 || status === 503 || status === 504) {
          errorMsg = 'Server error - please try again later'
        } else if (errorMessage) {
          // Use the actual error message from the API
          errorMsg = errorMessage
        } else if (err.message) {
          errorMsg = err.message
        }

        validationChecklist[1].detail = errorMsg
        return false
      }
    }

    const handleSubmit = async () => {
      // Clear any previous errors
      error.value = ''

      // Check if validation has already passed - if so, skip re-validation
      // This prevents UI freezing by avoiding duplicate API calls
      const alreadyValidated = canSubmit.value

      if (!alreadyValidated) {
        // Validation hasn't passed yet, show error
        const failedChecks = validationChecklist.filter(item => !item.checked)
        if (failedChecks.length > 0) {
          error.value = `Validation failed: ${failedChecks.map(item => item.label).join(', ')}`
        } else {
          error.value = 'Please wait for validation to complete or check the requirements.'
        }
        return
      }

      // Set loading state immediately to prevent multiple clicks
      loading.value = true
      submissionProgress.stage = 'submitting'

      try {
        // Submit the article directly since validation already passed
        // No need to re-validate - we already checked when URL was entered
        await api.post(`/contest/${props.contestId}/submit`, {
          article_link: formData.article_link.trim()
        })

        // Success - update stage
        submissionProgress.stage = 'success'

        // Reset loading state immediately
        loading.value = false

        showAlert('Article submitted successfully!', 'success')

        // Emit event to parent to refresh data
        emit('submitted')

        // Close modal immediately and reset
        const modalElement = document.getElementById('submitArticleModal')
        const modal = bootstrap.Modal.getInstance(modalElement)
        if (modal) {
          modal.hide()
        }

        // Reset form and progress immediately
        formData.article_link = ''
        submissionProgress.stage = 'idle'
        submissionProgress.articleByteCount = null
        validationChecklist[0].checked = false
        validationChecklist[0].detail = null
        validationChecklist[1].checked = false
        validationChecklist[1].detail = null
        error.value = ''
      } catch (err) {
        submissionProgress.stage = 'error'

        // Extract error message from response
        const errorData = err.response?.data || {}
        const errorMessage = errorData.error || err.message || 'Failed to submit article'

        // Build detailed error message
        let detailedError = errorMessage
        if (errorData.details) {
          detailedError += `\n\nDetails: ${errorData.details}`
        }
        if (errorData.error_type) {
          detailedError += `\n\nError Type: ${errorData.error_type}`
        }
        if (errorData.traceback && process.env.NODE_ENV === 'development') {
          detailedError += `\n\nTraceback:\n${errorData.traceback}`
        }

        // Log full error for debugging
        console.error('Submission error:', {
          status: err.response?.status,
          error: errorData,
          fullError: err
        })

        error.value = detailedError

        // If error is about byte count, update validation checklist
        if (errorMessage.toLowerCase().includes('byte count')) {
          // Mark byte count validation as failed
          validationChecklist[1].checked = false
          validationChecklist[1].detail = errorMessage
          // Try to extract byte count from error if available
          const byteMatch = errorMessage.match(/(\d+)\s*bytes?/i)
          if (byteMatch) {
            submissionProgress.articleByteCount = parseInt(byteMatch[1])
          }
        }

        showAlert(error.value, 'danger')
      } finally {
        loading.value = false
      }
    }

    return {
      formData,
      loading,
      error,
      handleSubmit,
      submissionProgress,
      progressSteps,
      progressPercentage,
      progressBarClass,
      contest,
      validationChecklist,
      canSubmit
    }
  }
}
</script>

<style scoped>
/* Submit Article Modal Styling with Wikipedia Colors */

/* Modal header - solid color, no gradient - matches theme */
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
  color: white;
}

.modal-header .btn-close {
  filter: invert(1) brightness(1.2);
  opacity: 0.9;
  transition: opacity 0.2s ease;
}

.modal-header .btn-close:hover {
  opacity: 1;
}

/* Form styling */
.form-label {
  color: var(--wiki-dark);
  font-weight: 500;
  margin-bottom: 0.5rem;
  transition: color 0.3s ease;
}

.form-label .text-primary {
  color: var(--wiki-primary) !important;
}

/* Text danger - MediaWiki red */
.form-label .text-danger {
  color: var(--wiki-danger) !important;
}

/* Ensure proper MediaWiki red in dark mode */
[data-theme="dark"] .form-label .text-danger {
  color: #990000 !important;
}

.form-control {
  border-color: var(--wiki-input-border);
  background-color: var(--wiki-input-bg);
  color: var(--wiki-text);
  transition: all 0.2s ease;
}

.form-control:focus {
  border-color: var(--wiki-primary);
  box-shadow: 0 0 0 0.2rem rgba(0, 102, 153, 0.25);
  background-color: var(--wiki-input-bg);
  color: var(--wiki-text);
}

[data-theme="dark"] .form-control:focus {
  box-shadow: 0 0 0 0.2rem rgba(93, 184, 230, 0.3);
}

/* Alert styling */
.alert-danger {
  background-color: rgba(153, 0, 0, 0.1);
  border: 1px solid var(--wiki-danger);
  border-left: 4px solid var(--wiki-danger);
  color: var(--wiki-danger);
  border-radius: 0.5rem;
  transition: background-color 0.3s ease, border-color 0.3s ease, color 0.3s ease;
}

[data-theme="dark"] .alert-danger {
  background-color: rgba(230, 128, 128, 0.2);
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
  transform: translateY(-1px);
  box-shadow: 0 2px 4px rgba(0, 102, 153, 0.3);
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

/* Modal body - matches theme */
.modal-body {
  padding: 1.5rem;
  background-color: var(--wiki-modal-bg);
  color: var(--wiki-text);
  transition: background-color 0.3s ease, color 0.3s ease;
}

/* Modal footer - matches theme */
.modal-footer {
  border-top: 1px solid var(--wiki-border);
  padding: 1rem 1.5rem;
  background-color: var(--wiki-modal-bg);
  transition: background-color 0.3s ease, border-color 0.3s ease;
}

/* Modal content - ensures proper background */
.modal-content {
  background-color: var(--wiki-modal-bg);
  border-color: var(--wiki-border);
  transition: background-color 0.3s ease, border-color 0.3s ease;
}

/* Icon styling */
.fas {
  transition: transform 0.2s ease;
}

.btn:hover .fas {
  transform: scale(1.1);
}

/* Spinner */
.spinner-border-sm {
  width: 1rem;
  height: 1rem;
  border-width: 0.15em;
  border-color: currentColor;
  border-right-color: transparent;
}

/* Progress Indicator Styling */
.progress-steps {
  font-size: 0.9rem;
}

.progress-step {
  padding: 0.5rem;
  border-radius: 0.25rem;
  transition: all 0.3s ease;
}

.progress-step.active {
  background-color: rgba(0, 102, 153, 0.1);
  font-weight: 500;
}

.progress-step.completed {
  color: #28a745;
}

.progress-step.completed .fas {
  color: #28a745 !important;
}

.progress-step.failed {
  color: #dc3545;
}

.progress-step.failed .fas {
  color: #dc3545 !important;
}

.progress-step .fas {
  transition: color 0.3s ease;
}

/* Progress bar styling */
.progress {
  background-color: rgba(0, 102, 153, 0.1);
  border-radius: 0.5rem;
  overflow: hidden;
}

.progress-bar {
  transition: width 0.6s ease;
  font-weight: 500;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* Card styling for progress */
.card.border-primary {
  border-color: var(--wiki-primary) !important;
  background-color: var(--wiki-card-bg);
  transition: background-color 0.3s ease;
}

.card-title {
  color: var(--wiki-text);
  font-weight: 600;
}

[data-theme="dark"] .progress-step.active {
  background-color: rgba(93, 184, 230, 0.15);
}

[data-theme="dark"] .progress {
  background-color: rgba(93, 184, 230, 0.1);
}

/* Validation Checklist Styling */
.form-check {
  padding: 0.75rem;
  border-radius: 0.25rem;
  transition: background-color 0.2s ease;
}

.form-check:hover {
  background-color: rgba(0, 102, 153, 0.05);
}

[data-theme="dark"] .form-check:hover {
  background-color: rgba(93, 184, 230, 0.1);
}

.form-check-input {
  margin-top: 0.35rem;
  cursor: not-allowed;
}

.form-check-label {
  cursor: default;
  display: flex;
  align-items: center;
  font-weight: 500;
  transition: color 0.2s ease;
}

.form-check-label.text-success {
  color: #28a745 !important;
}

.form-check-label.text-muted {
  color: var(--wiki-text-muted) !important;
}

.form-check-label .fas {
  font-size: 1rem;
  transition: transform 0.2s ease;
}

.form-check-label.text-success .fas {
  color: #28a745 !important;
}

.card.border-primary .card-body {
  padding: 1rem;
  background-color: var(--wiki-card-bg);
  transition: background-color 0.3s ease;
}
</style>

