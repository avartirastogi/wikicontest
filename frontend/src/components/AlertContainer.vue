<template>
  <div 
    id="alertContainer" 
    class="position-fixed end-0 p-3" 
    style="z-index: 1050; top: 80px;"
  >
    <transition-group name="alert" tag="div">
      <div
        v-for="alert in alerts"
        :key="alert.id"
        :class="`alert alert-${alert.type} alert-dismissible fade show`"
        role="alert"
      >
        {{ alert.message }}
        <button
          type="button"
          class="btn-close"
          @click="removeAlert(alert.id)"
        ></button>
      </div>
    </transition-group>
  </div>
</template>

<script>
import { getAlertState, removeAlert } from '../utils/alerts'

export default {
  name: 'AlertContainer',
  setup() {
    const alertState = getAlertState()
    
    return {
      alerts: alertState.alerts,
      removeAlert
    }
  }
}
</script>

<style scoped>
.alert-enter-active,
.alert-leave-active {
  transition: all 0.3s ease;
}

.alert-enter-from {
  opacity: 0;
  transform: translateX(100%);
}

.alert-leave-to {
  opacity: 0;
  transform: translateX(100%);
}

/* Alert container styling for better visibility */
/* Positioned below navbar to avoid cluttering with user profile dropdown */
#alertContainer {
  max-width: 400px;
  top: 80px !important; /* Push below navbar (typically 56-60px) */
  right: 1rem;
}

/* Ensure transition group displays alerts vertically with spacing */
#alertContainer > div {
  display: flex;
  flex-direction: column;
}

/* Alert styling with enhanced dark mode visibility */
/* Add margin-bottom to prevent overlapping alerts */
.alert {
  min-width: 280px;
  max-width: 380px;
  margin-bottom: 0.75rem;
  padding: 0.75rem 1rem;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  border-width: 1px;
  border-style: solid;
  font-weight: 500;
  font-size: 0.9rem;
  transition: all 0.3s ease;
}

/* Remove margin from last alert to avoid extra space at bottom */
.alert:last-child {
  margin-bottom: 0;
}

/* Responsive adjustments for mobile */
@media (max-width: 768px) {
  #alertContainer {
    top: 70px !important;
    right: 0.5rem;
    max-width: calc(100vw - 1rem);
  }
  
  .alert {
    min-width: 250px;
    max-width: calc(100vw - 1rem);
    font-size: 0.85rem;
    padding: 0.65rem 0.85rem;
  }
}

[data-theme="dark"] .alert {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.5);
  border-width: 1px;
}

/* Alert info - enhanced visibility */
.alert-info {
  background-color: rgba(0, 102, 153, 0.15) !important;
  border-color: var(--wiki-primary) !important;
  color: var(--wiki-primary) !important;
}

[data-theme="dark"] .alert-info {
  background-color: rgba(93, 184, 230, 0.25) !important;
  border-color: var(--wiki-primary) !important;
  color: var(--wiki-primary) !important;
  border-left-width: 4px;
}

/* Alert success - enhanced visibility */
.alert-success {
  background-color: rgba(51, 153, 102, 0.15) !important;
  border-color: var(--wiki-success) !important;
  color: var(--wiki-success) !important;
}

[data-theme="dark"] .alert-success {
  background-color: rgba(125, 211, 160, 0.25) !important;
  border-color: var(--wiki-success) !important;
  color: var(--wiki-success) !important;
  border-left-width: 4px;
}

/* Alert warning - enhanced visibility */
.alert-warning {
  background-color: rgba(153, 0, 0, 0.15) !important;
  border-color: var(--wiki-danger) !important;
  color: var(--wiki-danger) !important;
}

[data-theme="dark"] .alert-warning {
  background-color: rgba(230, 128, 128, 0.25) !important;
  border-color: var(--wiki-danger) !important;
  color: var(--wiki-danger) !important;
  border-left-width: 4px;
}

/* Alert danger - enhanced visibility */
.alert-danger {
  background-color: rgba(153, 0, 0, 0.15) !important;
  border-color: var(--wiki-danger) !important;
  color: var(--wiki-danger) !important;
}

[data-theme="dark"] .alert-danger {
  background-color: rgba(230, 128, 128, 0.25) !important;
  border-color: var(--wiki-danger) !important;
  color: var(--wiki-danger) !important;
  border-left-width: 4px;
}

/* Close button visibility in dark mode */
.alert .btn-close {
  filter: brightness(0.8);
  opacity: 0.8;
  transition: opacity 0.2s ease, filter 0.2s ease;
}

.alert .btn-close:hover {
  opacity: 1;
  filter: brightness(1);
}

[data-theme="dark"] .alert .btn-close {
  filter: invert(1) brightness(1.5);
  opacity: 0.9;
}

[data-theme="dark"] .alert .btn-close:hover {
  opacity: 1;
  filter: invert(1) brightness(2);
}
</style>
