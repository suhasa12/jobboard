/**
 * JobBoard ATS - Main Client-Side JavaScript
 * Includes:
 *  - Instant client-side keyword and skill filtering without page reload
 *  - Interactive application modal prefill & validation
 *  - Auto-dismissing alerts
 *  - Responsive table & badge helpers
 */

document.addEventListener('DOMContentLoaded', function () {
    // -------------------------------------------------------------
    // 1. Instant Client-Side Keyword & Skill Filtering
    // -------------------------------------------------------------
    const clientSearchInput = document.getElementById('client-keyword-filter');
    const jobCardsContainer = document.getElementById('job-cards-container');
    const visibleCountDisplay = document.getElementById('visible-jobs-count');
    const skillPillButtons = document.querySelectorAll('.filter-skill-pill');
    const activeSkillInput = document.getElementById('selected-skill-input');
    const noResultsNotice = document.getElementById('no-client-results');

    let activeSkill = '';

    function filterJobCards() {
        if (!jobCardsContainer) return;

        const searchTerm = clientSearchInput ? clientSearchInput.value.trim().toLowerCase() : '';
        const jobCards = jobCardsContainer.querySelectorAll('.job-card-col');
        let visibleCount = 0;

        jobCards.forEach(card => {
            const title = (card.getAttribute('data-title') || '').toLowerCase();
            const company = (card.getAttribute('data-company') || '').toLowerCase();
            const skills = (card.getAttribute('data-skills') || '').toLowerCase();
            const location = (card.getAttribute('data-location') || '').toLowerCase();
            const description = (card.getAttribute('data-description') || '').toLowerCase();

            // Check keyword match
            const matchesKeyword = !searchTerm || 
                title.includes(searchTerm) || 
                company.includes(searchTerm) || 
                skills.includes(searchTerm) || 
                location.includes(searchTerm) || 
                description.includes(searchTerm);

            // Check skill filter match
            const matchesSkill = !activeSkill || skills.includes(activeSkill.toLowerCase());

            if (matchesKeyword && matchesSkill) {
                card.classList.remove('d-none');
                visibleCount++;
            } else {
                card.classList.add('d-none');
            }
        });

        // Update counter
        if (visibleCountDisplay) {
            visibleCountDisplay.textContent = visibleCount;
        }

        // Toggle empty state notice
        if (noResultsNotice) {
            if (visibleCount === 0) {
                noResultsNotice.classList.remove('d-none');
            } else {
                noResultsNotice.classList.add('d-none');
            }
        }
    }

    if (clientSearchInput) {
        clientSearchInput.addEventListener('input', filterJobCards);
    }

    // Skill pills click events (instant filtering without reload)
    skillPillButtons.forEach(button => {
        button.addEventListener('click', function (e) {
            e.preventDefault();
            const clickedSkill = this.getAttribute('data-skill');

            if (activeSkill.toLowerCase() === clickedSkill.toLowerCase()) {
                // Deselect if clicked again
                activeSkill = '';
                this.classList.remove('active-skill');
            } else {
                // Select new skill
                skillPillButtons.forEach(btn => btn.classList.remove('active-skill'));
                activeSkill = clickedSkill;
                this.classList.add('active-skill');
            }

            if (activeSkillInput) {
                activeSkillInput.value = activeSkill;
            }

            filterJobCards();
        });
    });

    // Reset filters button
    const resetFiltersBtn = document.getElementById('reset-client-filters');
    if (resetFiltersBtn) {
        resetFiltersBtn.addEventListener('click', function () {
            if (clientSearchInput) clientSearchInput.value = '';
            activeSkill = '';
            if (activeSkillInput) activeSkillInput.value = '';
            skillPillButtons.forEach(btn => btn.classList.remove('active-skill'));
            filterJobCards();
        });
    }

    // -------------------------------------------------------------
    // 2. Client-side Form Validation
    // -------------------------------------------------------------
    const formsToValidate = document.querySelectorAll('.needs-validation');
    Array.from(formsToValidate).forEach(form => {
        form.addEventListener('submit', event => {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });

    // -------------------------------------------------------------
    // 3. Auto-Dismiss Alerts
    // -------------------------------------------------------------
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
            if (bsAlert) {
                bsAlert.close();
            }
        }, 6000);
    });

    // -------------------------------------------------------------
    // 4. Quick Status Update Confirmation
    // -------------------------------------------------------------
    const statusSelects = document.querySelectorAll('.auto-submit-status');
    statusSelects.forEach(select => {
        select.addEventListener('change', function () {
            const form = this.closest('form');
            if (form) {
                form.submit();
            }
        });
    });
});
