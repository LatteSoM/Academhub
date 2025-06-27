import {
    get_disciplines_and_teacher_for_theme,
    get_disciplines_with_cells,
    get_groups_by_curriculum_id,
    get_weeks_count_for_release, save_all_cells
} from "./api_requests/detail_ajaxes.js";

const curriculum_id = document.getElementsByClassName('getCurriculum').item(0).id.replace('curriculum', '');
const release_id = document.getElementsByClassName('getRelease').item(0).id.replace('release', '');
const course = document.getElementsByClassName('getCourse').item(0).textContent.replace('Курс: ', '')


const weeks_at_first_term = document.getElementById('weeks_at_first_term')
const weeks_at_second_term = document.getElementById('weeks_at_second_term')
const disciplines_table_container = document.getElementById('disciplines-table')
const groups_table_container = document.getElementById('groups-table')
const result_body_1 = document.getElementById('result_1')
const result_body_2 = document.getElementById('result_2')
const save_btn = document.getElementById('save_btn')


let groups_for_release;
let disciplines_for_release;
let disciplines_with_teachers;
let weeks;

document.addEventListener('DOMContentLoaded', async function () {

    groups_for_release = await get_groups_by_curriculum_id(curriculum_id);
    disciplines_with_teachers = await get_disciplines_and_teacher_for_theme(curriculum_id, course);
    disciplines_for_release = await get_disciplines_with_cells(curriculum_id, course, release_id);
    weeks = await get_weeks_count_for_release(release_id);

    if (weeks.first_term !== undefined) {
        weeks_at_first_term.value = weeks.first_term;
    }

    if (weeks.second_term !== undefined) {
        weeks_at_second_term.value = weeks.second_term;
    }

    weeks_at_first_term.addEventListener('change', function () {
        update_weeks(Number(this.value), 1)
        weeks_to_hours_at_week(1)
        generate_table_discipline()
        generate_result_table(1)
    });

    weeks_at_second_term.addEventListener('change', function () {
        update_weeks(Number(this.value), 2)
        weeks_to_hours_at_week(2)
        generate_table_discipline()
        generate_result_table(2)
    });

    generate_table_discipline()
    generate_table_groups()

    disciplines_table_container.addEventListener('scroll', function(e) {
        groups_table_container.scrollTop = e.target.scrollTop;
    });

    groups_table_container.addEventListener('scroll', function(e) {
        disciplines_table_container.scrollTop = e.target.scrollTop;
    });


    generate_result_table(1)
    generate_result_table(2)

    save_btn.addEventListener('click', async function () {
        await save_data()
    })
})


function update_weeks(new_weeks_count, term) {
    if (term === 1){
        weeks.first_term = new_weeks_count
    }
    else {
        weeks.second_term = new_weeks_count
    }
}


function generate_table_discipline() {
  // Проверка наличия данных
  if (!disciplines_for_release || disciplines_for_release.length === 0) {
    disciplines_table_container.innerHTML = '<p>Нет данных для отображения</p>';
    return;
  }

  // Очистка контейнера перед добавлением нового содержимого
  disciplines_table_container.innerHTML = '';

  // Создание элементов таблицы
  const table = document.createElement('table');

  // Создание заголовка таблицы (thead)
  const thead = document.createElement('thead');

  // Первая строка заголовка
  const headerRow1 = document.createElement('tr');
  headerRow1.classList.add('header-row');

  // Ячейки первой строки заголовка
  const headersRow1 = [
    { text: "№", rowspan: 2 },
    { text: "Дисциплина", rowspan: 2 },
    { text: "Код", rowspan: 2 },
    { text: "Семестр 1", colspan: 7 },
    { text: "Семестр 2", colspan: 7 }
  ];

  headersRow1.forEach(header => {
    const th = document.createElement('th');
    th.textContent = header.text;
    if (header.rowspan) {
      th.setAttribute('rowspan', header.rowspan);
    }
    if (header.colspan) {
      th.setAttribute('colspan', header.colspan);
    }
    headerRow1.appendChild(th);
  });
  thead.appendChild(headerRow1);

  // Вторая строка заголовка
  const headerRow2 = document.createElement('tr');
  headerRow2.classList.add('header-row');

  // Заголовки для семестра 1 и семестра 2 (по порядку)
  const semesterHeaders = [
    "Час в нед", "Час в сем", "2п/гр", "с/р", "конс", "КП", "экз",
    "Час в нед", "Час в сем", "2п/гр", "с/р", "конс", "КП", "экз"
  ];

  semesterHeaders.forEach(title => {
    const th = document.createElement('th');
    th.textContent = title;
    headerRow2.appendChild(th);
  });
  thead.appendChild(headerRow2);

  // Создание тела таблицы (tbody)
  const tbody = document.createElement('tbody');

  tbody.id = 'disciplines_body'

  // Генерация строк таблицы с данными
  disciplines_for_release.forEach((discipline, index) => {
      const discipline_index = discipline.discipline_code.split('.')[0]

      if (discipline_index !== 'УП' || discipline_index !== 'ПП') {
        const row = document.createElement('tr');

        // Создание и заполнение ячеек строки
        // № (номер дисциплины или порядковый индекс)
        const cell1 = document.createElement('td');
        cell1.textContent = index + 1;
        row.appendChild(cell1);

        // Название дисциплины
        const cell2 = document.createElement('td');
        cell2.classList.add('discipline-info');
        cell2.textContent = discipline.discipline_name || '';
        row.appendChild(cell2);

        // Код дисциплины
        const cell3 = document.createElement('td');
        cell3.textContent = discipline.discipline_code || '';
        row.appendChild(cell3);

        // Функция для создания input ячеек
        function createInputCell(value, type_work, term, discipline_id) {
          const td = document.createElement('td');
          const input = document.createElement('input');
          input.type = 'number';
          input.value = value || '0';
          input.classList.add('input_cell');

          input.addEventListener('change', function () {
              update_cell(this.value, type_work, term, discipline_id)
          })
          td.appendChild(input);
          return td;
        }

        // Функция для создания ячеек <p>
        function createPCell(value) {
          const td = document.createElement('td');
          const p = document.createElement('p');
          p.textContent = value || '0';
          p.classList.add('p_table');
          td.appendChild(p);
          return td;
        }

        // Для семестра 1
        row.appendChild(createInputCell(discipline.term_1.hours_at_week_cell, 'hours_at_week_cell', 1, discipline.discipline_id));
        row.appendChild(createPCell(discipline.term_1.term_hours_cell, 'term_hours_cell', 1, discipline.discipline_id));
        row.appendChild(createInputCell(discipline.term_1['2pgr_cell'], '2pgr_cell', 1, discipline.discipline_id));
        row.appendChild(createInputCell(discipline.term_1.indep_work_cell, 'indep_work_cell', 1, discipline.discipline_id));
        row.appendChild(createInputCell(discipline.term_1.cons_cell, 'cons_cell', 1, discipline.discipline_id));
        row.appendChild(createInputCell(discipline.term_1.course_project_cell, 'course_project_cell', 1, discipline.discipline_id));
        row.appendChild(createInputCell(discipline.term_1.exam_cell, 'exam_cell', 1, discipline.discipline_id));

        // Для семестра 2
        row.appendChild(createInputCell(discipline.term_2.hours_at_week_cell, 'hours_at_week_cell', 2, discipline.discipline_id));
        row.appendChild(createPCell(discipline.term_2.term_hours_cell, 'term_hours_cell', 2, discipline.discipline_id));
        row.appendChild(createInputCell(discipline.term_2['2pgr_cell'], '2pgr_cell', 2, discipline.discipline_id));
        row.appendChild(createInputCell(discipline.term_2.indep_work_cell, 'indep_work_cell', 2, discipline.discipline_id));
        row.appendChild(createInputCell(discipline.term_2.cons_cell, 'cons_cell', 2, discipline.discipline_id));
        row.appendChild(createInputCell(discipline.term_2.course_project_cell, 'course_project_cell', 2, discipline.discipline_id));
        row.appendChild(createInputCell(discipline.term_2.exam_cell, 'exam_cell', 2, discipline.discipline_id));

        tbody.appendChild(row);
      }
  });

  // Собираем таблицу и добавляем в контейнер

    tbody.addEventListener('click', function () {
        const clickedRow = event.target.closest('tr');

        // Удаляем выделение с ранее выбранной строки
        const currentSelectedRow = document.querySelector('.selected');
        if (currentSelectedRow) {
            currentSelectedRow.classList.remove('selected');
        }

        // Выделяем текущую строку
        clickedRow.classList.add('selected');
    })
  table.appendChild(thead);
  table.appendChild(tbody);
  disciplines_table_container.appendChild(table);
}



function generate_table_groups() {
    if (!groups_for_release || groups_for_release.length === 0) {
        groups_table_container.innerHTML = '<p>Нет данных для отображения</p>';
        return;
    }

    let tableHtml = `
    <table>
        <thead>
            <tr class="header-row">
    `;

    groups_for_release.forEach((group, index) => {
        tableHtml += `
            <th>${group.students_count}</th>
        `;
    });

    tableHtml += `
        </tr>
        <tr class="header-row">
    `;

    groups_for_release.forEach((group, index) => {
        tableHtml += `
            <th>${group.full_name}</th>
        `;
    });

    tableHtml += `
            </tr>
        </thead>
        <tbody>
    `;

    disciplines_for_release.forEach(discipline => {
        let tr = `
            <tr>
        `

        groups_for_release.forEach(group => {
            let surname = '';
            disciplines_with_teachers.forEach(disc_teachers => {
                if (disc_teachers.discipline_id === discipline.discipline_id){
                    disc_teachers.teachers.forEach(teacher => {
                        if (teacher.groups.includes(group.id)){
                            const teacher_name = teacher.teacher_name.split(' ')[0]
                            surname += teacher_name + ' '
                        }
                    })
                }
            })

            tr += `
                <td><p class="p_table">${surname}</p></td>
            `
        })
        tr += `
            </tr>
        `
        tableHtml += tr
    })

    tableHtml += `
        </tbody>
    </table>
    `;
    groups_table_container.innerHTML = tableHtml;
}


function update_cell(value, type_of_work, term, discipline_id){
    disciplines_for_release.forEach(discipline => {
        if (discipline.discipline_id === discipline_id) {
            const term_key = 'term_' + term;
            discipline[term_key][type_of_work] = Number(value)
        }
    })

    generate_result_table(term)
}

function generate_result_table(term) {
    function createPCell(value) {
          const td = document.createElement('td');
          const p = document.createElement('p');
          p.textContent = value || '0';
          p.classList.add('p_table');
          td.appendChild(p);
          return td;
        }


    if (Number(term) === 1) {
        result_body_1.innerHTML = ''
        const row = document.createElement('tr');

        let hours_at_week_cell = 0;
        let term_hours_cell = 0;
        let pgr_cell = 0;
        let indep_work_cell = 0;
        let cons_cell = 0;
        let course_project_cell = 0;
        let exam_cell = 0;

        disciplines_for_release.forEach(discipline => {
            hours_at_week_cell += Number(discipline.term_1.hours_at_week_cell);
            term_hours_cell += Number(discipline.term_1.term_hours_cell);
            pgr_cell += Number(discipline.term_1['2pgr_cell']);
            indep_work_cell += Number(discipline.term_1.indep_work_cell);
            cons_cell += Number(discipline.term_1.cons_cell);
            course_project_cell += Number(discipline.term_1.course_project_cell);
            exam_cell += Number(discipline.term_1.exam_cell);
        })
        row.appendChild(createPCell(hours_at_week_cell));
        row.appendChild(createPCell(term_hours_cell));
        row.appendChild(createPCell(pgr_cell));
        row.appendChild(createPCell(indep_work_cell));
        row.appendChild(createPCell(cons_cell));
        row.appendChild(createPCell(course_project_cell));
        row.appendChild(createPCell(exam_cell));

        result_body_1.appendChild(row)
    }
    else {
        result_body_2.innerHTML = ''
        const row = document.createElement('tr');

        let hours_at_week_cell = 0;
        let term_hours_cell = 0;
        let pgr_cell = 0;
        let indep_work_cell = 0;
        let cons_cell = 0;
        let course_project_cell = 0;
        let exam_cell = 0;

        disciplines_for_release.forEach(discipline => {
            hours_at_week_cell += Number(discipline.term_2.hours_at_week_cell);
            term_hours_cell += Number(discipline.term_2.term_hours_cell);
            pgr_cell += Number(discipline.term_2['2pgr_cell']);
            indep_work_cell += Number(discipline.term_2.indep_work_cell);
            cons_cell += Number(discipline.term_2.cons_cell);
            course_project_cell += Number(discipline.term_2.course_project_cell);
            exam_cell += Number(discipline.term_2.exam_cell);
        })
        row.appendChild(createPCell(hours_at_week_cell));
        row.appendChild(createPCell(term_hours_cell));
        row.appendChild(createPCell(pgr_cell));
        row.appendChild(createPCell(indep_work_cell));
        row.appendChild(createPCell(cons_cell));
        row.appendChild(createPCell(course_project_cell));
        row.appendChild(createPCell(exam_cell));

        result_body_2.appendChild(row)
    }
}

function weeks_to_hours_at_week(term){
    disciplines_for_release.forEach(discipline => {
        if (term === 1) {
            discipline.term_1.hours_at_week_cell = Math.round(discipline.term_1.term_hours_cell / weeks.first_term)
        }
        else {
            discipline.term_2.hours_at_week_cell = Math.round(discipline.term_2.term_hours_cell / weeks.second_term)
        }
    })
}


async function save_data() {

    if (weeks.first_term === "" || weeks.first_term === 0) {
        alert("Не заполнена ячейка недель для первого семестра")
        return;
    }

    else if (weeks.second_term === "" || weeks.second_term === 0) {
        alert("Не заполнена ячейка недель для первого семестра")
        return;
    }

    const message = await save_all_cells(release_id, disciplines_for_release, weeks);
    alert(message);
}


document.addEventListener('click', function() {
    const isClickInsideTable = event.target.closest('#disciplines_body');

    // Если клик произошёл вне таблицы, снимаем выделение
    if (!isClickInsideTable) {
        const selectedRows = document.querySelectorAll('.selected');
        selectedRows.forEach(row => row.classList.remove('selected'));
    }
});