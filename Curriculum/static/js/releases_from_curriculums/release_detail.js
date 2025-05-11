import {get_disciplines_and_teacher_for_theme, get_groups_by_curriculum_id} from "./api_requests/detail_ajaxes.js";

const curriculum_id = document.getElementsByClassName('getCurriculum').item(0).id.replace('curriculum', '');
const release_id = document.getElementsByClassName('getRelease').item(0).id.replace('release', '');
const course = document.getElementsByClassName('getCourse').item(0).textContent.replace('Курс: ', '')


let groups_for_release;
let disciplines_for_release;

document.addEventListener('DOMContentLoaded', function () {

    groups_for_release = get_groups_by_curriculum_id(curriculum_id);
    disciplines_for_release = get_disciplines_and_teacher_for_theme(curriculum_id, course, release_id)

    console.log(course);
})