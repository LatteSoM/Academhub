const disciplines = []

document.addEventListener('DOMContentLoaded', function() {
    const specialtySelect = document.getElementById('specialty');
    const studyPlanSelect = document.getElementById('study_plan');
    const courseSelect = document.getElementById('course');
    const groupsContainer = document.getElementById('groups');
    const termSelect = document.getElementById('termSelect');
    const disciplinesTbody = document.getElementById('disciplines-body');
    const selectAllCheckbox = document.getElementById('select_all_disciplines');
    const applyBulkButton = document.getElementById('apply_bulk_dates');
    const bulkStartDateInput = document.getElementById('bulk_start_date');
    const bulkEndDateInput = document.getElementById('bulk_end_date');

    // --- Get initial values from the json_script tag ---
    const initialSelections = JSON.parse(document.getElementById('initial-selections-data').textContent || '{}');
    const initialPlanId = initialSelections.plan_id || null;
    const initialCourseId = initialSelections.course_id || null;
    const initiallySelectedGroupIds = initialSelections.group_ids || [];

    // --- Helper function to clear subsequent selects ---
    function clearSelect(selectElement, message) {
        selectElement.innerHTML = `<option selected value="">${message}</option>`;
        selectElement.disabled = true;
    }

    function clearGroups(message = '<em class="theme-text-secondary">Выберите курс для отображения групп.</em>') {
        groupsContainer.innerHTML = message;
    }

    function clearDisciplinesTable(message = '<i>Выберите группу и семестр для отображения дисциплин.</i>') {
        disciplinesTbody.innerHTML = `<tr class="theme-surface empty-placeholder"><td colspan="5" class="text-center theme-text-secondary">${message}</td></tr>`;
        if (selectAllCheckbox) selectAllCheckbox.checked = false; // Reset select all
    }

    // --- Function to fetch and display disciplines ---
    function fetchDisciplines() {
        const studyPlanId = studyPlanSelect.value;
        const courseId = courseSelect.value;
        const termId = termSelect.value;
        // Get currently checked groups within this page
        const selectedGroupCheckboxes = groupsContainer.querySelectorAll('input[type="checkbox"]:checked');
        const currentSelectedGroupIds = Array.from(selectedGroupCheckboxes).map(cb => cb.value);

        if (!studyPlanId || !courseId || !termId || currentSelectedGroupIds.length === 0) {
            clearDisciplinesTable();
            // Optionally add a more specific message if groups aren't selected
            if (studyPlanId && courseId && termId && currentSelectedGroupIds.length === 0) {
                 clearDisciplinesTable('<i>Выберите хотя бы одну группу для отображения дисциплин.</i>');
            }
            return;
        }

        // Construct the API URL - Adjust if your API endpoint differs
        // Note: Sending groups might require a different API or parameter handling
        const apiUrl = `/CurriculumApp/api/disciplines_by_curriculum_course_term/?curriculum_id=${studyPlanId}&course=${courseId}&term=${termId}`;
        // If your API supports filtering by group IDs, add them:
        // apiUrl += `&groups=${currentSelectedGroupIds.join(',')}`;

        disciplinesTbody.innerHTML = `<tr class="theme-surface"><td colspan="5" class="text-center theme-text-secondary"><i>Загрузка дисциплин...</i></td></tr>`;

        fetch(apiUrl)
            .then(response => response.json())
            .then(data => {
                disciplinesTbody.innerHTML = ''; // Clear loading message
                if (data && data.length > 0) {
                    data.forEach(discipline => {
                        const row = document.createElement('tr');
                        row.className = 'theme-surface';

                        // Checkbox cell
                        const checkCell = document.createElement('td');
                        const checkbox = document.createElement('input');
                        checkbox.type = 'checkbox';
                        checkbox.className = 'discipline-select';
                        checkbox.name = `discipline_${discipline.discipline_id}`; // Use discipline_id from API response
                        checkbox.value = discipline.discipline_id;
                        checkCell.appendChild(checkbox);
                        row.appendChild(checkCell);

                        // Code cell
                        const codeCell = document.createElement('td');
                        codeCell.textContent = discipline.discipline_code;
                        row.appendChild(codeCell);

                        // Name cell
                        const nameCell = document.createElement('td');
                        nameCell.textContent = discipline.discipline_name;
                        row.appendChild(nameCell);

                        // Start Date cell
                        const startDateCell = document.createElement('td');
                        const startDateInput = document.createElement('input');
                        startDateInput.type = 'date';
                        startDateInput.className = 'form-control form-control-sm theme-input';
                        startDateInput.name = `start_date_${discipline.discipline_id}`;
                        // Pre-fill if data available (adjust property name if needed)
                        // startDateInput.value = discipline.attestation_start_date || '';
                        startDateCell.appendChild(startDateInput);
                        row.appendChild(startDateCell);

                        // End Date cell
                        const endDateCell = document.createElement('td');
                        const endDateInput = document.createElement('input');
                        endDateInput.type = 'date';
                        endDateInput.className = 'form-control form-control-sm theme-input';
                        endDateInput.name = `end_date_${discipline.discipline_id}`;
                        // Pre-fill if data available (adjust property name if needed)
                        // endDateInput.value = discipline.attestation_end_date || '';
                        endDateCell.appendChild(endDateInput);
                        row.appendChild(endDateCell);

                        disciplinesTbody.appendChild(row);
                    });
                    // Re-attach event listeners for new checkboxes if needed (delegation is better)
                    updateSelectAllState(); // Update select-all checkbox state
                } else {
                    clearDisciplinesTable('<i>Нет дисциплин для выбранных параметров.</i>');
                }
            })
            .catch(error => {
                console.error('Error fetching disciplines:', error);
                clearDisciplinesTable('<i class="text-danger">Ошибка загрузки дисциплин.</i>');
            });
    }

    // --- Event Listener for Specialty ---


    // --- Event Listener for Study Plan ---

    // --- Event Listener for Course ---
    courseSelect.addEventListener('change', function() {
        // Groups are usually tied to the Study Plan, not the course selection within it.
        // But changing the course *does* affect which disciplines are shown.
        fetchDisciplines();
    });

    // --- Event Listener for Term ---
    termSelect.addEventListener('change', fetchDisciplines);

    // --- Event Listener for Group Checkboxes (using delegation) ---
    groupsContainer.addEventListener('change', function(event) {
        if (event.target.matches('.group-select')) {
            fetchDisciplines();
        }
    });

    // --- Select All/None Disciplines ---
    function updateSelectAllState() {
         // Removed check as selectAllCheckbox should exist
         const disciplineCheckboxes = disciplinesTbody.querySelectorAll('.discipline-select');
         let allChecked = disciplineCheckboxes.length > 0; // Start assuming true if there are checkboxes
         disciplineCheckboxes.forEach(cb => {
             if (!cb.checked) {
                 allChecked = false;
             }
         });
         selectAllCheckbox.checked = allChecked;
         selectAllCheckbox.indeterminate = false; // Reset indeterminate state
    } // Close func

    selectAllCheckbox.addEventListener('change', function() {
        const disciplineCheckboxes = disciplinesTbody.querySelectorAll('.discipline-select');
        disciplineCheckboxes.forEach(checkbox => {
            checkbox.checked = selectAllCheckbox.checked;
        });
    }); // Close listener func

    // Use event delegation for dynamically added discipline checkboxes
    disciplinesTbody.addEventListener('change', function(event) {
        if (event.target.matches('.discipline-select')) {
             updateSelectAllState();
        }
    }); // Close listener func

    // --- Apply Bulk Dates ---
    applyBulkButton.addEventListener('click', function() {
        const startDate = bulkStartDateInput.value;
        const endDate = bulkEndDateInput.value;
        const selectedDisciplineCheckboxes = disciplinesTbody.querySelectorAll('.discipline-select:checked');

        if (!startDate && !endDate) {
            alert('Пожалуйста, выберите хотя бы одну дату для применения.');
            return;
        }
        if (selectedDisciplineCheckboxes.length === 0) {
             alert('Пожалуйста, выберите хотя бы одну дисциплину.');
             return;
        }

        selectedDisciplineCheckboxes.forEach(checkbox => {
            const row = checkbox.closest('tr');
            const startDateField = row.querySelector('input[type="date"][name^="start_date_"]');
            const endDateField = row.querySelector('input[type="date"][name^="end_date_"]');

            if (startDate && startDateField) {
                startDateField.value = startDate;
            }
            if (endDate && endDateField) {
                endDateField.value = endDate;
            }
        });
    }); // Close listener func

    // --- Initial Load Trigger ---
    // Prioritize triggering study plan change if it's pre-selected,
    // as this loads courses and groups. Otherwise, trigger specialty change.
    if (studyPlanSelect.value) {
        console.log("Initial load: Triggering study plan change.");
        studyPlanSelect.dispatchEvent(new Event('change'));
        // Note: The study plan change handler should subsequently trigger course change if needed.
    } else if (specialtySelect.value) {
        console.log("Initial load: Triggering specialty change.");
        specialtySelect.dispatchEvent(new Event('change'));
    } else {
        // If nothing is pre-selected, no initial fetch needed.
        console.log("Initial load: No pre-selections found.");
    }
}); // End DOMContentLoaded listener