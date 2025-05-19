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


let speciality_id;
let curriculum_id;
let course_number;
let term = 1;
let disciplines = []
let groups = []


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
    const apiUrl = `/CurriculumApp/api/disciplines_by_curriculum_course_term_for_attestation/?curriculum_id=${studyPlanId}&course=${courseId}&term=${termId}`;
    // If your API supports filtering by group IDs, add them:
    // apiUrl += `&groups=${currentSelectedGroupIds.join(',')}`;

    disciplinesTbody.innerHTML = `<tr class="theme-surface"><td colspan="5" class="text-center theme-text-secondary"><i>Загрузка дисциплин...</i></td></tr>`;

    const formData = new FormData();
    const checkedGroups = groups.filter(group => group.checked === false);
    formData.append('checked_groups', JSON.stringify(checkedGroups));

    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    formData.append('csrfmiddlewaretoken', csrfToken);

    fetch(apiUrl, {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': csrfToken
            }
        })
        .then(response => response.json())
        .then(data => {
            disciplines = data
            renderTable(data)
        })
        .catch(error => {
            console.error('Error fetching disciplines:', error);
            clearDisciplinesTable('<i class="text-danger">Ошибка загрузки дисциплин.</i>');
        });
}


function setStartDate(disciplineId, newStartAttestation){
    disciplines.forEach(discipline => {
        if (discipline.discipline_id === Number(disciplineId)){
            discipline.start_attestation = newStartAttestation;
            return true
        }
    })
}

function setEndDate(disciplineId, newEndAttestation){
    disciplines.forEach(discipline => {
        if (discipline.discipline_id === Number(disciplineId)){
            discipline.end_attestation = newEndAttestation;
            return true
        }
    })
}

function renderTable(data){
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
            startDateInput.value = discipline.start_attestation
            startDateInput.addEventListener('change', function () {
                setStartDate(discipline.discipline_id, this.value)
            })
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
            endDateInput.value = discipline.end_attestation
            endDateInput.addEventListener('change', function () {
                setEndDate(discipline.discipline_id, this.value)
                console.log(disciplines)
                console.log(groups)
            })
            // Pre-fill if data available (adjust property name if needed)
            // endDateInput.value = discipline.attestation_end_date || '';
            endDateCell.appendChild(endDateInput);
            row.appendChild(endDateCell);

            disciplinesTbody.appendChild(row);
        })

        updateSelectAllState();
    }
     else {
        clearDisciplinesTable('<i>Нет дисциплин для выбранных параметров.</i>');
     }
}

document.getElementById('specialty').addEventListener('change', function() {
    const specialtyId = this.value;
    const studyPlanSelect = document.getElementById('study_plan');
    const courseSelect = document.getElementById('course');
    const groupsContainer = document.getElementById('groups');
    const tbody = document.getElementById('disciplines-body')

    if (!specialtyId || specialtyId === 'Выберите специальность') {
        studyPlanSelect.innerHTML = '<option>Сначала выберите специальность</option>';
        studyPlanSelect.disabled = true;
        courseSelect.innerHTML = '<option selected>Сначала выберите специальность и учебный план</option>';
        courseSelect.disabled = true;

        groupsContainer.innerHTML = '';
        tbody.innerHTML = ''
        return;
    }

    speciality_id = specialtyId;
    // AJAX-запрос для получения учебных планов
    fetch(`/CurriculumApp/api/study-plans/?specialty_id=${specialtyId}`)
        .then(response => response.json())
        .then(data => {
            console.log(data)
            courseSelect.innerHTML = '<option selected>Сначала выберите учебный план</option>';
            courseSelect.disabled = true;

            groupsContainer.innerHTML = '';

            studyPlanSelect.innerHTML = '<option selected>Выберите учебный план</option>';
            data.forEach(plan => {
                const option = document.createElement('option');
                option.value = plan.id;
                option.textContent = plan.qualification_name + "-" + plan.admission_year + "-" + plan.basis_of_admission;
                studyPlanSelect.appendChild(option);
            });
            studyPlanSelect.disabled = false;
        })
        .catch(error => console.error('Error:', error));
});

studyPlanSelect.addEventListener('change', function() {
    const studyPlanId = this.value;
    curriculum_id = studyPlanId;

    clearSelect(courseSelect, 'Загрузка...');
    clearGroups();
    clearDisciplinesTable();

    if (!studyPlanId) {
        clearSelect(courseSelect, 'Сначала выберите учебный план');
        return;
    }

    fetch(`/CurriculumApp/api/courses_and_groups/?curriculum_id=${studyPlanId}`)
        .then(response => response.json())
        .then(data => {
            console.log("API Response (/courses_and_groups/):", data); // Log API response
            clearSelect(courseSelect, 'Выберите курс');
            data.courses.forEach(course => {
                const option = document.createElement('option');
                option.value = course;
                option.textContent = course;

                courseSelect.appendChild(option);
            });
            courseSelect.disabled = false;

            // Populate groups
            groupsContainer.innerHTML = ''; // Clear placeholder
             if (data.study_groups && data.study_groups.length > 0) {
                console.log("Populating groups..."); // Log before loop

                 groups = data.study_groups
                data.study_groups.forEach(study_group => {
                    const div = document.createElement('div');
                    div.className = 'form-check';
                    const input = document.createElement('input');
                    input.type = 'checkbox';
                    input.className = 'form-check-input group-select';
                    input.id = `group_${study_group.id}`;
                    input.value = study_group.id;
                    input.name = 'selected_groups_dynamic'; // Use a distinct name

                    input.addEventListener('change', function () {
                        changeCheckOfGroup(study_group.id)
                        console.log(groups)
                    })
                    // Check if this group was initially selected
                    // Check against initial IDs, coercing both to strings for comparison
                    const label = document.createElement('label');
                    label.className = 'form-check-label theme-text';
                    label.htmlFor = `group_${study_group.id}`;
                    label.textContent = study_group.full_name || study_group.name; // Use full_name if available
                    div.appendChild(input);
                    div.appendChild(label);
                    groupsContainer.appendChild(div);
                });
                console.log("Finished populating groups."); // Log after loop
             } else {
                 console.log("No study groups found in API response."); // Log if no groups
                 clearGroups('<em>Нет групп для этого плана.</em>');
             }
             // Trigger change if a course was pre-selected to load disciplines
             if (courseSelect.value) {
                 courseSelect.dispatchEvent(new Event('change'));
             } else {
                 // If no course pre-selected, but groups might be, try fetching disciplines
                 fetchDisciplines();
             }
        })
        .catch(error => {
            console.error('Error fetching courses/groups:', error); // Log fetch error
            clearSelect(courseSelect, 'Ошибка загрузки курсов');
            clearGroups('Ошибка загрузки групп.');
        });
});


courseSelect.addEventListener('change', function() {
    // Groups are usually tied to the Study Plan, not the course selection within it.
    // But changing the course *does* affect which disciplines are shown.
    course_number = this.value
    fetchDisciplines();
});

// --- Event Listener for Term ---
termSelect.addEventListener('change', function () {
    term = this.valueOf()
    fetchDisciplines()
});

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

            const discipline_id = startDateField.name.split('_')[2]
            console.log(discipline_id)
            setStartDate(discipline_id, startDate)
        }
        if (endDate && endDateField) {
            endDateField.value = endDate;

            const discipline_id = endDateField.name.split('_')[2]
            setEndDate(discipline_id, endDate)
        }
    });

    console.log(disciplines)
});


document.getElementById('save_periods').addEventListener('click', function () {
    const formData = new FormData();
    const curriculum = document.getElementById('study_plan');
    const speciality = document.getElementById('specialty');
    const course = document.getElementById('specialty');

    if (speciality.value === 'Выберите специальность'
        || curriculum.value === 'Выберите учебный план'
        || course.value === 'Выберите курс'){
        window.alert('Вы ничего не выбрали!')
        return;
    }
    console.log(speciality)
    formData.append('speciality_id', speciality_id);
    formData.append('curriculum_id', curriculum_id);
    formData.append('course', course_number);
    formData.append('term', term);
    formData.append('disciplines_with_periods', JSON.stringify(disciplines));

    const checkedGroups = groups.filter(group => group.checked === false);
    formData.append('checked_groups', JSON.stringify(checkedGroups));

    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    formData.append('csrfmiddlewaretoken', csrfToken);


    try {
        const response = fetch('/CurriculumApp/api/save-attestation-periods/', {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': csrfToken
            }
        })
            .then(response => response.json())
            .then(data => {
                window.alert(data.message);
            })
    } catch (error) {
        console.error('Ошибка:', error);
    }
})


function changeCheckOfGroup(group_id){
    for (const index in groups){
        let group = groups[index];

        if (group.id === Number(group_id)) {
            group.checked = !group.checked
        }
    }
}

