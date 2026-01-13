<template>
  <div class="container py-5">
    <!-- Navigation and Action Buttons -->
    <div class="mb-4 d-flex justify-content-between align-items-center">
      <button class="btn btn-outline-secondary" @click="goBack">
        <i class="fas fa-arrow-left me-2"></i>Back to Contests
      </button>
      <div class="d-flex gap-2">
        <button v-if="contest"
class="btn btn-primary text-white"
@click="goToLeaderboard"
          title="View Contest Leaderboard">
          <i class="fas fa-trophy me-2"></i>Leaderboard
        </button>
        <!-- Only contest creators and admins can delete -->
        <button v-if="canDeleteContest"
class="btn btn-danger"
@click="handleDeleteContest"
:disabled="deletingContest">
          <span v-if="deletingContest" class="spinner-border spinner-border-sm me-2"></span>
          <i v-else class="fas fa-trash me-2"></i>
          {{ deletingContest ? 'Deleting...' : 'Delete Contest' }}
        </button>

        <button v-if="canDeleteContest" class="btn btn-primary" @click="openEditModal">
          <i class="fas fa-edit me-2"></i>Edit Contest
        </button>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="alert alert-danger">
      <i class="fas fa-exclamation-circle me-2"></i>{{ error }}
      <button class="btn btn-sm btn-outline-danger ms-3" @click="goBack">Go Back</button>
    </div>

    <!-- Contest Details -->
    <div v-else-if="contest" class="contest-view">
      <!-- Header Section -->
      <div class="contest-header-section mb-4">
        <h1 class="contest-title">{{ contest.name }}</h1>
        <div class="contest-meta">
          <span class="badge bg-primary me-2">{{ getStatusLabel(contest.status) }}</span>
          <span class="text-muted">
            <i class="fas fa-calendar-alt me-1"></i>
            Created {{ formatDate(contest.created_at) }}
          </span>
        </div>
      </div>

      <!-- Main Content -->
      <div class="row">
        <div :class="canViewSubmissions ? 'col-md-12' : 'col-md-12'">
          <!-- Basic Contest Information -->
          <div class="card mb-4">
            <div class="card-header">
              <h5 class="mb-0"><i class="fas fa-info-circle me-2"></i>Contest Details</h5>
            </div>
            <div class="card-body">
              <p><strong>Project:</strong> {{ contest.project_name }}</p>
              <p><strong>Status:</strong> <span class="badge bg-primary">{{ contest.status }}</span></p>
              <p v-if="contest.start_date"><strong>Start Date:</strong> {{ formatDate(contest.start_date) }}</p>
              <p v-if="contest.end_date"><strong>End Date:</strong> {{ formatDate(contest.end_date) }}</p>

              <strong>Organizers:</strong>
              <div v-if="contest.organizers && contest.organizers.length > 0" class="organizers-flex">
                <div v-for="organizer in contest.organizers" :key="organizer" class="organizer-chip">
                  <i class="fas fa-user-tie me-2"></i>
                  <strong>{{ organizer }}</strong>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Scoring System Display -->
      <div class="col-md-12">
        <div class="scoring-card">
          <div class="card-header">
            <h5 class="mb-0"><i class="fas fa-chart-line"></i> Scoring System</h5>
          </div>

          <div class="scoring-content">
            <!-- Multi-Parameter Scoring Display -->
            <div v-if="contest.scoring_parameters?.enabled === true">
              <div class="scoring-meta">
                <span class="max-points">Accepted points: {{ contest.scoring_parameters.max_score }}</span>
                <span class="max-points">Rejected points: {{ contest.scoring_parameters.min_score }}</span>
              </div>

              <div class="params-list">
                <div v-for="param in contest.scoring_parameters.parameters" :key="param.name" class="param-item">
                  <div class="param-row">
                    <span class="param-label">{{ param.name }}</span>
                    <span class="param-value">{{ param.weight }}%</span>
                  </div>
                  <p v-if="param.description" class="param-note">{{ param.description }}</p>
                </div>
              </div>

              <div class="info-note">
                <i class="fas fa-info-circle"></i>
                <span>Each parameter scored 0-10, weighted average calculated</span>
              </div>
            </div>

            <!-- Simple Accept/Reject Scoring Display -->
            <div v-else>
              <div class="points-row">
                <div class="point-item">
                  <span class="point-label">Accepted</span>
                  <span class="point-value">{{ contest.marks_setting_accepted }}</span>
                </div>

                <div class="point-item">
                  <span class="point-label">Rejected</span>
                  <span class="point-value">{{ contest.marks_setting_rejected }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Contest Description -->
      <div v-if="contest.description" class="card mb-4 description-section">
        <div class="card-header">
          <h5 class="mb-0"><i class="fas fa-align-left me-2"></i>Description</h5>
        </div>
        <div class="card-body">
          <p class="description-text">{{ contest.description }}</p>
        </div>
      </div>

      <!-- Contest Rules -->
      <div v-if="contest.rules && contest.rules.text" class="card mb-4">
        <div class="card-header">
          <h5 class="mb-0"><i class="fas fa-book me-2"></i>Contest Rules</h5>
        </div>
        <div class="card-body">
          <pre class="rules-text" style="white-space: pre-wrap; font-size: 1rem;">{{ contest.rules.text }}</pre>
        </div>
      </div>

      <!-- Submission Type Information -->
      <div class="card mb-4">
        <div class="card-header">
          <h5 class="mb-0"><i class="fas fa-file-alt me-2"></i>Submission Type Allowed</h5>
        </div>
        <div class="card-body">
          <p>
            <strong>
              {{
                contest.allowed_submission_type === 'new'
                  ? 'New Articles Only'
                  : contest.allowed_submission_type === 'expansion'
                    ? 'Improved Articles Only'
                    : 'Both (New Articles + Improved Articles)'
              }}
            </strong>
          </p>

          <p class="mt-2 small text-muted">
            <em>
              • <strong>New Articles</strong> = Completely new Wikipedia article created during the contest.<br />
              • <strong>Improved Articles</strong> = An existing article improved or expanded with substantial content.
            </em>
          </p>
        </div>
      </div>

      <!-- Required MediaWiki Categories -->
      <div v-if="contest.categories && contest.categories.length > 0" class="card mb-4">
        <div class="card-header">
          <h5 class="mb-0"><i class="fas fa-tags me-2"></i>Required Categories</h5>
        </div>
        <div class="card-body">
          <p class="mb-2">
            <strong>Articles must belong to the following MediaWiki categories:</strong>
          </p>
          <ul class="list-unstyled">
            <li v-for="(category, index) in contest.categories" :key="index" class="mb-2">
              <a :href="category"
target="_blank"
rel="noopener noreferrer"
class="text-decoration-none">
                <i class="fas fa-external-link-alt me-2"></i>{{ getCategoryName(category) }}
              </a>
            </li>
          </ul>
          <small class="text-muted">
            <i class="fas fa-info-circle me-1"></i>
            Submitted articles must be categorized under at least one of these categories.
          </small>
        </div>
      </div>

      <!-- Minimum Reference Requirement -->
      <div v-if="contest.min_reference_count > 0" class="card mb-4">
        <div class="card-header">
          <h5 class="mb-0"><i class="fas fa-link me-2"></i>Minimum Reference Count</h5>
        </div>
        <div class="card-body">
          <p>
            <strong>{{ contest.min_reference_count }} References required</strong>
          </p>
          <small class="text-muted">
            <i class="fas fa-info-circle me-1"></i>
            Submitted articles must have at least {{ contest.min_reference_count }} external references.
          </small>
        </div>
      </div>

      <!-- Jury Members List -->
      <div v-if="contest.jury_members && contest.jury_members.length > 0" class="card mb-4">
        <div class="card-header">
          <h5 class="mb-0"><i class="fas fa-users me-2"></i>Jury Members</h5>
        </div>
        <div class="card-body">
          <div class="organizers-flex">
            <div v-for="jury in contest.jury_members" :key="jury" class="organizer-chip">
              <i class="fas fa-gavel me-2"></i>
              <strong>{{ jury }}</strong>
            </div>
          </div>
        </div>
      </div>

      <!-- Submissions Table (Visible to Jury and Organizers) -->
      <div v-if="canViewSubmissions" class="card mb-4">
        <div class="card-header">
          <div class="d-flex justify-content-between align-items-center">
            <h5 class="mb-0"><i class="fas fa-file-alt me-2"></i>Submissions</h5>
            <button v-if="loadingSubmissions || refreshingMetadata" class="btn btn-sm btn-outline-secondary" disabled>
              <span class="spinner-border spinner-border-sm me-2"></span>
              {{ loadingSubmissions ? 'Loading...' : 'Refreshing...' }}
            </button>
            <!-- Refresh metadata fetches latest article data from MediaWiki -->
            <button v-else
class="btn btn-sm btn-outline-light"
@click="refreshMetadata"
              :disabled="submissions.length === 0"
title="Refresh article metadata"
              style="color: white; border-color: white;">
              <i class="fas fa-database me-1"></i>Refresh Metadata
            </button>
          </div>
        </div>
        <div class="card-body">
          <div v-if="submissions.length === 0 && !loadingSubmissions" class="alert alert-info">
            <i class="fas fa-info-circle me-2"></i>No submissions yet for this contest.
          </div>

          <div v-else-if="submissions.length > 0" class="table-responsive">
            <table class="table table-sm table-hover">
              <thead>
                <tr>
                  <th>Article Title</th>
                  <th>Article Author</th>
                  <th>Submitted By</th>
                  <th>Status</th>
                  <th>Score</th>
                  <th>Submitted At</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="submission in submissions" :key="submission.id">
                  <!-- Article Title with Metadata -->
                  <td>
                    <a href="#"
@click.prevent="showArticlePreview(submission)"
                      class="text-decoration-none article-title-link"
:title="submission.article_link">
                      {{ submission.article_title }}
                      <i class="fas fa-eye ms-1" style="font-size: 0.8em;"></i>
                    </a>
                    <!-- Total byte count -->
                    <div v-if="submission.article_word_count !== null" class="text-muted small mt-1">
                      <i class="fas fa-file-alt me-1"></i>Total bytes:
                      {{ formatByteCountWithExact((submission.article_word_count || 0) +
                        (submission.article_expansion_bytes || 0)) }}
                    </div>
                    <!-- Original article size -->
                    <div v-if="submission.article_word_count !== null &&
                      submission.article_word_count !== undefined"
class="text-muted small mt-1">
                      <i class="fas fa-clock me-1"></i>Original bytes:
                      {{ formatByteCountWithExact(submission.article_word_count) }}
                    </div>
                    <!-- Expansion bytes (can be negative for content removal) -->
                    <div v-if="submission.article_expansion_bytes !== null &&
                      submission.article_expansion_bytes !== undefined"
class="text-muted small mt-1">
                      <i class="me-1"
:class="submission.article_expansion_bytes > 0
                        ? 'fas fa-arrow-up'
                        : submission.article_expansion_bytes < 0
                          ? 'fas fa-arrow-down'
                          : 'fas fa-arrows-left-right'
                        "></i>
                      Expansion bytes:
                      <span v-if="submission.article_expansion_bytes !== 0"
                        :class="submission.article_expansion_bytes >= 0 ? 'text-success' : 'text-danger'">
                        {{ submission.article_expansion_bytes >= 0 ? '+' : '-' }}{{
                          formatByteCountWithExact(Math.abs(submission.article_expansion_bytes))
                        }}
                      </span>
                      <span v-else>
                        {{ formatByteCountWithExact(0) }}
                      </span>
                    </div>
                  </td>
                  <!-- Author Information with Latest Revision -->
                  <td>
                    <div v-if="submission.article_author">
                      <i class="fas fa-user me-1"></i>{{ submission.article_author }}
                    </div>
                    <div v-else class="text-muted small">Unknown</div>
                    <div v-if="submission.article_created_at" class="text-muted small mt-1">
                      <i class="fas fa-calendar me-1"></i>{{ formatDateShort(submission.article_created_at) }}
                    </div>
                    <!-- Latest revision author may differ from original -->
                    <div v-if="submission.latest_revision_author"
class="mt-2 pt-2"
                      style="border-top: 1px solid #dee2e6;">
                      <div>
                        <i class="fas fa-user me-1"></i>{{ submission.latest_revision_author }}
                        <span class="badge bg-info ms-1" style="font-size: 0.7em;">Latest</span>
                      </div>
                      <div v-if="submission.latest_revision_timestamp" class="text-muted small mt-1">
                        <i class="fas fa-calendar me-1"></i>
                        {{ formatDateShort(submission.latest_revision_timestamp) }}
                      </div>
                    </div>
                  </td>
                  <td>{{ submission.username || 'Unknown' }}</td>
                  <td>
                    <span :class="`badge bg-${getStatusColor(submission.status)}`">
                      {{ submission.status }}
                    </span>
                    <div v-if="submission.already_reviewed" class="text-muted small mt-1">
                      <i class="fas fa-check-circle me-1"></i>Reviewed
                    </div>
                  </td>
                  <td>{{ submission.score || 0 }}</td>
                  <td>{{ formatDate(submission.submitted_at) }}</td>
                  <td>
                    <button @click="showArticlePreview(submission)"
class="btn btn-sm btn-outline-primary"
                      title="Preview Article">
                      <i class="fas fa-eye"></i>
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- Bottom Action Row -->
      <div class="d-flex justify-content-between align-items-center gap-2 mb-4">
        <!-- Debug warning for auth issues -->
        <div v-if="contest && !currentUser && !checkingAuth" class="alert alert-warning py-1 px-2 mb-0 me-auto">
          <i class="fas fa-exclamation-triangle me-1"></i>
          <strong>User not loaded!</strong>
          <button class="btn btn-sm btn-outline-warning ms-2" @click="forceAuthRefresh">
            <i class="fas fa-sync-alt me-1"></i>Refresh Auth
          </button>
        </div>

        <!-- Submit article button for active contests -->
        <button v-if="contest?.status === 'current' && isAuthenticated && !canViewSubmissions"
          class="btn btn-primary ms-auto"
@click="handleSubmitArticle">
          <i class="fas fa-paper-plane me-2"></i>Submit Article
        </button>
      </div>
    </div>
  </div>

  <!-- Modals -->
  <SubmitArticleModal v-if="submittingToContestId"
:contest-id="submittingToContestId"
    @submitted="handleArticleSubmitted" />

  <ArticlePreviewModal v-if="!!currentSubmission"
:can-review="canUserReview"
    :article-url="currentSubmission.article_link"
:article-title="currentSubmission.article_title"
    :submission-id="currentSubmission.id"
:submission="currentSubmission"
    :contest-scoring-config="contest?.scoring_parameters"
@reviewed="handleSubmissionReviewed" />

  <!-- Edit Contest Modal -->
  <div class="modal fade" id="editContestModal" tabindex="-1">
    <div class="modal-dialog modal-fullscreen">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">
            <i class="fas fa-edit me-2"></i>Edit Contest
          </h5>
          <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
        </div>

        <div class="modal-body">
          <form @submit.prevent="saveContestEdits">
            <!-- Basic Contest Information -->
            <div class="mb-3">
              <label class="form-label">Contest Name</label>
              <input v-model="editForm.name" class="form-control" required />
            </div>

            <div class="mb-3">
              <label class="form-label">Project Name</label>
              <input v-model="editForm.project_name" class="form-control" required />
            </div>

            <div class="mb-3">
              <label class="form-label">Description</label>
              <textarea v-model="editForm.description" rows="4" class="form-control"></textarea>
            </div>

            <div class="mb-3">
              <label class="form-label">Rules</label>
              <textarea v-model="editForm.rules" rows="6" class="form-control"></textarea>
            </div>

            <div class="mb-3">
              <label class="form-label">Allowed Submission Type</label>
              <select class="form-control" v-model="editForm.allowed_submission_type">
                <option value="new">New Articles Only</option>
                <option value="expansion">Improved Article Only</option>
                <option value="both">Both (New Article + Improved Article)</option>
              </select>
            </div>

            <!-- Contest Date Range -->
            <div class="row">
              <div class="col-md-6 mb-3">
                <label class="form-label">Start Date</label>
                <input type="date" v-model="editForm.start_date" class="form-control" />
              </div>

              <div class="col-md-6 mb-3">
                <label class="form-label">End Date</label>
                <input type="date" v-model="editForm.end_date" class="form-control" />
              </div>
            </div>

            <!-- Organizer Management with Search -->
            <div class="mb-3">
              <label class="form-label">
                Contest Organizers
                <span class="badge bg-info">Type to search and add users</span>
              </label>

              <!-- Selected Organizers Display -->
              <div class="mb-2 p-2 border rounded bg-light organizer-selection-box" style="min-height: 60px;">
                <small v-if="editForm.selectedOrganizers.length === 0" class="text-muted">
                  No organizers selected
                </small>
                <span v-for="username in editForm.selectedOrganizers"
:key="username"
class="badge bg-success me-2 mb-2"
                  style="font-size: 0.9rem; cursor: pointer;">
                  <i class="fas fa-user-tie me-1"></i>{{ username }}
                  <i class="fas fa-times ms-1" @click="removeOrganizer(username)"></i>
                </span>
              </div>

              <!-- Organizer Search Input with Autocomplete -->
              <div style="position: relative;">
                <input type="text"
class="form-control"
v-model="organizerSearchQuery"
@input="searchOrganizers"
                  placeholder="Type username to search and add..."
autocomplete="off" />

                <!-- Autocomplete Dropdown -->
                <div v-if="organizerSearchResults.length > 0 && organizerSearchQuery.length >= 2"
                  class="organizer-autocomplete position-absolute w-100 border rounded-bottom"
                  style="max-height: 200px; overflow-y: auto; z-index: 1000; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                  <div v-for="user in organizerSearchResults"
:key="user.username"
                    class="p-2 border-bottom cursor-pointer"
                    :class="{ 'bg-warning-subtle': isCurrentUser(user.username) }"
style="cursor: pointer;"
                    @click="addOrganizer(user.username)">
                    <div class="d-flex align-items-center justify-content-between">
                      <div class="d-flex align-items-center">
                        <i class="fas fa-user me-2 text-success"></i>
                        <strong>{{ user.username }}</strong>
                      </div>
                      <!-- Warn when adding self as organizer -->
                      <div v-if="isCurrentUser(user.username)" class="self-warning-badge">
                        <i class="fas fa-exclamation-triangle me-1"></i>
                        <small>This is you</small>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <small class="form-text text-muted mt-1">
                Search and click to add organizers. Click × to remove. Organizers can manage this contest.
              </small>
            </div>

            <!-- Jury Member Management with Search -->
            <div class="mb-3">
              <label class="form-label">
                Jury Members
                <span class="badge bg-info">Type to search and add users</span>
              </label>

              <!-- Selected Jury Members Display -->
              <div class="mb-2 p-2 border rounded bg-light jury-selection-box" style="min-height: 60px;">
                <small v-if="editForm.selectedJuryMembers.length === 0" class="text-muted">
                  No jury members selected
                </small>
                <span v-for="username in editForm.selectedJuryMembers"
:key="username"
                  class="badge bg-primary me-2 mb-2"
style="font-size: 0.9rem; cursor: pointer;">
                  <i class="fas fa-gavel me-1"></i>{{ username }}
                  <i class="fas fa-times ms-1" @click="removeJuryMember(username)"></i>
                </span>
              </div>

              <!-- Jury Search Input with Autocomplete -->
              <div style="position: relative;">
                <input type="text"
class="form-control"
v-model="jurySearchQuery"
@input="searchJuryMembers"
                  placeholder="Type username to search and add..."
autocomplete="off" />

                <!-- Autocomplete Dropdown -->
                <div v-if="jurySearchResults.length > 0 && jurySearchQuery.length >= 2"
                  class="jury-autocomplete position-absolute w-100 border rounded-bottom"
                  style="max-height: 200px; overflow-y: auto; z-index: 1000; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                  <div v-for="user in jurySearchResults"
:key="user.username"
class="p-2 border-bottom cursor-pointer"
                    :class="{ 'bg-warning-subtle': isCurrentUser(user.username) }"
style="cursor: pointer;"
                    @click="addJuryMember(user.username)">
                    <div class="d-flex align-items-center justify-content-between">
                      <div class="d-flex align-items-center">
                        <i class="fas fa-user me-2 text-primary"></i>
                        <strong>{{ user.username }}</strong>
                      </div>
                      <!-- Warn when adding self as jury -->
                      <div v-if="isCurrentUser(user.username)" class="self-warning-badge">
                        <i class="fas fa-exclamation-triangle me-1"></i>
                        <small>This is you</small>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <small class="form-text text-muted mt-1">
                Search and click to add jury members. Click × to remove.
              </small>
            </div>

            <!-- Simple Scoring Configuration -->
            <div v-if="editForm.scoring_mode === 'simple'">
              <div class="mb-3">
                <label class="form-label">Accepted Points</label>
                <input type="number" v-model.number="editForm.marks_setting_accepted" class="form-control" />
              </div>

              <div class="mb-3">
                <label class="form-label">Rejected Points</label>
                <input type="number" v-model.number="editForm.marks_setting_rejected" class="form-control" />
              </div>
            </div>

            <!-- Multi-Parameter Scoring Configuration -->
            <div v-if="editForm.scoring_mode === 'multi'">
              <div class="mb-3">
                <label class="form-label">Maximum Score</label>
                <input type="number" v-model.number="editForm.scoring_parameters.max_score" class="form-control" />
              </div>

              <div class="mb-3">
                <label class="form-label">Minimum Score</label>
                <input type="number" v-model.number="editForm.scoring_parameters.min_score" class="form-control" />
              </div>

              <hr />

              <h6>Scoring Parameters</h6>

              <!-- Dynamic parameter list -->
              <div v-for="(param, index) in editForm.scoring_parameters.parameters"
:key="index"
                class="border rounded p-3 mb-2">
                <div class="row">
                  <div class="col-md-4">
                    <input v-model="param.name" placeholder="Parameter name" class="form-control" />
                  </div>

                  <div class="col-md-3">
                    <input type="number"
v-model.number="param.weight"
placeholder="Weight %"
class="form-control" />
                  </div>

                  <div class="col-md-4">
                    <input v-model="param.description" placeholder="Description (optional)" class="form-control" />
                  </div>

                  <div class="col-md-1 text-end">
                    <button class="btn btn-outline-danger btn-sm"
                      @click="editForm.scoring_parameters.parameters.splice(index, 1)">
                      <i class="fas fa-trash"></i>
                    </button>
                  </div>
                </div>
              </div>

              <button class="btn btn-outline-primary btn-sm"
                @click="editForm.scoring_parameters.parameters.push({ name: '', weight: 0, description: '' })">
                <i class="fas fa-plus me-1"></i>Add Parameter
              </button>
            </div>

            <!-- Article Requirements -->
            <div class="mb-3">
              <label class="form-label">Minimum Byte Count *</label>
              <input type="number"
v-model.number="editForm.min_byte_count"
class="form-control"
min="0"
                placeholder="e.g., 1000"
required />
              <small class="form-text text-muted">Articles must have at least this many bytes</small>
            </div>

            <div class="mb-3">
              <label class="form-label">Minimum Reference Count</label>
              <input type="number"
v-model.number="editForm.min_reference_count"
class="form-control"
min="0"
                placeholder="e.g., 5" />
              <small class="form-text text-muted">
                Articles must have at least this many references. Set to 0 for no requirement.
              </small>
            </div>


            <!-- Continuing from edit form - Category URLs section -->
            <div class="mb-3">
              <label class="form-label">
                Category URLs *
                <span class="text-muted">(MediaWiki category pages)</span>
              </label>

              <!-- Dynamic category URL inputs -->
              <div v-for="(category, index) in editForm.categories" :key="index" class="mb-2">
                <div class="input-group">
                  <input type="url"
class="form-control"
v-model="editForm.categories[index]"
                    :placeholder="index === 0 ? 'https://en.wikipedia.org/wiki/Category:Example' : 'Add another category URL'"
                    required />
                  <!-- Allow removing categories except the first one -->
                  <button v-if="editForm.categories.length > 1"
type="button"
class="btn btn-outline-danger"
                    @click="removeCategory(index)"
title="Remove category">
                    <i class="fas fa-times"></i>
                  </button>
                </div>
              </div>

              <button type="button" class="btn btn-outline-primary btn-sm" @click="addCategory">
                <i class="fas fa-plus me-1"></i>Add Category
              </button>

              <small class="form-text text-muted d-block mt-2">
                At least one MediaWiki category URL is required. Articles must belong to these categories.
              </small>
            </div>
          </form>
        </div>

        <div class="modal-footer">
          <button class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
          <button class="btn btn-primary" @click="saveContestEdits">
            <i class="fas fa-save me-2"></i>Save Changes
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { computed, ref, watch, onMounted, reactive } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useStore } from '../store'
import api from '../services/api'
import { showAlert } from '../utils/alerts'
import SubmitArticleModal from '../components/SubmitArticleModal.vue'
import ArticlePreviewModal from '../components/ArticlePreviewModal.vue'

export default {
  name: 'ContestView',
  components: {
    SubmitArticleModal,
    ArticlePreviewModal
  },

  setup() {
    const router = useRouter()
    const route = useRoute()
    const store = useStore()

    // Component state
    const contest = ref(null)
    const loading = ref(true)
    const error = ref(null)
    const submissions = ref([])
    const loadingSubmissions = ref(false)
    const refreshingMetadata = ref(false)
    const deletingContest = ref(false)
    const canDeleteContest = ref(false)
    const checkingAuth = ref(false)
    const submittingToContestId = ref(null)
    const previewArticleUrl = ref('')
    const previewArticleTitle = ref('')
    const jurySearchQuery = ref('')
    const jurySearchResults = ref([])
    const organizerSearchQuery = ref('')
    const organizerSearchResults = ref([])

    // Debounce timers for search functionality
    let jurySearchTimeout = null
    let organizerSearchTimeout = null
    const scoringMode = ref('simple')

    // Track current submission for preview modal
    const currentSubmissionId = ref(null)

    // Get submission reactively to ensure updates propagate
    const currentSubmission = computed(() => {
      if (!currentSubmissionId.value) return null
      return submissions.value.find(s => s.id === currentSubmissionId.value)
    })

    // Get current user from multiple possible store locations
    const currentUser = computed(() => {
      if (store.state && store.state.currentUser) {
        return store.state.currentUser
      }
      if (store.currentUser) {
        return store.currentUser
      }
      return null
    })

    // Check if user is authenticated with valid data
    const isAuthenticated = computed(() => {
      const user = currentUser.value
      return !!user && !!user.id && !!user.username
    })

    // Determine if user can view submissions (organizers and jury only)
    const canViewSubmissions = computed(() => {
      if (!isAuthenticated.value || !contest.value || !currentUser.value) {
        return false
      }

      const username = (currentUser.value.username || '').trim().toLowerCase()
      const contestData = contest.value

      // Contest creator can view submissions
      const contestCreator = (contestData.created_by || '').trim().toLowerCase()
      if (contestCreator && username === contestCreator) {
        return true
      }

      // Jury members can view submissions
      if (contestData.jury_members && Array.isArray(contestData.jury_members)) {
        const juryUsernames = contestData.jury_members.map(j => (j || '').trim().toLowerCase())
        return juryUsernames.includes(username)
      }

      return false
    })

    // Determine if user can delete contest (creator or admin/superadmin)
    const checkDeletePermission = () => {
      canDeleteContest.value = false

      const userFromComputed = currentUser.value
      const userFromStore = store.currentUser
      const userFromState = (store.state && store.state.currentUser) || null
      const userToCheck = userFromComputed || userFromStore || userFromState

      if (!isAuthenticated.value || !contest.value || !userToCheck) {
        canDeleteContest.value = false
        return
      }

      const username = (userToCheck.username || '').trim()
      const role = (userToCheck.role || '').trim().toLowerCase()
      const contestCreator = (contest.value.created_by || '').trim()

      if (!username || !contestCreator) {
        canDeleteContest.value = false
        return
      }

      const usernameLower = username.toLowerCase()
      const creatorLower = contestCreator.toLowerCase()

      // Allow delete if user is creator or admin-level
      if (usernameLower === creatorLower) {
        canDeleteContest.value = true
        return
      }

      if (role === 'admin' || role === 'superadmin') {
        canDeleteContest.value = true
        return
      }

      canDeleteContest.value = false
    }

    // Format date to IST timezone with full details
    const formatDate = (dateString) => {
      if (!dateString) return 'No date'
      try {
        // Ensure UTC format for consistent parsing
        let utcDateString = dateString
        if (!dateString.endsWith('Z') && !dateString.includes('+') && !dateString.includes('-', 10)) {
          utcDateString = dateString + 'Z'
        }

        return new Date(utcDateString).toLocaleString('en-IN', {
          timeZone: 'Asia/Kolkata',
          year: 'numeric',
          month: 'long',
          day: 'numeric',
          hour: '2-digit',
          minute: '2-digit',
          hour12: true
        })
      } catch (e) {
        return dateString
      }
    }

    // Format date in shorter format for table display
    const formatDateShort = (dateString) => {
      if (!dateString) return ''
      try {
        let utcDateString = dateString
        if (!dateString.endsWith('Z') && !dateString.includes('+') && !dateString.includes('-', 10)) {
          utcDateString = dateString + 'Z'
        }

        return new Date(utcDateString).toLocaleString('en-IN', {
          timeZone: 'Asia/Kolkata',
          year: 'numeric',
          month: 'long',
          day: 'numeric',
          hour: '2-digit',
          minute: '2-digit',
          hour12: true
        })
      } catch (e) {
        return dateString
      }
    }

    // Convert bytes to human-readable format (KB/MB)
    const formatByteCount = (bytes) => {
      if (!bytes) return ''
      if (bytes >= 1048576) {
        return `${(bytes / 1048576).toFixed(1)} MB`
      }
      if (bytes >= 1024) {
        return `${(bytes / 1024).toFixed(1)} KB`
      }
      return `${bytes} bytes`
    }

    // Format bytes with exact count in parentheses
    const formatByteCountWithExact = (bytes) => {
      if (!bytes && bytes !== 0) return ''

      const absBytes = Math.abs(bytes)

      let formatted = ''
      if (absBytes >= 1048576) {
        formatted = `${(absBytes / 1048576).toFixed(1)} MB (${bytes} bytes)`
      } else if (absBytes >= 1024) {
        formatted = `${(absBytes / 1024).toFixed(1)} KB (${bytes} bytes)`
      } else {
        formatted = `${bytes} bytes`
      }

      return formatted
    }

    // Extract category name from full MediaWiki URL
    const getCategoryName = (categoryUrl) => {
      if (!categoryUrl) return ''

      try {
        const url = new URL(categoryUrl)
        let pageTitle = ''

        // Parse standard MediaWiki URL format
        if (url.pathname.includes('/wiki/')) {
          pageTitle = decodeURIComponent(url.pathname.split('/wiki/')[1])
        } else if (url.searchParams.has('title')) {
          pageTitle = decodeURIComponent(url.searchParams.get('title'))
        } else {
          // Fallback to last path segment
          const parts = url.pathname.split('/').filter(p => p)
          if (parts.length > 0) {
            pageTitle = decodeURIComponent(parts[parts.length - 1])
          }
        }

        return pageTitle || categoryUrl
      } catch (e) {
        return categoryUrl
      }
    }

    // Simple byte count formatter
    const formatWordCount = (bytes) => {
      if (bytes === null || bytes === undefined) return '0 bytes'
      const absBytes = Math.abs(bytes)
      if (absBytes >= 1048576) {
        return `${(absBytes / 1048576).toFixed(1)} MB`
      }
      if (absBytes >= 1024) {
        return `${(absBytes / 1024).toFixed(1)} KB`
      }
      return `${absBytes} bytes`
    }

    // Convert status key to display label
    const getStatusLabel = (status) => {
      const labels = {
        current: 'Active',
        upcoming: 'Upcoming',
        past: 'Past',
        unknown: 'Unknown'
      }
      return labels[status] || 'Unknown'
    }

    // Get Bootstrap color class for submission status
    const getStatusColor = (status) => {
      switch (status?.toLowerCase()) {
        case 'accepted':
          return 'success'
        case 'rejected':
          return 'danger'
        case 'pending':
          return 'warning'
        default:
          return 'secondary'
      }
    }

    // Load contest by ID or name from route
    const loadContest = async (id = null) => {
      loading.value = true
      error.value = null

      try {
        let data
        if (id) {
          data = await api.get(`/contest/${id}`)
        } else {
          const contestName = route.params.name
          if (!contestName) throw new Error('Contest name is required')
          data = await api.get(`/contest/name/${contestName}`)
        }

        // Ensure scoring parameters are initialized
        contest.value = {
          ...data,
          scoring_parameters: data.scoring_parameters
            ? { ...data.scoring_parameters }
            : { enabled: false }
        }

        // Check permissions after loading contest
        await checkAuthAndPermissions()

        // Load submissions if user has access
        if (canViewSubmissions.value) loadSubmissions()
      } catch (err) {
        console.error('Error loading contest:', err)
        error.value = 'Failed to load contest: ' + (err.message || 'Unknown error')
      } finally {
        loading.value = false
      }
    }

    // Verify user authentication and check permissions
    const checkAuthAndPermissions = async () => {
      checkingAuth.value = true
      canDeleteContest.value = false

      try {
        // Try to get user from store
        let loadedUser = store.currentUser || (store.state && store.state.currentUser) || currentUser.value

        // If not in store, fetch from backend
        if (!loadedUser) {
          await store.checkAuth()
          await new Promise(resolve => setTimeout(resolve, 150))
          loadedUser = store.currentUser || (store.state && store.state.currentUser) || currentUser.value
        }

        // Allow time for reactive updates
        await new Promise(resolve => setTimeout(resolve, 100))

        checkDeletePermission()
      } catch (error) {
        console.error('Failed to check auth:', error)
        canDeleteContest.value = false
      } finally {
        checkingAuth.value = false
      }
    }

    // Fetch all submissions for this contest
    const loadSubmissions = async () => {
      if (!contest.value || !canViewSubmissions.value) {
        return
      }

      loadingSubmissions.value = true
      try {
        const data = await api.get(`/contest/${contest.value.id}/submissions`)
        submissions.value = data || []
      } catch (error) {
        console.error('Failed to load submissions:', error)
        showAlert('Failed to load submissions: ' + error.message, 'danger')
        submissions.value = []
      } finally {
        loadingSubmissions.value = false
      }
    }

    // Refresh article metadata from MediaWiki for all submissions
    const refreshMetadata = async () => {
      if (!contest.value || !canViewSubmissions.value || submissions.value.length === 0) {
        return
      }

      refreshingMetadata.value = true
      try {
        const response = await api.post(`/submission/contest/${contest.value.id}/refresh-metadata`)
        showAlert(
          `Metadata refreshed: ${response.updated} updated, ${response.failed} failed`,
          response.failed === 0 ? 'success' : 'warning'
        )
        await loadSubmissions()
      } catch (error) {
        console.error('Failed to refresh metadata:', error)
        showAlert('Failed to refresh metadata: ' + error.message, 'danger')
      } finally {
        refreshingMetadata.value = false
      }
    }

    // Delete contest with confirmation
    const handleDeleteContest = async () => {
      if (!contest.value) return

      const confirmed = confirm(
        `Are you sure you want to delete the contest "${contest.value.name}"?\n\n` +
        'This action cannot be undone and will delete all associated submissions.'
      )

      if (!confirmed) return

      deletingContest.value = true
      try {
        await api.delete(`/contest/${contest.value.id}`)
        showAlert('Contest deleted successfully', 'success')
        router.push({ name: 'Contests' })
      } catch (error) {
        console.error('Failed to delete contest:', error)
        showAlert('Failed to delete contest: ' + error.message, 'danger')
      } finally {
        deletingContest.value = false
      }
    }

    // Open article submission modal
    const handleSubmitArticle = () => {
      if (!store.isAuthenticated) {
        showAlert('Please login to submit an article', 'warning')
        return
      }
      submittingToContestId.value = contest.value.id
      setTimeout(() => {
        const modalElement = document.getElementById('submitArticleModal')
        if (modalElement) {
          const modal = new bootstrap.Modal(modalElement)
          modal.show()
        }
      }, 100)
    }

    // Refresh after article submission
    const handleArticleSubmitted = () => {
      submittingToContestId.value = null
      loadContest()
    }

    // Manually refresh authentication status
    const forceAuthRefresh = async () => {
      checkingAuth.value = true
      try {
        await store.checkAuth()
        await new Promise(resolve => setTimeout(resolve, 200))
        checkDeletePermission()
      } catch (error) {
        console.error('Auth refresh failed:', error)
      } finally {
        checkingAuth.value = false
      }
    }

    // Navigate back to contests list
    const goBack = () => {
      router.push({ name: 'Contests' })
    }

    // Show article preview modal for submission
    const showArticlePreview = (submission) => {
      currentSubmissionId.value = submission.id

      setTimeout(() => {
        const modalElement = document.getElementById('articlePreviewModal')
        if (modalElement) {
          const modal = new bootstrap.Modal(modalElement)
          modal.show()
        }
      }, 100)
    }

    // Update submission in array after review
    const handleSubmissionReviewed = (reviewData) => {
      console.log('Review received:', reviewData)

      const submissionIndex = submissions.value.findIndex(
        s => s.id === reviewData.submissionId
      )

      if (submissionIndex !== -1) {
        submissions.value[submissionIndex] = {
          ...submissions.value[submissionIndex],
          status: reviewData.status,
          score: reviewData.score,
          review_comment: reviewData.comment,
          already_reviewed: true,
          reviewed_at: new Date().toISOString()
        }

        // Trigger reactivity
        submissions.value = [...submissions.value]

        showAlert('Submission reviewed successfully', 'success')
      }
    }

    // Watch for user changes and update permissions
    watch(() => currentUser.value, (newUser) => {
      if (newUser && contest.value && !checkingAuth.value) {
        setTimeout(() => {
          checkDeletePermission()
        }, 50)
      } else if (!newUser && contest.value) {
        canDeleteContest.value = false
      }
    }, { deep: true })

    // Edit form state
    const editForm = reactive({
      name: '',
      project_name: '',
      description: '',
      rules: '',
      start_date: '',
      end_date: '',
      marks_setting_accepted: 0,
      marks_setting_rejected: 0,
      jury_members: '',
      allowed_submission_type: '',
      selectedJuryMembers: [],
      selectedOrganizers: [],
      min_byte_count: 0,
      categories: [''],
      min_reference_count: 0,
      scoring_mode: '',
      scoring_parameters: {
        max_score: 10,
        min_score: 0,
        parameters: []
      }
    })

    let editModal = null

    // Initialize modal on mount
    onMounted(() => {
      loadContest()
      const modalEl = document.getElementById('editContestModal')
      if (modalEl) editModal = new bootstrap.Modal(modalEl)
    })

    // Check if username matches current user
    const isCurrentUser = (username) => {
      const currentUsername = currentUser.value?.username
      if (!currentUsername || !username) return false
      return String(currentUsername).trim().toLowerCase() ===
        String(username).trim().toLowerCase()
    }

    // Search jury members with debounce
    const searchJuryMembers = async () => {
      const query = jurySearchQuery.value.trim()

      if (query.length < 2) {
        jurySearchResults.value = []
        return
      }

      if (jurySearchTimeout) {
        clearTimeout(jurySearchTimeout)
      }

      // Debounce to avoid excessive API calls
      jurySearchTimeout = setTimeout(async () => {
        try {
          const response = await api.get(`/user/search?q=${encodeURIComponent(query)}&limit=10`)
          // Filter out already selected users
          jurySearchResults.value = (response.users || []).filter(
            user => !editForm.selectedJuryMembers.includes(user.username)
          )
        } catch (error) {
          console.error('Jury search error:', error)
          jurySearchResults.value = []
        }
      }, 300)
    }

    // Add jury member with self-selection warning
    const addJuryMember = (username) => {
      if (isCurrentUser(username)) {
        const confirmed = window.confirm(
          '⚠️ WARNING: Self-Selection as Jury Member\n\n' +
          'You are about to add yourself as a jury member.\n\n' +
          'It is recommended to select other users as jury members.\n\n' +
          'Continue?'
        )
        if (!confirmed) return
      }

      if (!editForm.selectedJuryMembers.includes(username)) {
        editForm.selectedJuryMembers.push(username)
        jurySearchQuery.value = ''
        jurySearchResults.value = []
      }
    }

    // Remove jury member from selection
    const removeJuryMember = (username) => {
      editForm.selectedJuryMembers = editForm.selectedJuryMembers.filter(
        u => u !== username
      )
    }

    // Search organizers with debounce
    const searchOrganizers = async () => {
      const query = organizerSearchQuery.value.trim()

      if (query.length < 2) {
        organizerSearchResults.value = []
        return
      }

      if (organizerSearchTimeout) {
        clearTimeout(organizerSearchTimeout)
      }

      organizerSearchTimeout = setTimeout(async () => {
        try {
          const response = await api.get(`/user/search?q=${encodeURIComponent(query)}&limit=10`)
          organizerSearchResults.value = (response.users || []).filter(
            user => !editForm.selectedOrganizers.includes(user.username)
          )
        } catch (error) {
          console.error('Organizer search error:', error)
          organizerSearchResults.value = []
        }
      }, 300)
    }

    // Add organizer with confirmation
    const addOrganizer = (username) => {
      if (isCurrentUser(username)) {
        const confirmed = window.confirm(
          '⚠️ WARNING: Self-Selection as Organizer\n\n' +
          'You are about to add yourself as an organizer.\n\n' +
          'Continue?'
        )
        if (!confirmed) return
      }

      if (!editForm.selectedOrganizers.includes(username)) {
        editForm.selectedOrganizers.push(username)
        organizerSearchQuery.value = ''
        organizerSearchResults.value = []
      }
    }

    // Remove organizer from selection
    const removeOrganizer = (username) => {
      editForm.selectedOrganizers = editForm.selectedOrganizers.filter(
        u => u !== username
      )
    }

    // Add new category field
    const addCategory = () => {
      editForm.categories.push('')
    }

    // Remove category field if more than one exists
    const removeCategory = (index) => {
      if (editForm.categories.length > 1) {
        editForm.categories.splice(index, 1)
      }
    }

    // Populate edit form with contest data
    const openEditModal = () => {
      if (!contest.value) return

      editForm.name = contest.value.name
      editForm.project_name = contest.value.project_name || ''
      editForm.description = contest.value.description || ''
      editForm.rules = contest.value.rules?.text || ''
      editForm.allowed_submission_type = contest.value.allowed_submission_type || 'both'
      editForm.start_date = contest.value.start_date || ''
      editForm.end_date = contest.value.end_date || ''
      editForm.min_byte_count = Number(contest.value.min_byte_count ?? 0)
      editForm.min_reference_count = Number(contest.value.min_reference_count ?? 0)

      // Populate jury members
      if (Array.isArray(contest.value.jury_members)) {
        editForm.selectedJuryMembers = [...contest.value.jury_members]
      } else {
        editForm.selectedJuryMembers = []
      }

      // Populate organizers
      if (Array.isArray(contest.value.organizers)) {
        editForm.selectedOrganizers = [...contest.value.organizers]
      } else {
        editForm.selectedOrganizers = []
      }

      // Populate categories
      if (Array.isArray(contest.value.categories) && contest.value.categories.length > 0) {
        editForm.categories = [...contest.value.categories]
      } else {
        editForm.categories = ['']
      }

      // Populate scoring configuration
      if (contest.value.scoring_parameters?.enabled) {
        editForm.scoring_mode = 'multi'

        editForm.scoring_parameters = {
          max_score: contest.value.scoring_parameters.max_score ?? 10,
          min_score: contest.value.scoring_parameters.min_score ?? 0,
          parameters: contest.value.scoring_parameters.parameters
            ? [...contest.value.scoring_parameters.parameters]
            : []
        }
      } else {
        editForm.scoring_mode = 'simple'
        editForm.marks_setting_accepted = Number(contest.value.marks_setting_accepted ?? 0)
        editForm.marks_setting_rejected = Number(contest.value.marks_setting_rejected ?? 0)

        editForm.scoring_parameters = {
          max_score: 10,
          min_score: 0,
          parameters: []
        }
      }

      // Reset search states
      jurySearchQuery.value = ''
      jurySearchResults.value = []
      organizerSearchQuery.value = ''
      organizerSearchResults.value = []

      if (editModal) editModal.show()
    }

    // Save contest edits with validation
    const saveContestEdits = async () => {
      try {
        // Validate multi-parameter scoring weights sum to 100%
        if (editForm.scoring_mode === 'multi') {
          const totalWeight = editForm.scoring_parameters.parameters
            .reduce((sum, p) => sum + Number(p.weight || 0), 0)

          if (totalWeight !== 100) {
            showAlert('Total parameter weight must be 100%', 'warning')
            return
          }
        }

        // Ensure at least one category is provided
        const validCategories = editForm.categories.filter(cat => cat && cat.trim())
        if (validCategories.length === 0) {
          showAlert('At least one category URL is required', 'warning')
          return
        }

        // Build update payload
        const payload = {
          name: editForm.name,
          project_name: editForm.project_name,
          description: editForm.description,
          rules: editForm.rules?.trim() || '',
          start_date: editForm.start_date || null,
          end_date: editForm.end_date || null,
          jury_members: editForm.selectedJuryMembers,
          organizers: editForm.selectedOrganizers,
          allowed_submission_type: editForm.allowed_submission_type,
          min_byte_count: Number(editForm.min_byte_count),
          categories: validCategories,
          min_reference_count: Number(editForm.min_reference_count)
        }

        // Add scoring configuration based on mode
        if (editForm.scoring_mode === 'multi') {
          payload.scoring_parameters = {
            enabled: true,
            max_score: Number(editForm.scoring_parameters.max_score),
            min_score: Number(editForm.scoring_parameters.min_score),
            parameters: editForm.scoring_parameters.parameters
          }
        } else {
          payload.marks_setting_accepted = Number(editForm.marks_setting_accepted)
          payload.marks_setting_rejected = Number(editForm.marks_setting_rejected)
          payload.scoring_parameters = { enabled: false }
        }

        await api.put(`/contest/${contest.value.id}`, payload)

        showAlert('Contest updated successfully', 'success')
        editModal.hide()

        // Reload contest to show changes
        await loadContest(contest.value.id)
      } catch (error) {
        showAlert(
          'Failed to save: ' + (error.response?.data?.detail || error.message),
          'danger'
        )
      }
    }

    // Check if user can review submissions (jury members only)
    const canUserReview = computed(() => {
      if (!isAuthenticated.value || !contest.value || !currentUser.value) {
        return false
      }

      const username = currentUser.value.username.trim().toLowerCase()

      if (Array.isArray(contest.value.jury_members)) {
        const jury = contest.value.jury_members
          .filter(Boolean)
          .map(j => String(j).trim().toLowerCase())

        if (jury.includes(username)) {
          return true
        }
      }

      return false
    })

    // Navigate to contest leaderboard
    const goToLeaderboard = () => {
      if (!contest.value) return

      router.push({
        name: 'ContestLeaderboard',
        params: { name: route.params.name }
      })
    }

    return {
      contest,
      loading,
      error,
      submissions,
      loadingSubmissions,
      deletingContest,
      canDeleteContest,
      checkingAuth,
      submittingToContestId,
      currentUser,
      isAuthenticated,
      canViewSubmissions,
      currentSubmission,
      formatDate,
      formatDateShort,
      formatByteCount,
      formatByteCountWithExact,
      getStatusLabel,
      formatWordCount,
      getStatusColor,
      getCategoryName,
      loadSubmissions,
      refreshMetadata,
      refreshingMetadata,
      handleDeleteContest,
      handleSubmitArticle,
      handleArticleSubmitted,
      forceAuthRefresh,
      jurySearchQuery,
      jurySearchResults,
      organizerSearchQuery,
      organizerSearchResults,
      searchJuryMembers,
      addJuryMember,
      removeJuryMember,
      searchOrganizers,
      addOrganizer,
      removeOrganizer,
      addCategory,
      removeCategory,
      isCurrentUser,
      goBack,
      showArticlePreview,
      handleSubmissionReviewed,
      previewArticleUrl,
      previewArticleTitle,
      editForm,
      openEditModal,
      saveContestEdits,
      canUserReview,
      goToLeaderboard,
      scoringMode
    }
  }
}
</script>

<style scoped>
/* Contest View Styling with Wikipedia Colors */
/* Main Container */
.contest-view {
  max-width: 1200px;
  margin: 0 auto;
}

/* Header Section */
.contest-header-section {
  border-bottom: 2px solid var(--wiki-primary);
  padding-bottom: 1rem;
}

/* Main contest title styling with theme support */
.contest-title {
  color: var(--wiki-dark);
  font-weight: 700;
  font-size: 2.5rem;
  margin-bottom: 0.5rem;
  transition: color 0.3s ease;
}

/* Dark theme override for title */
[data-theme="dark"] .contest-title {
  color: #ffffff !important;
}

/* Metadata container below contest title */
.contest-meta {
  display: flex;
  align-items: center;
  gap: 1rem;
  flex-wrap: wrap;
}

/* Base card container with border and shadow */
.card {
  border: 1px solid var(--wiki-border);
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  transition: box-shadow 0.2s ease;
}

/* Dark theme card background and border */
[data-theme="dark"] .card {
  background-color: #2a2a2a;
  border-color: #444;
}

/* Elevated shadow on card hover */
.card:hover {
  box-shadow: 0 4px 8px rgba(0, 102, 153, 0.15);
}

/* Card header with primary background */
.card-header {
  background-color: var(--wiki-primary);
  color: white;
  border-bottom: none;
  padding: 1rem 1.5rem;
  font-weight: 600;
}

/* Card body content area */
.card-body {
  padding: 1.5rem;
  color: var(--wiki-dark);
}

/* Paragraph spacing within card body */
.card-body p {
  margin-bottom: 0.75rem;
  color: var(--wiki-text);
}

/* Ensure strong text is visible in dark mode */
[data-theme="dark"] .card-body strong {
  color: #ffffff;
}

/* Base badge styling */
.badge {
  font-weight: 500;
  padding: 0.4em 0.8em;
  font-size: 0.85em;
}

/* Primary badge uses theme primary color */
.badge.bg-primary {
  background-color: var(--wiki-primary) !important;
}

/* Info badge styled as primary with white text */
.badge.bg-info {
  background-color: var(--wiki-primary) !important;
  color: white;
}

/* Remove default top margin from tables */
.table {
  margin-top: 0;
}

/* Table header with light background and primary accent */
.table thead th {
  background-color: rgba(0, 102, 153, 0.1);
  color: var(--wiki-primary);
  font-weight: 600;
  border-bottom: 2px solid var(--wiki-primary);
  padding: 0.75rem;
}

/* Dark theme table header with adjusted opacity */
[data-theme="dark"] .table thead th {
  background-color: rgba(93, 184, 230, 0.15);
  border-bottom-color: var(--wiki-primary);
}

/* Table body cell styling */
.table tbody td {
  padding: 0.75rem;
  vertical-align: middle;
  color: var(--wiki-text);
}

/* Row hover effect for better readability */
.table tbody tr:hover {
  background-color: var(--wiki-hover-bg);
}

/* Links within tables */
.table a {
  color: var(--wiki-primary);
  font-weight: 500;
  transition: color 0.2s ease;
}

/* Link hover state with underline */
.table a:hover {
  color: var(--wiki-primary-hover);
  text-decoration: underline;
}

/* Clickable article titles with pointer cursor */
.article-title-link {
  cursor: pointer;
  color: var(--wiki-primary);
  font-weight: 500;
  transition: color 0.2s ease;
}

.article-title-link:hover {
  color: var(--wiki-primary-hover);
  text-decoration: underline;
}

/* Primary outline button */
.btn-outline-primary {
  border-color: var(--wiki-primary);
  color: var(--wiki-primary);
  transition: all 0.2s ease;
}

/* Outline button hover with lift effect */
.btn-outline-primary:hover {
  background-color: var(--wiki-primary);
  border-color: var(--wiki-primary);
  color: white;
  transform: translateY(-1px);
  box-shadow: 0 2px 4px rgba(0, 102, 153, 0.3);
}

/* Solid primary button */
.btn-primary {
  background-color: var(--wiki-primary);
  border-color: var(--wiki-primary);
  transition: all 0.2s ease;
}

/* Primary button hover with lift effect */
.btn-primary:hover {
  background-color: var(--wiki-primary-hover);
  border-color: var(--wiki-primary-hover);
  transform: translateY(-1px);
  box-shadow: 0 2px 4px rgba(0, 102, 153, 0.3);
}

/* Danger button for destructive actions */
.btn-danger {
  background-color: var(--wiki-danger);
  border-color: var(--wiki-danger);
  color: white;
  transition: all 0.2s
}

/* Danger button hover state */
.btn-danger:hover {
  background-color: var(--wiki-danger-hover);
  border-color: var(--wiki-danger-hover);
  color: white;
  box-shadow: 0 2px 4px rgba(153, 0, 0, 0.2);
}

/* Dark theme danger button */
[data-theme="dark"] .btn-danger {
  background-color: #990000;
  border-color: #990000;
}

[data-theme="dark"] .btn-danger:hover {
  background-color: #7a0000;
  border-color: #7a0000;
}

/* Secondary outline button */
.btn-outline-secondary {
  border-color: var(--wiki-text-muted);
  color: var(--wiki-text-muted);
  transition: all 0.2s ease;
}

.btn-outline-secondary:hover {
  background-color: var(--wiki-text-muted);
  border-color: var(--wiki-text-muted);
  color: white;
}

/* Base alert with left border accent */
.alert {
  border-radius: 0.5rem;
  border-left: 4px solid;
  padding: 0.75rem 1rem;
}

/* Info alert with primary color scheme */
.alert-info {
  background-color: rgba(0, 102, 153, 0.1);
  border-color: var(--wiki-primary);
  color: var(--wiki-primary);
}

/* Dark theme info alert with higher opacity */
[data-theme="dark"] .alert-info {
  background-color: rgba(93, 184, 230, 0.2);
  border-color: var(--wiki-primary);
  color: var(--wiki-primary);
}

/* Danger alert for errors */
.alert-danger {
  background-color: rgba(153, 0, 0, 0.1);
  border-color: var(--wiki-danger);
  color: var(--wiki-danger);
}

/* Warning alert uses danger colors */
.alert-warning {
  background-color: rgba(153, 0, 0, 0.1);
  border-color: var(--wiki-danger);
  color: var(--wiki-danger);
}

/* Primary colored loading spinner */
.spinner-border.text-primary {
  color: var(--wiki-primary) !important;
  width: 3rem;
  height: 3rem;
  border-width: 0.3em;
}

/* Container for description content */
.description-section {
  margin-top: 0;
}

/* Text with preserved line breaks and word wrapping */
.description-text {
  white-space: pre-line;
  line-height: 1.6;
  margin-bottom: 0;
  color: var(--wiki-text);
  word-wrap: break-word;
  transition: color 0.3s ease;
}

[data-theme="dark"] .description-text {
  color: var(--wiki-text);
}

/* Autocomplete dropdown container */
.jury-autocomplete {
  border: 1px solid var(--wiki-border);
  border-top: none;
  border-radius: 0 0 4px 4px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  background-color: var(--wiki-card-bg);
  z-index: 1060;
  transition: background-color 0.2s ease;
}

/* Dark theme dropdown with deeper shadow */
[data-theme="dark"] .jury-autocomplete {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4);
}

/* Individual autocomplete suggestion item */
.jury-autocomplete .p-2 {
  transition: background-color 0.2s ease;
  color: var(--wiki-text);
}

/* Suggestion hover state */
.jury-autocomplete .p-2:hover {
  background-color: var(--wiki-hover-bg) !important;
}

/* Warning indicator for self-selection */
.jury-autocomplete .bg-warning-subtle {
  background-color: rgba(255, 193, 7, 0.25) !important;
  border-left: 4px solid #ffc107;
}

/* Dark theme self-selection warning */
[data-theme="dark"] .jury-autocomplete .bg-warning-subtle {
  background-color: rgba(255, 193, 7, 0.35) !important;
}

/* Badge displayed on self-selection warning */
.self-warning-badge {
  background-color: #ffc107;
  color: #000;
  padding: 2px 8px;
  border-radius: 10px;
  font-size: 0.75rem;
  font-weight: 600;
  white-space: nowrap;
}

[data-theme="dark"] .self-warning-badge {
  background-color: #ff9800;
  color: #fff;
}

/* Primary text color within autocomplete */
.jury-autocomplete .text-primary {
  color: var(--wiki-primary) !important;
}

/* Adjustments for screens 768px and below */
@media (max-width: 768px) {
  .contest-title {
    font-size: 2rem;
  }

  .card-body {
    padding: 1rem;
  }

  .table {
    font-size: 0.9rem;
  }

  .table thead th,
  .table tbody td {
    padding: 0.5rem;
  }
}

/* Modal that takes entire viewport */
.modal-fullscreen {
  width: 100vw;
  max-width: 100%;
  height: 100vh;
  margin: 0;
  padding: 0;
}

/* Modal content fills viewport height */
.modal-fullscreen .modal-content {
  height: 100vh;
  border: 0;
  border-radius: 0;
  display: flex;
  flex-direction: column;
}

/* Scrollable modal body */
.modal-fullscreen .modal-body {
  flex: 1;
  overflow-y: auto;
  padding: 2rem;
}

/* Row spacing within fullscreen modal */
.modal-fullscreen .modal-body .row {
  margin-bottom: 1rem;
}

/* Override margin-bottom utility class */
.modal-fullscreen .modal-body .mb-3 {
  margin-bottom: 1.5rem !important;
}

/* Center and constrain form width */
.modal-fullscreen .modal-body form {
  max-width: 1200px;
  margin: 0 auto;
}

/* Card container for scoring criteria */
.scoring-card {
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  overflow: hidden;
  margin-bottom: 1.5rem;
}

[data-theme="dark"] .scoring-card {
  background: #2a2a2a;
  border-color: #404040;
}

/* Inner content padding */
.scoring-content {
  padding: 1.25rem;
}

/* Base tag styling for categories */
.tag {
  display: inline-block;
  padding: 0.375rem 0.5rem;
  border-radius: 4px;
  font-size: 0.8125rem;
  font-weight: 600;
}

/* Multi-parameter tag in green */
.tag-multi {
  background: #28a745;
  color: white;
}

/* Simple scoring tag in blue */
.tag-simple {
  background: #17a2b8;
  color: white;
}

/* Flex container for scoring metadata */
.scoring-meta {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1.25rem;
  gap: 1rem;
  flex-wrap: wrap;
}

/* Maximum points display */
.max-points {
  color: var(--wiki-primary);
  font-weight: 600;
  font-size: 0.9375rem;
}

/* Vertical list of scoring parameters */
.params-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

/* Individual parameter container */
.param-item {
  padding: 0.5rem;
  background: #f9fafb;
  border-radius: 6px;
  border: 1px solid var(--wiki-primary);
}

[data-theme="dark"] .param-item {
  background: #1f1f1f;
}

/* Parameter label and value row */
.param-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.375rem;
}

/* Parameter name label */
.param-label {
  font-weight: 600;
  font-size: 0.9375rem;
}

/* Parameter point value badge */
.param-value {
  background: var(--wiki-primary);
  color: white;
  padding: 0.25rem 0.625rem;
  border-radius: 4px;
  font-weight: 600;
  font-size: 0.8125rem;
}

/* Additional parameter description */
.param-note {
  color: #6b7280;
  font-size: 0.8125rem;
  line-height: 1.4;
  margin: 0;
}

[data-theme="dark"] .param-note {
  color: #9ca3af;
}

/* Informational message box */
.info-note {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem;
  background: #eff6ff;
  border-radius: 4px;
  font-size: 0.8125rem;
  color: #1e40af;
}

[data-theme="dark"] .info-note {
  background: rgba(59, 130, 246, 0.15);
  color: #93c5fd;
}

.info-note i {
  font-size: 0.9375em;
}

/* Responsive grid for point items */
.points-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 1rem;
  margin-top: 1rem;
}

/* Individual point display card */
.point-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.5rem;
  background: #f9fafb;
  border-radius: 6px;
  border: 2px solid var(--wiki-border);
}

[data-theme="dark"] .point-item {
  background: #1f1f1f;
}

/* Point category label */
.point-label {
  font-weight: 500;
  color: #6b7280;
  font-size: 15px;
}

/* Numeric point value */
.point-value {
  font-weight: 700;
  font-size: 1.25rem;
  color: var(--wiki-primary)
}

/* Submission count display */
.submissions-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.5rem;
  background: #f9fafb;
  border-radius: 6px;
  margin-top: 1.25rem;
  font-size: 0.9375rem;
  border: 2px solid var(--wiki-border);
}

[data-theme="dark"] .submissions-info {
  background: #1f1f1f;
}

.submissions-info span {
  color: #6b7280;
  font-weight: 500;
}

/* Highlighted submission count */
.submissions-info strong {
  color: var(--wiki-primary);
  font-size: 1.25rem;
}

/* Adjustments for screens 640px and below */
@media (max-width: 640px) {
  .scoring-meta {
    flex-direction: column;
    align-items: flex-start;
  }

  .points-row {
    grid-template-columns: 1fr;
  }
}

/* Flex container for organizer chips */
.organizers-list {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

/* Vertical grid for organizer management */
.organizers-grid {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

/* Individual organizer card in management modal */
.organizer-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.5rem;
  background-color: var(--wiki-hover-bg);
  border: 1px solid var(--wiki-border);
  border-radius: 6px;
  transition: all 0.2s ease;
}

/* Organizer card hover with subtle highlight */
.organizer-card:hover {
  background-color: rgba(0, 102, 153, 0.05);
  border-color: var(--wiki-primary);
}

[data-theme="dark"] .organizer-card {
  background-color: #2a2a2a;
  border-color: #444;
}

[data-theme="dark"] .organizer-card:hover {
  background-color: rgba(93, 184, 230, 0.1);
}

/* Informational text about organizers */
.organizer-info-text {
  color: var(--wiki-text);
  font-size: 0.95rem;
  line-height: 1.6;
  padding: 0.75rem;
  background-color: rgba(40, 167, 69, 0.05);
  border-radius: 4px;
}

[data-theme="dark"] .organizer-info-text {
  background-color: rgba(40, 167, 69, 0.1);
}

/* Flex wrapper for organizer chips */
.organizers-flex {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  margin-top: 0.5rem;
}

/* Individual organizer chip/badge */
.organizer-chip {
  display: flex;
  align-items: center;
  padding: 0.50rem 1rem;
  background-color: var(--wiki-primary);
  color: white;
  border-radius: 8px;
  font-size: 0.95rem;
  transition: all 0.2s ease;
  position: relative;
}

/* Chip hover with lift effect */
.organizer-chip:hover {
  background-color: var(--wiki-primary);
  transform: translateY(-2px);
}

[data-theme="dark"] .organizer-chip {
  background-color: var(--wiki-primary);
}

[data-theme="dark"] .organizer-chip:hover {
  background-color: var(--wiki-primary);
}

/* Mobile adjustments for organizers section */
@media (max-width: 768px) {
  .organizers-flex {
    gap: 0.5rem;
  }

  .organizer-chip {
    padding: 0.5rem 0.75rem;
    font-size: 0.85rem;
  }

  .organizer-info-text {
    font-size: 0.85rem;
    padding: 0.5rem;
  }
}
</style>
