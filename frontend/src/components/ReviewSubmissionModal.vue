<template>
  <div class="modal fade" id="reviewSubmissionModal" tabindex="-1" data-bs-backdrop="static" data-bs-keyboard="false">
    <div class="modal-dialog modal-dialog-centered modal-lg review-dialog">
      <div class="modal-content review-modal">

        <!-- Header -->
        <div class="modal-header">
          <h5 class="modal-title">
            <i class="fas fa-gavel me-2"></i>Review Submission
          </h5>
          <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
        </div>

        <!-- Body -->
        <div class="modal-body">

          <!-- Decision -->
          <div class="mb-4">
            <label class="form-label fw-semibold">Decision</label>
            <div class="decision-options">
              <label class="decision-card accept" :class="{ 'selected': status === 'accepted' }">
                <input type="radio" value="accepted" v-model="status" />
                <span>
                  <i class="fas fa-check-circle me-2"></i>
                  Accept
                </span>
              </label>

              <label class="decision-card reject" :class="{ 'selected': status === 'rejected' }">
                <input type="radio" value="rejected" v-model="status" />
                <span>
                  <i class="fas fa-times-circle me-2"></i>
                  Reject
                </span>
              </label>
            </div>
          </div>

          <!-- NEW: Multi-Parameter Scoring (if enabled) -->
          <div v-if="isMultiParameterEnabled && status === 'accepted'" class="parameter-scoring-section">
            <!-- Loop through each parameter -->
            <div v-for="param in scoringParams" :key="param.name" class="parameter-slider mb-4">
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

              <!-- Slider -->
              <input type="range" class="form-range parameter-range" min="0" max="10" step="1"
                v-model.number="parameterScores[param.name]">

              <!-- Description -->
              <small v-if="param.description" class="text-muted d-block mt-1">
                {{ param.description }}
              </small>
            </div>

            <!-- Final Score Preview (OUTSIDE the loop) -->
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

              <!-- Score breakdown -->
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

          <!-- Simple score input (if multi-param is OFF) -->
          <div v-else-if="!isMultiParameterEnabled && status === 'accepted'" class="mb-4">
            <label class="form-label fw-semibold">
              Points to be Awarded
            </label>
            <input type="number" class="form-control" v-model.number="simpleScore" min="0" :max="maxScore"
              :placeholder="`Enter score (0-${maxScore})`" />
            <small class="form-text text-muted">
              Enter a score between 0 and {{ maxScore }} points.
            </small>
          </div>

          <!-- Rejected - No scoring -->
          <div v-else-if="status === 'rejected'" class="alert alert-warning">
            <i class="fas fa-info-circle me-2"></i>
            Rejected submissions receive 0 points
          </div>

          <!-- Overall Comment (OUTSIDE all scoring sections) -->
          <div class="mt-4">
            <label class="form-label fw-semibold">
              Overall Comment
              <span class="text-muted">(optional)</span>
            </label>
            <textarea class="form-control" rows="4" v-model="overallComment"
              placeholder="Provide overall feedback for the participant..."></textarea>
          </div>
        </div>

        <!-- Footer (OUTSIDE modal-body) -->
        <div class="modal-footer">
          <button class="btn btn-secondary" data-bs-dismiss="modal">
            <i class="fas fa-times me-2"></i>Cancel
          </button>

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
    const status = ref('')
    const simpleScore = ref(null)
    const overallComment = ref('')
    const submitting = ref(false)
    const parameterScores = ref({})
    const parameterComments = ref({})

    const isMultiParameterEnabled = computed(() => {
      return props.contestScoringConfig?.enabled === true
    })

    const scoringParams = computed(() => {
      return props.contestScoringConfig?.parameters || []
    })

    const maxScore = computed(() => {
      return props.contestScoringConfig?.max_score || 100
    })
    const minScore = computed(() => {
      return props.contestScoringConfig?.min_score || 0
    })

    const calculatedScore = computed(() => {
      if (!isMultiParameterEnabled.value) return 0

      let weightedSum = 0
      scoringParams.value.forEach(param => {
        const score = parameterScores.value[param.name] || 0
        const weight = param.weight / 100
        weightedSum += score * weight
      })

      return Math.round(weightedSum * (maxScore.value / 10))
    })

    const canSubmit = computed(() => {
      if (!status.value) return false
      if (status.value === 'rejected') return true

      if (isMultiParameterEnabled.value) {
        return scoringParams.value.every(param =>
          parameterScores.value[param.name] !== undefined &&
          parameterScores.value[param.name] !== null
        )
      } else {
        return simpleScore.value !== null && simpleScore.value !== undefined && simpleScore.value >= 0
      }
    })

    watch(() => props.contestScoringConfig, (config) => {
      if (config?.enabled) {
        config.parameters.forEach(param => {
          if (!(param.name in parameterScores.value)) {
            parameterScores.value[param.name] = 0
          }
        })
      }
    }, { immediate: true, deep: true })

    watch(status, (newStatus) => {
      if (newStatus === 'rejected') {
        simpleScore.value = 0
      }
    })

    const submitReview = async () => {
      submitting.value = true

      try {
        const csrfToken = getCookie('csrf_access_token')

        let payload = {
          status: status.value,
          comment: overallComment.value
        }

        if (status.value === 'accepted') {
          if (isMultiParameterEnabled.value) {
            payload.parameter_scores = { ...parameterScores.value }
            payload.score = calculatedScore.value
          } else {
            payload.score = simpleScore.value
          }
        }


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

        const finalScore = isMultiParameterEnabled.value
          ? calculatedScore.value
          : (status.value === 'accepted' ? simpleScore.value : 0)

        emit('reviewed', {
          submissionId: props.submissionId,
          status: status.value,
          score: finalScore,
          comment: overallComment.value,
          parameter_scores: isMultiParameterEnabled.value ? parameterScores.value : null
        })

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

    const resetForm = () => {
      status.value = ''
      simpleScore.value = null
      overallComment.value = ''
      parameterScores.value = {}
      parameterComments.value = {}
    }

    onMounted(() => {
      const modal = document.getElementById('reviewSubmissionModal')
      if (!modal) return

      modal.addEventListener('shown.bs.modal', () => {
        if (isMultiParameterEnabled.value) {
          scoringParams.value.forEach(param => {
            if (!(param.name in parameterScores.value)) {
              parameterScores.value[param.name] = 0
            }
          })
        }
      })

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
.review-dialog {
  max-width: 700px;
}

.review-modal {
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  border: 1px solid var(--wiki-border);
}

[data-theme="dark"] .review-modal {
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.6);
}

.modal-header {
  background: var(--wiki-primary);
  color: white;
  border-bottom: none;
  padding: 1.5rem;
}

.modal-title {
  font-weight: 600;
  font-size: 1.35rem;
  letter-spacing: -0.01em;
  display: flex;
  align-items: center;
}

.modal-title i {
  opacity: 0.9;
}

.btn-close {
  filter: brightness(0) invert(1);
  opacity: 0.8;
  transition: opacity 0.2s ease, transform 0.2s ease;
}

.btn-close:hover {
  opacity: 1;
  transform: scale(1.1);
}

.modal-body {
  padding: 2rem;
  background-color: var(--wiki-card-bg);
}

[data-theme="dark"] .modal-body {
  background-color: #1a1a1a;
}

.decision-options {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
  margin-top: 0.5rem;
}

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

[data-theme="dark"] .decision-card {
  background-color: #2a2a2a;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.3);
}

.decision-card input[type="radio"] {
  position: absolute;
  opacity: 0;
  pointer-events: none;
}

.decision-card span {
  font-weight: 600;
  font-size: 1.125rem;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--wiki-text);
  transition: color 0.25s ease;
}

.decision-card i {
  font-size: 1.35rem;
  transition: transform 0.25s ease;
}

/* Hover States */
.decision-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.12);
}

[data-theme="dark"] .decision-card:hover {
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.4);
}

.decision-card.accept:hover {
  border-color: rgba(40, 167, 69, 0.5);
  background-color: rgba(40, 167, 69, 0.03);
}

.decision-card.reject:hover {
  border-color: rgba(220, 53, 69, 0.5);
  background-color: rgba(220, 53, 69, 0.03);
}

/* Selected States */
.decision-card.selected {
  border-width: 2.5px;
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.15);
}

[data-theme="dark"] .decision-card.selected {
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.5);
}

.decision-card.accept.selected {
  border-color: #28a745;
  background: linear-gradient(135deg, rgba(40, 167, 69, 0.08), rgba(40, 167, 69, 0.03));
}

.decision-card.accept.selected span {
  color: #28a745;
}

.decision-card.accept.selected i {
  transform: scale(1.1);
}

.decision-card.reject.selected {
  border-color: #dc3545;
  background: linear-gradient(135deg, rgba(220, 53, 69, 0.08), rgba(220, 53, 69, 0.03));
}

.decision-card.reject.selected span {
  color: #dc3545;
}

.decision-card.reject.selected i {
  transform: scale(1.1);
}

/* Focus States for Accessibility */
.decision-card:focus-within {
  outline: 3px solid var(--wiki-primary);
  outline-offset: 3px;
}

.parameter-scoring-section {
  background: var(--wiki-hover-bg);
  padding: 1.5rem;
}

[data-theme="dark"] .parameter-scoring-section {
  background: #222;
}

.parameter-scoring-section .form-label {
  font-size: 1.125rem;
  color: var(--wiki-dark);
  margin-bottom: 1.25rem;
}

[data-theme="dark"] .parameter-scoring-section .form-label {
  color: #fff;
}

.parameter-slider {
  background: white;
  padding: 1rem;
  border-radius: 10px;
  border: 1px solid var(--wiki-border);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  transition: box-shadow 0.2s ease, transform 0.2s ease;
}

[data-theme="dark"] .parameter-slider {
  background: #2a2a2a;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

.parameter-slider:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  transform: translateY(-1px);
}

[data-theme="dark"] .parameter-slider:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}

.parameter-slider strong {
  font-size: 1.05rem;
  color: var(--wiki-dark);
}

[data-theme="dark"] .parameter-slider strong {
  color: #fff;
}

.parameter-slider .badge {
  font-size: 0.8rem;
  font-weight: 600;
  padding: 0.35rem 0.65rem;
}

/* Score Display */
.score-display {
  font-size: 1.75rem;
  font-weight: 700;
  color: var(--wiki-primary);
  font-variant-numeric: tabular-nums;
  letter-spacing: -0.02em;
}

.score-value {
  color: var(--wiki-primary);
}

.score-max {
  color: var(--wiki-text-muted);
  font-size: 1.15rem;
  font-weight: 500;
}

.parameter-range {
  width: 100%;
  height: 8px;
  border-radius: 6px;
  cursor: pointer;
  background: #e9ecef;
  outline: none;
  transition: background 0.2s ease;
}

[data-theme="dark"] .parameter-range {
  background: #3a3a3a;
}

.parameter-range:hover {
  background: #dee2e6;
}

[data-theme="dark"] .parameter-range:hover {
  background: #444;
}

.parameter-range:focus {
  box-shadow: 0 0 0 3px rgba(0, 102, 153, 0.2);
}

/* Webkit (Chrome, Safari, Edge) */
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

.parameter-range::-webkit-slider-thumb:hover {
  transform: scale(1.15);
  box-shadow: 0 4px 12px rgba(0, 102, 153, 0.4);
}

.parameter-range::-webkit-slider-thumb:active {
  cursor: grabbing;
  transform: scale(1.05);
}

/* Firefox */
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

.parameter-range::-moz-range-thumb:hover {
  transform: scale(1.15);
  box-shadow: 0 4px 12px rgba(0, 102, 153, 0.4);
}

.parameter-range::-moz-range-thumb:active {
  cursor: grabbing;
  transform: scale(1.05);
}

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

[data-theme="dark"] .final-score-preview {
  background: linear-gradient(135deg,
      rgba(93, 184, 230, 0.15),
      rgba(93, 184, 230, 0.08));
  box-shadow: 0 4px 12px rgba(93, 184, 230, 0.15);
}

.final-score {
  font-size: 2.25rem;
  font-weight: 700;
  color: var(--wiki-primary);
  letter-spacing: -0.02em;
  font-variant-numeric: tabular-nums;
}

.final-score .text-muted {
  font-size: 1.5rem;
  font-weight: 600;
}

.score-breakdown {
  border-top: 1px solid rgba(0, 102, 153, 0.15);
  padding-top: 1rem;
  margin-top: 1rem;
}

.score-breakdown small {
  font-size: 0.875rem;
  line-height: 1.6;
  opacity: 0.85;
}

.form-label {
  font-weight: 600;
  font-size: 1.05rem;
  color: var(--wiki-dark);
  margin-bottom: 0.75rem;
  display: block;
}

[data-theme="dark"] .form-label {
  color: #fff;
}

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

[data-theme="dark"] .form-control,
[data-theme="dark"] textarea.form-control {
  background-color: #2a2a2a;
  color: #fff;
}

.form-control:hover {
  border-color: rgba(0, 102, 153, 0.4);
}

.form-control:focus {
  border-color: var(--wiki-primary);
  box-shadow: 0 0 0 3px rgba(0, 102, 153, 0.12);
  background-color: white;
  outline: none;
}

[data-theme="dark"] .form-control:focus {
  background-color: #2a2a2a;
}

textarea.form-control {
  resize: vertical;
  min-height: 120px;
  line-height: 1.6;
}

.form-text {
  font-size: 0.875rem;
  color: var(--wiki-text-muted);
  margin-top: 0.5rem;
  display: block;
}

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

[data-theme="dark"] .alert-warning {
  background-color: rgba(255, 193, 7, 0.15);
  color: #ffecb3;
}

.alert-warning i {
  font-size: 1.25rem;
}

.badge.bg-primary {
  background-color: var(--wiki-primary) !important;
  font-weight: 600;
  letter-spacing: 0.01em;
}

.modal-footer {
  border-top: 1px solid var(--wiki-border);
  padding: 1.25rem 2rem;
  background-color: var(--wiki-modal-bg);
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
}

[data-theme="dark"] .modal-footer {
  background-color: #1a1a1a;
}

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

.btn i {
  transition: transform 0.2s ease;
}

.btn-success {
  background-color: #28a745;
  color: white;
  box-shadow: 0 2px 8px rgba(40, 167, 69, 0.2);
}

.btn-success:hover:not(:disabled) {
  background-color: #218838;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(40, 167, 69, 0.3);
}

.btn-success:hover:not(:disabled) i {
  transform: scale(1.1);
}

.btn-success:active:not(:disabled) {
  transform: translateY(0);
}

.btn-success:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  background-color: #28a745;
  box-shadow: none;
}

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