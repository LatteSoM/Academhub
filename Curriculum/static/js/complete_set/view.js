let teachers = []
let disciplines = []

document.getElementById('specialty').addEventListener('change', function() {
    const specialtyId = this.value;
    const studyPlanSelect = document.getElementById('study_plan');
    const courseSelect = document.getElementById('course');
    const groupsContainer = document.getElementById('groups');

    if (!specialtyId || specialtyId === 'Выберите специальность') {
        studyPlanSelect.innerHTML = '<option>Сначала выберите специальность</option>';
        studyPlanSelect.disabled = true;
        courseSelect.innerHTML = '<option selected>Сначала выберите специальность и учебный план</option>';
        courseSelect.disabled = true;

        groupsContainer.innerHTML = '';
        return;
    }

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


document.getElementById('study_plan').addEventListener('change', function () {
    const studyPlanId = this.value;

    const groupsContainer = document.getElementById('groups');
    const courseSelect = document.getElementById('course');

    if (studyPlanId === 'Выберите учебный план'){
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
                input.checked = true;

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


document.getElementById('course').addEventListener('change', function () {
    const termValue = document.getElementById('termSelect').value
    const curriculumValue = document.getElementById('study_plan').value
    const tbody = document.getElementById('disciplines-body');

    if (curriculumValue === 'Выберите учебный план' || this.value === 'Выберите курс'){
        tbody.innerHTML = ''
        return
    }

    fetch(
        `/CurriculumApp/api/disciplines_by_curriculum_course_term/?curriculum_id=${curriculumValue}&course=${this.value}&term=${termValue}`
    )
        .then(response => response.json())
        .then(data => {

            tbody.innerHTML = '';

            if (data.length === 0) {
                tbody.innerHTML = `
                    <tr>
                        <td colspan="4">Нет данных для отображения</td>
                    </tr>`;
                return;
            }

            disciplines = data

            if (teachers.length !== 0){
                add_teachers_to_disciplines()
            }

            console.log(disciplines)
            renderDisciplinesTable(tbody)
        })
})


document.getElementById('termSelect').addEventListener('change', function () {
    const courseValue = document.getElementById('course').value
    const curriculumValue = document.getElementById('study_plan').value
    const tbody = document.getElementById('disciplines-body');

    if (curriculumValue === 'Выберите учебный план' || this.value === 'Выберите курс'){
        tbody.innerHTML = ''
        return
    }

    fetch(
        `/CurriculumApp/api/disciplines_by_curriculum_course_term/?curriculum_id=${curriculumValue}&course=${courseValue}&term=${this.value}`
    )
        .then(response => response.json())
        .then(data => {

            tbody.innerHTML = '';

            if (data.length === 0) {
                tbody.innerHTML = `
                    <tr>
                        <td colspan="4">Нет данных для отображения</td>
                    </tr>`;
                return;
            }
            disciplines = data

            if (teachers.length !== 0){
                add_teachers_to_disciplines()
            }

            console.log(disciplines)
            renderDisciplinesTable(tbody)
        })
})



document.getElementById('sendFileBtn').addEventListener('click', function () {

  const fileInput = document.getElementById('excel_file_import');
  const formData = new FormData();
  const curriculum = document.getElementById('study_plan');
  const course = document.getElementById('course');
  const tbody = document.getElementById('disciplines-body')

  formData.append('excel_file', fileInput.files[0]);
  const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
  formData.append('csrfmiddlewaretoken', csrfToken);


  try {
    const response = fetch('/CurriculumApp/api/import-teachers-excel/', {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': csrfToken
        }
    })
        .then(response => response.json())
        .then(data => {
            window.alert(data.message)
            teachers = data.teachers

            if (curriculum !== 'Выберите учебный план' && course !== 'Выберите курс') {
                add_teachers_to_disciplines()
                renderDisciplinesTable(tbody)
            }
        })
  } catch (error) {
    console.error('Ошибка:', error);
  }
})


function renderDisciplinesTable(tbody) {
    console.log('fff')
    disciplines.forEach(discipline => {
        const row = document.createElement('tr');

        // Колонка с кодом дисциплины
        const codeCell = document.createElement('td');
        codeCell.textContent = discipline.discipline_code;
        row.appendChild(codeCell);

        // Колонка с названием дисциплины
        const nameCell = document.createElement('td');
        nameCell.textContent = discipline.discipline_name;
        row.appendChild(nameCell);

        // Колонка с преподавателями
        const teachersCell = document.createElement('td');
        const teachersDiv = document.createElement('div');
        teachersDiv.style.height = '100px';
        teachersDiv.style.overflowY = 'auto';
        teachersDiv.className = 'teachers-list';
        teachersDiv.dataset.disciplineId = discipline.discipline_id;

        // Добавляем преподавателей в блок
        discipline.teachers.forEach(teacher => {
            const teacherBlock = document.createElement('div');
            teacherBlock.className = 'teacher-block';
            teacherBlock.innerHTML = `
                <div class="teacher-name">${teacher.full_name}</div>
            `;
            teachersDiv.appendChild(teacherBlock);
        });

        teachersCell.appendChild(teachersDiv);
        row.appendChild(teachersCell);

        // Колонка с выбором преподавателя
        const selectCell = document.createElement('td');
        const select = document.createElement('select');
        select.className = 'form-select teacher-select';
        select.dataset.disciplineId = discipline.discipline_id;
        select.id = discipline.discipline_id;

        const defaultOption = document.createElement('option');
        defaultOption.value = '';
        defaultOption.textContent = 'Выберите преподавателя';
        defaultOption.selected = true;
        select.appendChild(defaultOption);

        // Добавляем преподавателей в выпадающий список
        teachers.forEach(teacher => {
            const option = document.createElement('option');
            option.value = teacher.teacher_id;
            option.textContent = `${teacher.full_name}`;
            select.appendChild(option);
        });
        
        
        select.addEventListener('change', function() {
            const value = this.value;

            if (value !== 'Выберите преподавателя' || value !== ''){
                add_teacher_to_discipline(this.value, this.id);
                renderDisciplinesTable(tbody)
                
            }
            
        })
        selectCell.appendChild(select);
        row.appendChild(selectCell);

        tbody.appendChild(row);
    });
}


function add_teachers_to_disciplines(){
    disciplines.forEach(discipline => {
        teachers.forEach(teacher => {

            discipline_cmc = discipline.discipline_code.split('.')[0].replaceAll(' ', '')

            if (discipline_cmc === teacher.cmc){
                already_exist = false;
                console.log(teacher.cmc)
                console.log(discipline)
                for (let discipline_teacher in discipline.teachers){
                    let disc_teacher = discipline.teachers[discipline_teacher]
                    if (disc_teacher.full_name === teacher.full_name
                         && disc_teacher.cmc === teacher.cmc){
                        already_exist = true;
                    }
                }

                if (!already_exist){
                    discipline.teachers.push(teacher)
                }
            }
        })
    })
}


function add_teacher_to_discipline(teacher_id, discipline_id){
    
    let teacher_to_add = '';
    for (let teacher in teachers){
        let teacher_ = teachers[teacher]
        if (teacher_.teacher_id === Number(teacher_id)){
            teacher_to_add = teacher_;
            break;
        }
    }

    console.log(teacher_to_add)
    for (let discipline in disciplines){

        let discipline_ = disciplines[discipline]
        if (discipline_.discipline_id === Number(discipline_id)){
            already_exist = false;
            for (let discipline_teacher in discipline_.teachers){
                let disc_teacher = discipline_.teachers[discipline_teacher]
                if (disc_teacher.full_name === teacher_to_add.full_name
                     && disc_teacher.cmc === teacher_to_add.cmc){

                    already_exist = true;
                }
            }

            if (!already_exist){
                discipline_.teachers.push(teacher_to_add)
            }
        }
    }

}