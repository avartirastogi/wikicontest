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
            <label class="form-label fw-semibold mb-3">
              <i class="fas fa-sliders-h me-2"></i>Score Parameters
            </label>

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
.review-modal {
  border-radius: 12px;
  overflow: hidden;
}

.modal-header {
  background: linear-gradient(135deg, var(--wiki-primary), var(--wiki-primary-hover));
  color: white;
  border-bottom: none;
  padding: 1.5rem;
}

.modal-title {
  font-weight: 600;
  font-size: 1.25rem;
}

.modal-body {
  padding: 2rem;
  background-color: var(--wiki-modal-bg);
}

.decision-options {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.decision-card {
  position: relative;
  padding: 1.5rem;
  border: 2px solid var(--wiki-border);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  text-align: center;
  background-color: white;
}

[data-theme="dark"] .decision-card {
  background-color: #2a2a2a;
}

.decision-card input[type="radio"] {
  position: absolute;
  opacity: 0;
}

.decision-card span {
  font-weight: 600;
  font-size: 1.1rem;
  display: block;
}

.decision-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.decision-card.accept:hover,
.decision-card.accept.selected {
  border-color: #28a745;
  background-color: rgba(40, 167, 69, 0.1);
}

.decision-card.reject:hover,
.decision-card.reject.selected {
  border-color: #dc3545;
  background-color: rgba(220, 53, 69, 0.1);
}

.decision-card.selected {
  border-width: 3px;
  box-shadow: 0 0 0 3px rgba(0, 102, 153, 0.15);
}

.decision-card.accept.selected span {
  color: #28a745;
}

.decision-card.reject.selected span {
  color: #dc3545;
}

.parameter-scoring-section {
  background: var(--wiki-hover-bg);
  padding: 1.5rem;
  border-radius: 8px;
  margin-bottom: 1rem;
}

.parameter-slider {
  background: linear-gradient(135deg, #ffffff, #f8f9fa);
  padding: 1.25rem;
  border-radius: 8px;
  border: 1px solid var(--wiki-border);
}

[data-theme="dark"] .parameter-slider {
  background: linear-gradient(135deg, #2a2a2a, #1f1f1f);
}

.score-display {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--wiki-primary);
}

.score-value {
  color: var(--wiki-primary);
}

.score-max {
  color: var(--wiki-text-muted);
  font-size: 1rem;
}

.parameter-range {
  width: 100%;
  border-radius: 4px;
  cursor: pointer;
  height: 6px;
  background: linear-gradient(to right, var(--wiki-primary), #e9ecef);
}

.parameter-range::-webkit-slider-thumb {
  width: 24px;
  height: 24px;
  background: var(--wiki-primary);
  border-radius: 50%;
  cursor: pointer;
  transition: transform 0.2s ease;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.3);
}

.parameter-range::-webkit-slider-thumb:hover {
  transform: scale(1.2);
}

.parameter-range::-moz-range-thumb {
  width: 24px;
  height: 24px;
  background: var(--wiki-primary);
  border-radius: 50%;
  cursor: pointer;
  border: none;
  transition: transform 0.2s ease;
}

.parameter-range::-moz-range-thumb:hover {
  transform: scale(1.2);
}

.final-score-preview {
  background: linear-gradient(135deg, rgba(0, 102, 153, 0.1), rgba(0, 102, 153, 0.05));
  border: 2px solid var(--wiki-primary);
}

[data-theme="dark"] .final-score-preview {
  background: linear-gradient(135deg, rgba(93, 184, 230, 0.2), rgba(93, 184, 230, 0.1));
}

.final-score {
  font-size: 2rem;
  font-weight: 700;
  color: var(--wiki-primary);
  letter-spacing: 1px;
}

.score-breakdown {
  border-top: 1px solid var(--wiki-border);
  padding-top: 0.5rem;
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
}

.btn-success {
  background-color: #28a745;
  border-color: #28a745;
}

.btn-success:hover:not(:disabled) {
  background-color: #218838;
  border-color: #1e7e34;
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(40, 167, 69, 0.3);
}

.btn-success:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-secondary {
  background-color: var(--wiki-text-muted);
  border-color: var(--wiki-text-muted);
}

.btn-secondary:hover {
  background-color: #5a6268;
  border-color: #545b62;
}

.alert-warning {
  background-color: rgba(255, 193, 7, 0.1);
  border-color: #ffc107;
  color: #856404;
}

[data-theme="dark"] .alert-warning {
  background-color: rgba(255, 193, 7, 0.2);
  color: #ffecb3;
}

.badge.bg-primary {
  background-color: var(--wiki-primary) !important;
}

.modal-footer {
  border-top: 1px solid var(--wiki-border);
  padding: 1rem 1.5rem;
  background-color: var(--wiki-modal-bg);
}

@media (max-width: 768px) {
  .decision-options {
    grid-template-columns: 1fr;
  }

  .modal-body {
    padding: 1.5rem;
  }
}
</style>