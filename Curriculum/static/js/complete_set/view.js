let speciality_id;
let curriculum_id;
let course_number;
let term = 1;
let teachers = []
let disciplines = []
let groups = []

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


document.getElementById('study_plan').addEventListener('change', function () {
    const studyPlanId = this.value;

    const groupsContainer = document.getElementById('groups');
    const courseSelect = document.getElementById('course');
    const tbody = document.getElementById('disciplines-body')

    if (studyPlanId === 'Выберите учебный план'){
        courseSelect.innerHTML = '<option>Сначала выберите учебный план</option>';
        courseSelect.disabled = true;

        groupsContainer.innerHTML = ''
        tbody.innerHTML = ''
        return;
    }

    curriculum_id = studyPlanId;
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
            groups = data.study_groups;
            renderStudyGroups(data, groupsContainer)

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

    course_number = this.value
    fetch(
        `/CurriculumApp/api/disciplines_by_curriculum_course_term/?curriculum_id=${curriculumValue}&course=${this.value}&term=${termValue}`
    )
        .then(response => response.json())
        .then(data => {

            if (data.length === 0) {
                tbody.innerHTML = `
                    <tr>
                        <td colspan="4">Нет данных для отображения</td>
                    </tr>`;
                return;
            }

            disciplines = data
            console.log(data)
            if (teachers.length !== 0){
                add_teachers_to_disciplines()
            }

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

    term = this.value;
    fetch(
        `/CurriculumApp/api/disciplines_by_curriculum_course_term/?curriculum_id=${curriculumValue}&course=${courseValue}&term=${this.value}`
    )
        .then(response => {
            console.log(response)
            return response.json()
        })
        .then(data => {
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

  const url = '/CurriculumApp/api/import_teachers_excel/'

  console.log(csrfToken)
  try {
    fetch(url, {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': csrfToken
        }
    })
        .then(response => {
            console.log(response)
            return response.json()
        })
        .then(data => {
            window.alert(data.message)
            teachers = data.teachers

            if (curriculum !== 'Выберите учебный план' && course !== 'Выберите курс') {
                add_teachers_to_disciplines()
                renderDisciplinesTable(tbody)
                console.log(teachers)
            }
        })
  } catch (error) {
      console.log(error)
      console.error('Ошибка:', error);
  }
})

document.getElementById('saveAllData').addEventListener('click', function () {
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
    formData.append('disciplines_with_teachers', JSON.stringify(disciplines));
    const checkedGroups = groups.filter(group => group.checked === true);
    formData.append('checked_groups', JSON.stringify(checkedGroups));

    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    formData.append('csrfmiddlewaretoken', csrfToken);


    try {
        const response = fetch('/CurriculumApp/api/save-all-changes/', {
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


function renderDisciplinesTable(tbody) {
    tbody.innerHTML = '';
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
            teacherBlock.className = 'teacher-block mb-2 p-2 rounded';

            const nameDiv = document.createElement('div');
            nameDiv.className = 'teacher-name';
            nameDiv.textContent = teacher.full_name;

            // Создаем кнопку с крестиком
            const deleteBtn = document.createElement('button');
            deleteBtn.className = 'btn btn-sm btn-outline-danger';
            deleteBtn.innerHTML = '&times;'; // Значок крестика
            deleteBtn.title = 'Удалить преподавателя';
            deleteBtn.id = teacher.teacher_id;

            // Обработчик клика на кнопку удаления
            deleteBtn.addEventListener('click', (e) => {
                e.stopPropagation(); // Предотвращаем всплытие события

                deleteTeacherFromDiscipline(discipline.teachers, deleteBtn.id)
                renderDisciplinesTable(tbody)
            });

            teacherBlock.appendChild(nameDiv);
            teacherBlock.appendChild(deleteBtn);
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


function renderStudyGroups(data, groupsContainer){
    data.study_groups.forEach(study_group => {
        const div = document.createElement('div');
        div.className = 'form-check';

        const input = document.createElement('input');
        input.type = 'checkbox';
        input.className = 'form-check-input';
        input.id = study_group.id;

        if (study_group.checked){
            input.checked = true;
        }

        input.addEventListener('change', function () {
            changeCheckOfGroup(input.id)
            console.log(groups)
        })

        const label = document.createElement('label');
        label.className = 'form-check-label';
        label.htmlFor = `group${study_group.id}`;
        label.textContent = study_group.full_name;

        div.appendChild(input);
        div.appendChild(label);
        groupsContainer.appendChild(div);
    })
}


function add_teachers_to_disciplines(){
    disciplines.forEach(discipline => {
        teachers.forEach(teacher => {
            discipline_cmc = discipline.discipline_code.split('.')[0].replaceAll(' ', '')
            discipline_speciality = discipline.discipline_speciality.split('.')[0].replaceAll(' ', '')

            if (discipline_cmc === teacher.cmc && discipline_speciality === teacher.speciality){
                const checkUnique = checkUniqueTeacher(discipline.teachers, teacher);

                if (!checkUnique){
                    discipline.teachers.push(teacher)
                }
            }
        })
    })
}


function add_teacher_to_discipline(teacher_id, discipline_id){
    let teacher_to_add = findTeacherById(teacher_id);

    for (let discipline in disciplines){

        let discipline_ = disciplines[discipline]
        if (discipline_.discipline_id === Number(discipline_id)){
            const checkUnique = checkUniqueTeacher(discipline_.teachers, teacher_to_add);
            if (!checkUnique){
                discipline_.teachers.push(teacher_to_add)
            }
        }
    }
}


function findTeacherById(teacher_id) {
    for (let teacher in teachers){
        let teacher_ = teachers[teacher]
        if (teacher_.teacher_id === Number(teacher_id)){
            return teacher_
        }
    }
}

function checkUniqueTeacher(teachersForDiscipline, teacher){
    let check = false
    teachersForDiscipline.forEach(discipline_teacher => {
        if (discipline_teacher.cmc === teacher.cmc
            && discipline_teacher.full_name === teacher.full_name
            && discipline_teacher.teacher_id === teacher.teacher_id){
            check = true
            return true;
        }
    })

    return check
}


function deleteTeacherFromDiscipline(teachersForDiscipline, teacher_id){
    const teacher = findTeacherById(teacher_id);

    for (const index in teachersForDiscipline){
        const discipline_teacher = teachersForDiscipline[index]
        if (discipline_teacher.cmc === teacher.cmc
            && discipline_teacher.full_name === teacher.full_name
            && discipline_teacher.teacher_id === teacher.teacher_id){
            teachersForDiscipline.splice(index, 1)
        }
    }
}


function changeCheckOfGroup(group_id){
    for (const index in groups){
        let group = groups[index];

        if (group.id === Number(group_id)) {
            group.checked = !group.checked
        }
    }
}

function sendDataOnSave(){

}
