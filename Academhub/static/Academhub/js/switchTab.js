document.addEventListener('DOMContentLoaded', function () {
    const tabButtons = document.querySelectorAll('.tab-button');
    const tabPanes = document.querySelectorAll('.tab-pane');

    // Функция для переключения вкладок
    function switchTab(event) {
        // Убираем активный класс у всех кнопок и панелей
        tabButtons.forEach(button => button.classList.remove('active'));
        tabPanes.forEach(pane => pane.classList.remove('active'));

        // Добавляем активный класс к выбранной кнопке и соответствующей панели
        const targetTab = event.target.getAttribute('data-tab');
        event.target.classList.add('active');
        document.getElementById(targetTab).classList.add('active');
    }

    // Назначаем обработчик событий для каждой кнопки
    tabButtons.forEach(button => {
        button.addEventListener('click', switchTab);
    });
});