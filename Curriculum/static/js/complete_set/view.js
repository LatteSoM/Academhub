document.getElementById('specialty').addEventListener('change', function() {
    const specialtyId = this.value;
    const studyPlanSelect = document.getElementById('study_plan');

    if (!specialtyId) {
        studyPlanSelect.innerHTML = '<option>Сначала выберите специальность</option>';
        studyPlanSelect.disabled = true;
        return;
    }

    // AJAX-запрос для получения учебных планов
    fetch(`/CurriculumApp/api/study-plans/?specialty_id=${specialtyId}`)
        .then(response => response.json())
        .then(data => {
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


document.getElementById('study_plan').addEventListener('change', function () {
    const studyPlanId = this.value;

    const groupsContainer = document.getElementById('groups');
    const courseSelect = document.getElementById('course');

    if (!studyPlanId){
        courseSelect.innerHTML = '<option>Сначала выберите учебный план</option>';
        courseSelect.disabled = true;
        return;
    }

    // AJAX-запрос для получения курсов, дисциплин и групп
    fetch(`/CurriculumApp/api/courses_and_groups/?curriculum_id=${studyPlanId}`)
        .then(response => response.json())
        .then(data => {
            courseSelect.innerHTML = '<option selected>Выберите курс</option>';
            data.courses.forEach(course => {
                const option = document.createElement('option');
                option.value = course;
                option.textContent = course;
                courseSelect.appendChild(option);
            });
            courseSelect.disabled = false;

            groupsContainer.innerHTML = '';
            console.log(data)
            data.study_groups.forEach(study_group => {
                const div = document.createElement('div');
                div.className = 'form-check';

                const input = document.createElement('input');
                input.type = 'checkbox';
                input.className = 'form-check-input';
                input.id = `group${study_group.id}`;

                const label = document.createElement('label');
                label.className = 'form-check-label';
                label.htmlFor = `group${study_group.id}`;
                label.textContent = study_group.full_name;

                div.appendChild(input);
                div.appendChild(label);
                groupsContainer.appendChild(div);
            })
        })
        .catch(error => {
            groupsContainer.innerHTML = '<div class="text-danger">Ошибка загрузки данных</div>';
            console.error('Error:', error);
        });
})