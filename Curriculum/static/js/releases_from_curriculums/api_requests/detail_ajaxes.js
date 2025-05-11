
export function get_groups_by_curriculum_id(curriculum_id) {
    let groups;
    fetch(`/CurriculumApp/api/get_groups_by_curriculum_id/?curriculum_id=${curriculum_id}`)
        .then(response => response.json())
        .then(data => {
            if (data.study_groups) {
                groups = data.study_groups
                console.log(groups)
            }

        })
        .catch(error => {
            console.error('Error:', error);
        });

    return groups;
}


export function get_disciplines_and_teacher_for_theme(curriculum_id, course, release_id) {
    let disciplines;

    fetch(`/CurriculumApp/api/get_disciplines_and_teacher_for_theme/?curriculum_id=${curriculum_id}&course=${course}
    &release_id=${release_id}`)
        .then(response => response.json())
        .then(data => {
            console.log(data)
            disciplines = data

        })
        .catch(error => {
            console.error('Error:', error);
        });

    return disciplines;
}