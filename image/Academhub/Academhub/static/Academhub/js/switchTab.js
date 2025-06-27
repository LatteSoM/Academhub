document.addEventListener('DOMContentLoaded', function () {
    const tabButtons = document.querySelectorAll('.tab-button');
    const tabPanes = document.querySelectorAll('.tab-pane');

    function switchTab(event) {
        tabButtons.forEach(button => button.classList.remove('active'));
        tabPanes.forEach(pane => pane.classList.remove('active'));

        const targetTab = event.target.getAttribute('data-tab');
        event.target.classList.add('active');
        document.getElementById(targetTab).classList.add('active');
    }

    tabButtons.forEach(button => {
        button.addEventListener('click', switchTab);
    });
});