
export async function get_groups_by_curriculum_id(curriculum_id) {
    return fetch(`/CurriculumApp/api/get_groups_by_curriculum_id/?curriculum_id=${curriculum_id}`)
        .then(response => response.json())
        .then(data => {
            if (data.study_groups) {
                return data.study_groups;
            }

        })
        .catch(error => {
            console.error('Error:', error);
        });
}


export async function get_disciplines_and_teacher_for_theme(curriculum_id, course) {
    return fetch(`/CurriculumApp/api/get_disciplines_and_teacher_for_theme/?curriculum_id=${curriculum_id}&course=${course}`)
        .then(response => response.json())
        .then(data => {
            return data;
        })
        .catch(error => {
            console.error('Error:', error);
        });
}

export async function get_disciplines_with_cells(curriculum_id, course, release_id) {
    return await fetch(`/CurriculumApp/api/get_disciplines_with_cells/?curriculum_id=${curriculum_id}
    &course=${course}
    &release_id=${release_id}`)
        .then(response => response.json())
        .then(data => {

            return data;
        })
        .catch(error => {
            console.error('Error:', error);
        });
}

export async function get_weeks_count_for_release(release_id) {
    return await fetch(`/CurriculumApp/api/get_weeks_count_for_release/?release_id=${release_id}`)
        .then(response => response.json())
        .then(data => {
            return data;
        })
        .catch(error => {
            console.error('Error:', error);
        });
}

export async function save_all_cells(release_id, disciplines_data, weeks_data) {
    const formData = new FormData();

    formData.append('release_id', release_id);
    formData.append('disciplines_data', JSON.stringify(disciplines_data));
    formData.append('weeks_data', JSON.stringify(weeks_data));

    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    formData.append('csrfmiddlewaretoken', csrfToken);

    try {
        return await fetch('/CurriculumApp/api/save_all_cells/', {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': csrfToken
            }
        })
            .then(response => response.json())
            .then(data => {
                return data.message;
            })
    } catch (error) {
        console.error('Ошибка:', error);
    }
}