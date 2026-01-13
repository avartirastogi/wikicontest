<template>
  <!-- Modal for jury members to review and score submissions -->
  <div class="modal fade"
id="reviewSubmissionModal"
tabindex="-1"
data-bs-backdrop="static"
data-bs-keyboard="false">
    <div class="modal-dialog modal-dialog-centered modal-lg review-dialog">
      <div class="modal-content review-modal">

        <!-- Modal header with jury icon -->
        <div class="modal-header">
          <h5 class="modal-title">
            <i class="fas fa-gavel me-2"></i>Review Submission
          </h5>
          <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
        </div>

        <!-- Main review form content -->
        <div class="modal-body">

          <!-- Accept/Reject decision selector -->
          <div class="mb-4">
            <label class="form-label fw-semibold">Decision</label>
            <div class="decision-options">
              <!-- Accept option card -->
              <label class="decision-card accept" :class="{ 'selected': status === 'accepted' }">
                <input type="radio" value="accepted" v-model="status" />
                <span>
                  <i class="fas fa-check-circle me-2"></i>
                  Accept
                </span>
              </label>

              <!-- Reject option card -->
              <label class="decision-card reject" :class="{ 'selected': status === 'rejected' }">
                <input type="radio" value="rejected" v-model="status" />
                <span>
                  <i class="fas fa-times-circle me-2"></i>
                  Reject
                </span>
              </label>
            </div>
          </div>

          <!-- Multi-parameter scoring interface (when enabled and accepted) -->
          <div v-if="isMultiParameterEnabled && status === 'accepted'" class="parameter-scoring-section">
            <!-- Loop through each scoring parameter -->
            <div v-for="param in scoringParams" :key="param.name" class="parameter-slider mb-4">
              <!-- Parameter name, weight badge, and current score -->
              <div class="d-flex justify-content-between align-items-center mb-2">
                <div>
                  <strong>{{ param.name }}</strong>
                  <span class="badge bg-primary ms-2">{{ param.weight }}%</span>
                </div>
                <div class="score-display">
                  <span class="score-value">{{ parameterScores[param.name] || 0 }}</span>
                  <span class="score-max">/10</span>
                </div>
              </div>

              <!-- Slider input for parameter score (0-10) -->
              <input type="range"
class="form-range parameter-range"
min="0"
max="10"
step="1"
                v-model.number="parameterScores[param.name]"/>

              <!-- Optional parameter description -->
              <small v-if="param.description" class="text-muted d-block mt-1">
                {{ param.description }}
              </small>
            </div>

            <!-- Final calculated score preview with breakdown -->
            <div class="final-score-preview p-3 rounded mt-3">
              <div class="d-flex justify-content-between align-items-center">
                <div>
                  <i class="fas fa-calculator me-2"></i>
                  <strong>Calculated Score:</strong>
                </div>
                <div class="final-score">
                  {{ calculatedScore }}<span class="text-muted">/{{ maxScore }}</span>
                </div>
              </div>

              <!-- Show how each parameter contributes to final score -->
              <div class="score-breakdown mt-2">
                <small class="text-muted">
                  <div v-for="param in scoringParams" :key="param.name">
                    {{ param.name }}: {{ parameterScores[param.name] || 0 }} × {{ param.weight }}% =
                    {{ ((parameterScores[param.name] || 0) * param.weight / 100).toFixed(1) }} points
                  </div>
                </small>
              </div>
            </div>
          </div>

          <!-- Simple score input (when multi-parameter is disabled and accepted) -->
          <div v-else-if="!isMultiParameterEnabled && status === 'accepted'" class="mb-4">
            <label class="form-label fw-semibold">
              Points to be Awarded
            </label>
            <input type="number"
class="form-control"
v-model.number="simpleScore"
min="0"
:max="maxScore"
              placeholder="Enter score" />
          </div>

          <!-- Info message when submission is rejected -->
          <div v-else-if="status === 'rejected'" class="alert alert-warning">
            <i class="fas fa-info-circle me-2"></i>
            Rejected submissions receive 0 points
          </div>

          <!-- Optional overall comment field (always visible) -->
          <div class="mt-4">
            <label class="form-label fw-semibold">
              Overall Comment
              <span class="text-muted">(optional)</span>
            </label>
            <textarea class="form-control"
rows="4"
v-model="overallComment"
              placeholder="Provide overall feedback for the participant..."></textarea>
          </div>
        </div>

        <!-- Modal footer with action buttons -->
        <div class="modal-footer">
          <!-- Cancel button to close modal -->
          <button class="btn btn-secondary" data-bs-dismiss="modal">
            <i class="fas fa-times me-2"></i>Cancel
          </button>

          <!-- Submit review button (disabled when invalid) -->
          <button class="btn btn-success" :disabled="submitting || !status || !canSubmit" @click="submitReview">
            <span v-if="submitting" class="spinner-border spinner-border-sm me-2"></span>
            <i v-else class="fas fa-check me-2"></i>
            {{ submitting ? 'Submitting...' : 'Submit Review' }}
          </button>
        </div>

      </div>
    </div>
  </div>
</template>

<script>
import { ref, watch, computed, onMounted } from 'vue'

// Helper function to get CSRF token from cookies
function getCookie(name) {
  return document.cookie
    .split('; ')
    .find(row => row.startsWith(name + '='))
    ?.split('=')[1]
}

export default {
  name: 'ReviewSubmissionModal',
  props: {
    submissionId: {
      type: Number,
      required: true
    },
    contestScoringConfig: {
      type: Object,
      default: null
    }
  },
  emits: ['reviewed'],

  setup(props, { emit }) {
    // Form state variables
    const status = ref('')
    const simpleScore = ref(null)
    const overallComment = ref('')
    const submitting = ref(false)
    const parameterScores = ref({})
    const parameterComments = ref({})

    // Check if multi-parameter scoring is enabled for this contest
    const isMultiParameterEnabled = computed(() => {
      return props.contestScoringConfig?.enabled === true
    })

    // Get list of scoring parameters from contest config
    const scoringParams = computed(() => {
      return props.contestScoringConfig?.parameters || []
    })

    // Maximum possible score for this contest
    const maxScore = computed(() => {
      return props.contestScoringConfig?.max_score || 100
    })

    // Minimum possible score for this contest
    const minScore = computed(() => {
      return props.contestScoringConfig?.min_score || 0
    })

    // Calculate weighted final score from individual parameter scores
    const calculatedScore = computed(() => {
      if (!isMultiParameterEnabled.value) return 0

      let weightedSum = 0
      scoringParams.value.forEach(param => {
        const score = parameterScores.value[param.name] || 0
        const weight = param.weight / 100
        weightedSum += score * weight
      })

      // Scale from 0-10 range to max score range
      return Math.round(weightedSum * (maxScore.value / 10))
    })

    // Validate if form can be submitted
    const canSubmit = computed(() => {
      if (!status.value) return false
      if (status.value === 'rejected') return true

      // For multi-parameter scoring, all parameters must have scores
      if (isMultiParameterEnabled.value) {
        return scoringParams.value.every(param =>
          parameterScores.value[param.name] !== undefined &&
          parameterScores.value[param.name] !== null
        )
      } else {
        // For simple scoring, score must be valid number
        return simpleScore.value !== null && simpleScore.value !== undefined && simpleScore.value >= 0
      }
    })

    // Initialize parameter scores when config changes
    watch(() => props.contestScoringConfig, (config) => {
      if (config?.enabled) {
        config.parameters.forEach(param => {
          if (!(param.name in parameterScores.value)) {
            parameterScores.value[param.name] = 0
          }
        })
      }
    }, { immediate: true, deep: true })

    // Reset score to 0 when status changes to rejected
    watch(status, (newStatus) => {
      if (newStatus === 'rejected') {
        simpleScore.value = 0
      }
    })

    // Submit review to API
    const submitReview = async () => {
      submitting.value = true

      try {
        const csrfToken = getCookie('csrf_access_token')

        // Build base payload with status and comment
        const payload = {
          status: status.value,
          comment: overallComment.value
        }

        // Add score data for accepted submissions
        if (status.value === 'accepted') {
          if (isMultiParameterEnabled.value) {
            // Include parameter scores and calculated total
            payload.parameter_scores = { ...parameterScores.value }
            payload.score = calculatedScore.value
          } else {
            // Include simple score only
            payload.score = simpleScore.value
          }
        }

        // Send PUT request to review endpoint
        const res = await fetch(
          `/api/submission/${props.submissionId}/review`,
          {
            method: 'PUT',
            credentials: 'include',
            headers: {
              'Content-Type': 'application/json',
              'X-CSRF-TOKEN': csrfToken
            },
            body: JSON.stringify(payload)
          }
        )

        if (!res.ok) {
          const text = await res.text()
          throw new Error(text)
        }

        // Determine final score for emit event
        const finalScore = isMultiParameterEnabled.value
          ? calculatedScore.value
          : (status.value === 'accepted' ? simpleScore.value : 0)

        // Emit reviewed event to parent component
        emit('reviewed', {
          submissionId: props.submissionId,
          status: status.value,
          score: finalScore,
          comment: overallComment.value,
          parameter_scores: isMultiParameterEnabled.value ? parameterScores.value : null
        })

        // Close modal programmatically
        const modalEl = document.getElementById('reviewSubmissionModal')
        const modalInstance = bootstrap.Modal.getInstance(modalEl)
        if (modalInstance) {
          modalInstance.hide()
        }

        resetForm()
      } catch (err) {
        alert('Failed to submit review: ' + err.message)
      } finally {
        submitting.value = false
      }
    }

    // Reset all form fields to initial state
    const resetForm = () => {
      status.value = ''
      simpleScore.value = null
      overallComment.value = ''
      parameterScores.value = {}
      parameterComments.value = {}
    }

    // Set up modal event listeners on mount
    onMounted(() => {
      const modal = document.getElementById('reviewSubmissionModal')
      if (!modal) return

      // Initialize parameter scores when modal is shown
      modal.addEventListener('shown.bs.modal', () => {
        if (isMultiParameterEnabled.value) {
          scoringParams.value.forEach(param => {
            if (!(param.name in parameterScores.value)) {
              parameterScores.value[param.name] = 0
            }
          })
        }
      })

      // Reset form when modal is hidden
      modal.addEventListener('hidden.bs.modal', () => {
        resetForm()
      })
    })

    return {
      status,
      simpleScore,
      overallComment,
      submitting,
      parameterScores,
      parameterComments,
      isMultiParameterEnabled,
      scoringParams,
      maxScore,
      minScore,
      calculatedScore,
      canSubmit,
      submitReview
    }
  }
}
</script>

<style scoped>
/* Maximum width for review dialog */
.review-dialog {
  max-width: 700px;
}

/* Modal container with rounded corners and shadow */
.review-modal {
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  border: 1px solid var(--wiki-border);
}

/* Dark mode: stronger shadow */
[data-theme="dark"] .review-modal {
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.6);
}

/* Header with Wikipedia blue background */
.modal-header {
  background: var(--wiki-primary);
  color: white;
  border-bottom: none;
  padding: 1.5rem;
}

/* Modal title with custom font styling */
.modal-title {
  font-weight: 600;
  font-size: 1.35rem;
  letter-spacing: -0.01em;
  display: flex;
  align-items: center;
}

/* Slightly transparent icon */
.modal-title i {
  opacity: 0.9;
}

/* White close button with hover effects */
.btn-close {
  filter: brightness(0) invert(1);
  opacity: 0.8;
  transition: opacity 0.2s ease, transform 0.2s ease;
}

.btn-close:hover {
  opacity: 1;
  transform: scale(1.1);
}

/* Modal body with theme-aware background */
.modal-body {
  padding: 2rem;
  background-color: var(--wiki-card-bg);
}

/* Dark mode: darker background */
[data-theme="dark"] .modal-body {
  background-color: #1a1a1a;
}

/* Two-column grid for decision cards */
.decision-options {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
  margin-top: 0.5rem;
}

/* Individual decision card with smooth transitions */
.decision-card {
  position: relative;
  padding: 1.5rem;
  border: 2px solid var(--wiki-border);
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  text-align: center;
  background-color: white;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.06);
}

/* Dark mode: darker card background */
[data-theme="dark"] .decision-card {
  background-color: #2a2a2a;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.3);
}

/* Hide actual radio input (custom styling applied to label) */
.decision-card input[type="radio"] {
  position: absolute;
  opacity: 0;
  pointer-events: none;
}

/* Card text styling with icon */
.decision-card span {
  font-weight: 600;
  font-size: 1.125rem;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--wiki-text);
  transition: color 0.25s ease;
}

/* Icon with scale transition */
.decision-card i {
  font-size: 1.35rem;
  transition: transform 0.25s ease;
}

/* Hover effect: lift card with shadow */
.decision-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.12);
}

/* Dark mode: stronger hover shadow */
[data-theme="dark"] .decision-card:hover {
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.4);
}

/* Accept card hover: green tint */
.decision-card.accept:hover {
  border-color: rgba(40, 167, 69, 0.5);
  background-color: rgba(40, 167, 69, 0.03);
}

/* Reject card hover: red tint */
.decision-card.reject:hover {
  border-color: rgba(220, 53, 69, 0.5);
  background-color: rgba(220, 53, 69, 0.03);
}

/* Selected state: thicker border and lift */
.decision-card.selected {
  border-width: 2.5px;
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.15);
}

/* Dark mode: stronger selected shadow */
[data-theme="dark"] .decision-card.selected {
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.5);
}

/* Accept selected: green gradient background */
.decision-card.accept.selected {
  border-color: #28a745;
  background: linear-gradient(135deg, rgba(40, 167, 69, 0.08), rgba(40, 167, 69, 0.03));
}

/* Accept selected: green text */
.decision-card.accept.selected span {
  color: #28a745;
}

/* Accept selected: scale up icon */
.decision-card.accept.selected i {
  transform: scale(1.1);
}

/* Reject selected: red gradient background */
.decision-card.reject.selected {
  border-color: #dc3545;
  background: linear-gradient(135deg, rgba(220, 53, 69, 0.08), rgba(220, 53, 69, 0.03));
}

/* Reject selected: red text */
.decision-card.reject.selected span {
  color: #dc3545;
}

/* Reject selected: scale up icon */
.decision-card.reject.selected i {
  transform: scale(1.1);
}

/* Accessibility: focus outline for keyboard navigation */
.decision-card:focus-within {
  outline: 3px solid var(--wiki-primary);
  outline-offset: 3px;
}

/* Container for multi-parameter scoring interface */
.parameter-scoring-section {
  background: var(--wiki-hover-bg);
  padding: 1.5rem;
}

/* Dark mode: darker section background */
[data-theme="dark"] .parameter-scoring-section {
  background: #222;
}

/* Section label styling */
.parameter-scoring-section .form-label {
  font-size: 1.125rem;
  color: var(--wiki-dark);
  margin-bottom: 1.25rem;
}

/* Dark mode: white label text */
[data-theme="dark"] .parameter-scoring-section .form-label {
  color: #fff;
}

/* Individual parameter card with hover effect */
.parameter-slider {
  background: white;
  padding: 1rem;
  border-radius: 10px;
  border: 1px solid var(--wiki-border);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  transition: box-shadow 0.2s ease, transform 0.2s ease;
}

/* Dark mode: darker parameter card */
[data-theme="dark"] .parameter-slider {
  background: #2a2a2a;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

/* Hover: stronger shadow and lift */
.parameter-slider:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  transform: translateY(-1px);
}

/* Dark mode: stronger hover shadow */
[data-theme="dark"] .parameter-slider:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}

/* Parameter name styling */
.parameter-slider strong {
  font-size: 1.05rem;
  color: var(--wiki-dark);
}

/* Dark mode: white parameter name */
[data-theme="dark"] .parameter-slider strong {
  color: #fff;
}

/* Weight percentage badge */
.parameter-slider .badge {
  font-size: 0.8rem;
  font-weight: 600;
  padding: 0.35rem 0.65rem;
}

/* Large score display with tabular numbers */
.score-display {
  font-size: 1.75rem;
  font-weight: 700;
  color: var(--wiki-primary);
  font-variant-numeric: tabular-nums;
  letter-spacing: -0.02em;
}

/* Current score value */
.score-value {
  color: var(--wiki-primary);
}

/* Maximum score indicator */
.score-max {
  color: var(--wiki-text-muted);
  font-size: 1.15rem;
  font-weight: 500;
}

/* Range slider base styling */
.parameter-range {
  width: 100%;
  height: 8px;
  border-radius: 6px;
  cursor: pointer;
  background: #e9ecef;
  outline: none;
  transition: background 0.2s ease;
}

/* Dark mode: darker slider track */
[data-theme="dark"] .parameter-range {
  background: #3a3a3a;
}

/* Hover: slightly darker track */
.parameter-range:hover {
  background: #dee2e6;
}

/* Dark mode: hover state */
[data-theme="dark"] .parameter-range:hover {
  background: #444;
}

/* Focus: blue outline for accessibility */
.parameter-range:focus {
  box-shadow: 0 0 0 3px rgba(0, 102, 153, 0.2);
}

/* Webkit browsers: custom slider thumb */
.parameter-range::-webkit-slider-thumb {
  appearance: none;
  width: 26px;
  height: 26px;
  background: var(--wiki-primary);
  border-radius: 50%;
  cursor: grab;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 2px 8px rgba(0, 102, 153, 0.3);
  border: 3px solid white;
  margin-top: -9px;
}

/* Thumb hover: scale up */
.parameter-range::-webkit-slider-thumb:hover {
  transform: scale(1.15);
  box-shadow: 0 4px 12px rgba(0, 102, 153, 0.4);
}

/* Thumb active: grabbing cursor */
.parameter-range::-webkit-slider-thumb:active {
  cursor: grabbing;
  transform: scale(1.05);
}

/* Firefox: custom slider thumb */
.parameter-range::-moz-range-thumb {
  width: 26px;
  height: 26px;
  background: var(--wiki-primary);
  border-radius: 50%;
  cursor: grab;
  border: 3px solid white;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 2px 8px rgba(0, 102, 153, 0.3);
}

/* Firefox thumb hover */
.parameter-range::-moz-range-thumb:hover {
  transform: scale(1.15);
  box-shadow: 0 4px 12px rgba(0, 102, 153, 0.4);
}

/* Firefox thumb active */
.parameter-range::-moz-range-thumb:active {
  cursor: grabbing;
  transform: scale(1.05);
}

/* Final score preview card with gradient background */
.final-score-preview {
  background: linear-gradient(135deg,
      rgba(0, 102, 153, 0.08),
      rgba(0, 102, 153, 0.03));
  border: 2px solid var(--wiki-primary);
  border-radius: 12px;
  padding: 1.5rem;
  margin-top: 1.5rem;
  box-shadow: 0 4px 12px rgba(0, 102, 153, 0.08);
}

/* Dark mode: lighter gradient */
[data-theme="dark"] .final-score-preview {
  background: linear-gradient(135deg,
      rgba(93, 184, 230, 0.15),
      rgba(93, 184, 230, 0.08));
  box-shadow: 0 4px 12px rgba(93, 184, 230, 0.15);
}

/* Large final score display */
.final-score {
  font-size: 2.25rem;
  font-weight: 700;
  color: var(--wiki-primary);
  letter-spacing: -0.02em;
  font-variant-numeric: tabular-nums;
}

/* Maximum score in final display */
.final-score .text-muted {
  font-size: 1.5rem;
  font-weight: 600;
}

/* Breakdown section with top border */
.score-breakdown {
  border-top: 1px solid rgba(0, 102, 153, 0.15);
  padding-top: 1rem;
  margin-top: 1rem;
}

/* Breakdown text styling */
.score-breakdown small {
  font-size: 0.875rem;
  line-height: 1.6;
  opacity: 0.85;
}

/* Form label with semibold weight */
.form-label {
  font-weight: 600;
  font-size: 1.05rem;
  color: var(--wiki-dark);
  margin-bottom: 0.75rem;
  display: block;
}

/* Dark mode: white labels */
[data-theme="dark"] .form-label {
  color: #fff;
}

/* Form inputs with rounded borders */
.form-control,
textarea.form-control {
  border: 2px solid var(--wiki-border);
  border-radius: 8px;
  padding: 0.75rem 1rem;
  font-size: 1rem;
  background-color: white;
  color: var(--wiki-text);
  transition: all 0.2s ease;
}

/* Dark mode: darker input background */
[data-theme="dark"] .form-control,
[data-theme="dark"] textarea.form-control {
  background-color: #2a2a2a;
  color: #fff;
}

/* Input hover: highlight border */
.form-control:hover {
  border-color: rgba(0, 102, 153, 0.4);
}

/* Input focus: blue border and shadow */
.form-control:focus {
  border-color: var(--wiki-primary);
  box-shadow: 0 0 0 3px rgba(0, 102, 153, 0.12);
  background-color: white;
  outline: none;
}

/* Dark mode: focus state */
[data-theme="dark"] .form-control:focus {
  background-color: #2a2a2a;
}

/* Textarea with vertical resize */
textarea.form-control {
  resize: vertical;
  min-height: 120px;
  line-height: 1.6;
}

/* Helper text below inputs */
.form-text {
  font-size: 0.875rem;
  color: var(--wiki-text-muted);
  margin-top: 0.5rem;
  display: block;
}

/* Warning alert for rejected submissions */
.alert-warning {
  background-color: rgba(255, 193, 7, 0.08);
  border: 2px solid #ffc107;
  border-radius: 10px;
  color: #856404;
  padding: 1.25rem;
  font-size: 1rem;
  display: flex;
  align-items: center;
}

/* Dark mode: lighter warning background */
[data-theme="dark"] .alert-warning {
  background-color: rgba(255, 193, 7, 0.15);
  color: #ffecb3;
}

/* Warning icon */
.alert-warning i {
  font-size: 1.25rem;
}

/* Primary badge with Wikipedia blue */
.badge.bg-primary {
  background-color: var(--wiki-primary) !important;
  font-weight: 600;
  letter-spacing: 0.01em;
}

/* Modal footer with action buttons */
.modal-footer {
  border-top: 1px solid var(--wiki-border);
  padding: 1.25rem 2rem;
  background-color: var(--wiki-modal-bg);
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
}

/* Dark mode: darker footer */
[data-theme="dark"] .modal-footer {
  background-color: #1a1a1a;
}

/* Base button styling */
.btn {
  padding: 0.75rem 1.5rem;
  font-weight: 600;
  font-size: 1rem;
  border-radius: 8px;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border: none;
}

/* Button icon transition */
.btn i {
  transition: transform 0.2s ease;
}

/* Success button: green background */
.btn-success {
  background-color: #28a745;
  color: white;
  box-shadow: 0 2px 8px rgba(40, 167, 69, 0.2);
}

/* Success button hover: lift and shadow */
.btn-success:hover:not(:disabled) {
  background-color: #218838;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(40, 167, 69, 0.3);
}

/* Hover: scale icon */
.btn-success:hover:not(:disabled) i {
  transform: scale(1.1);
}

/* Success button active: reset position */
.btn-success:active:not(:disabled) {
  transform: translateY(0);
}
/* Disabled success button styling */
.btn-success:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  background-color: #28a745;
  box-shadow: none;
}

/* Secondary button: gray background */
.btn-secondary {
  background-color: #6c757d;
  color: white;
  box-shadow: 0 2px 8px rgba(108, 117, 125, 0.2);
}


.btn-secondary:hover {
  background-color: #5a6268;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(108, 117, 125, 0.3);
}

.btn-secondary:active {
  transform: translateY(0);
}

.spinner-border-sm {
  width: 1rem;
  height: 1rem;
  border-width: 0.15em;
}

@media (max-width: 768px) {
  .review-dialog {
    margin: 1rem;
  }

  .modal-header {
    padding: 1.25rem 1.5rem;
  }

  .modal-title {
    font-size: 1.2rem;
  }

  .modal-body {
    padding: 1.5rem;
  }

  .decision-options {
    grid-template-columns: 1fr;
    gap: 0.75rem;
  }

  .decision-card {
    padding: 1.5rem 1.25rem;
  }

  .decision-card span {
    font-size: 1.05rem;
  }

  .parameter-scoring-section {
    padding: 1.25rem;
  }

  .parameter-slider {
    padding: 1rem;
  }

  .score-display {
    font-size: 1.5rem;
  }

  .final-score {
    font-size: 1.85rem;
  }

  .modal-footer {
    padding: 1rem 1.5rem;
    flex-direction: column-reverse;
  }

  .btn {
    width: 100%;
  }
}

@media (max-width: 480px) {
  .modal-body {
    padding: 1.25rem;
  }

  .decision-card i {
    font-size: 1.2rem;
  }

  .parameter-slider strong {
    font-size: 0.95rem;
  }

  .score-display {
    font-size: 1.35rem;
  }

  .final-score {
    font-size: 1.65rem;
  }
}

@media (prefers-reduced-motion: reduce) {

  *,
  *::before,
  *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}

/* Focus visible for keyboard navigation */
*:focus-visible {
  outline: 3px solid var(--wiki-primary);
  outline-offset: 2px;
}

/* Screen reader only content */
.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border-width: 0;
}
</style>
