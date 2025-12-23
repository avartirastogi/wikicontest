<template>
  <div class="modal fade"
id="reviewSubmissionModal"
tabindex="-1"
       data-bs-backdrop="static"
data-bs-keyboard="false"
aria-hidden="true">
    <div class="modal-dialog modal-dialog-centered modal-lg review-dialog">
      <div class="modal-content review-modal">

        <!-- Header -->
        <div class="modal-header">
          <h5 class="modal-title">
            <i class="fas fa-gavel me-2"></i>Review Submission
          </h5>
          <button type="button"
class="btn-close"
data-bs-dismiss="modal"
aria-label="Close"></button>
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

          <!-- Score -->
          <div class="mb-4">
            <label class="form-label fw-semibold">
              Points to be Awarded
              <span v-if="status === 'rejected'" class="text-muted">(Disabled for rejected)</span>
            </label>
            <input
              type="number"
              class="form-control"
              v-model.number="score"
              :disabled="status === 'rejected'"
              min="0"
              max="100"
              placeholder="Enter score (0-100)" />
          </div>

          <!-- Comment -->
          <div>
            <label class="form-label fw-semibold">
              Reviewer Comment
              <span class="text-muted">(optional)</span>
            </label>
            <textarea
              class="form-control"
              rows="4"
              v-model="comment"
              placeholder="Provide feedback for the participant..."></textarea>
          </div>
        </div>

        <!-- Footer -->
        <div class="modal-footer">
          <button class="btn btn-secondary" data-bs-dismiss="modal">
            <i class="fas fa-times me-2"></i>Cancel
          </button>

          <button
            class="btn btn-success"
            :disabled="submitting || !status"
            @click="submitReview">
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
import { ref, watch, onMounted } from 'vue'

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
    }
  },
  emits: ['reviewed'],

  setup(props, { emit }) {
    const status = ref('')
    const score = ref(null)
    const comment = ref('')
    const submitting = ref(false)

    const submitReview = async () => {
      submitting.value = true

      try {
        const csrfToken = getCookie('csrf_access_token')

        const payload = {
          status: status.value,
          score: status.value === 'accepted' ? score.value : null,
          comment: comment.value
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

        // Emit the complete review data
        emit('reviewed', {
          submissionId: props.submissionId,
          status: status.value,
          score: status.value === 'accepted' ? score.value : 0,
          comment: comment.value
        })

        console.log('ReviewSubmissionModal emitted:', {
          submissionId: props.submissionId,
          status: status.value,
          score: score.value
        })

        // Close modal
        const modalEl = document.getElementById('reviewSubmissionModal')
        const modalInstance = bootstrap.Modal.getInstance(modalEl)
        if (modalInstance) {
          modalInstance.hide()
        }

        // Reset form
        status.value = ''
        score.value = null
        comment.value = ''
      } catch (err) {
        alert('Failed to submit review: ' + err.message)
      } finally {
        submitting.value = false
      }
    }

    watch(status, (newVal) => {
      if (newVal === 'rejected') {
        score.value = null
      }
    })

    onMounted(() => {
      const modal = document.getElementById('reviewSubmissionModal')

      if (!modal) return

      modal.addEventListener('shown.bs.modal', () => {
        document.body.classList.add('review-blur-active')
      })

      modal.addEventListener('hidden.bs.modal', () => {
        document.body.classList.remove('review-blur-active')
      })
    })

    return {
      status,
      score,
      comment,
      submitting,
      submitReview
    }
  }
}
</script>
<style scoped>
/* ===== Modal Shell ===== */
.review-modal {
  border-radius: 0.75rem;
  border: 1px solid var(--wiki-border);
  background-color: var(--wiki-modal-bg);
  box-shadow: 0 20px 45px rgba(0, 0, 0, 0.25);
  overflow: hidden;
}

/* Header */
.modal-header {
  background-color: var(--wiki-primary);
  color: #fff;
  border-bottom: none;
  padding: 1.25rem 1.5rem;
}

.modal-title {
  font-weight: 600;
}

.modal-header .btn-close {
  filter: invert(1);
}

/* Body */
.modal-body {
  color: var(--wiki-text);
}

/* Decision Cards */
.decision-options {
  display: flex;
  gap: 1rem;
}

.decision-card {
  flex: 1;
  border: 2px solid var(--wiki-border);
  border-radius: 0.5rem;
  padding: 0.75rem;
  cursor: pointer;
  text-align: center;
  transition: all 0.2s ease;
}

.decision-card input {
  display: none;
}

.decision-card.accept {
  color: #198754;
}

.decision-card.reject {
  color: #dc3545;
}

.decision-card:has(input:checked) {
  border-color: currentColor;
  background-color: rgba(0, 0, 0, 0.04);
  transform: translateY(-2px);
  box-shadow: 0 6px 14px rgba(0, 0, 0, 0.15);
}

/* Inputs */
.form-control {
  border-radius: 0.5rem;
}

/* Footer */
.modal-footer {
  border-top: 1px solid var(--wiki-border);
  padding: 1rem 1.5rem;
}

/* Dialog animation (same feel as CreateContest) */
.review-dialog {
  transform: scale(0.96);
  opacity: 0;
  transition: all 0.25s ease;
}

.modal.show .review-dialog {
  transform: scale(1);
  opacity: 1;
}
</style>
