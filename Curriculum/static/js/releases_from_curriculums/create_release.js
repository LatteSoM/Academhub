const qualification_select = document.getElementById('qualifications');
const curriculum_select = document.getElementById('curriculum');
const create_btn = document.getElementById('createButton');
const course_select = document.getElementById('courses')


let curriculum_id = '';
let course_number = '';

qualification_select.addEventListener('change', function() {
    const qualificationId = this.value;

    if (!qualificationId || qualificationId === '-- Выберите квалификацию --') {
        curriculum_select.innerHTML = '<option>Сначала выберите квалификацию</option>';
        curriculum_select.disabled = true;
        return;
    }

    // AJAX-запрос для получения учебных планов
    fetch(`/CurriculumApp/api/curriculums_by_spec_id/?qualification_id=${qualificationId}`)
        .then(response => response.json())
        .then(data => {
            console.log(data)

            curriculum_select.innerHTML = '<option selected>Выберите учебный план</option>';

            data.forEach(plan => {
                const option = document.createElement('option');
                option.value = plan.id;
                option.textContent = plan.qualification_name + "-" + plan.admission_year + "-" + plan.basis_of_admission;
                curriculum_select.appendChild(option);
            });
            curriculum_select.disabled = false;
        })
        .catch(error => console.error('Error:', error));
});


curriculum_select.addEventListener('change', function () {
    const curriculumId = this.value

    if (!curriculumId || curriculumId === 'Выберите учебный план' || curriculumId === 'Сначала выберите квалификацию') {
        curriculum_id = ''
        course_number = ''
        course_select.disabled = true;
        return;
    }

    curriculum_id = curriculumId

    fetch(`/CurriculumApp/api/courses/?curriculum_id=${curriculum_id}`)
        .then(response => response.json())
        .then(data => {
            course_select.innerHTML = '<option selected>Выберите курс</option>';
            data.courses.forEach(course => {
                const option = document.createElement('option');
                option.value = course;
                option.textContent = course;
                course_select.appendChild(option);
            });
            course_select.disabled = false;

        })
        .catch(error => {
            console.error('Error:', error);
        });
})

course_select.addEventListener('change', function () {
    const curriculumValue = curriculum_select.value

    if (
        curriculumValue === 'Выберите учебный план'
        || this.value === '-- Сначала выберете учебный план --'
        || this.value === 'Выберите курс'
    ){
        course_number = '';
        return
    }

    course_number = this.value
})


create_btn.addEventListener('click', function () {
    console.log(curriculum_id)
    console.log(course_number)

    if (curriculum_id === '' || course_number === ''){
        alert('Одно из полей не заполнено')
        return;
    }

    const formData = new FormData();

    formData.append('curriculum_id', curriculum_id);
    formData.append('course_number', course_number);

    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    const url = '/CurriculumApp/api/create_new_release_from_curriculum/'

    try {
    fetch(url, {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': csrfToken
        }
    })
        .then(response => {
            return response.json()
        })
        .then(data => {
            console.log(data)
            if (data.release_id){
                window.location.href = "/CurriculumApp/releases/detail/" + data.release_id
            }
        })
  } catch (error) {
      console.error('Ошибка:', error);
  }
})