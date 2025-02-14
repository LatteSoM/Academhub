document.addEventListener('DOMContentLoaded', function () {
    const navItems = document.querySelectorAll('.nav-item.has-children');
    const burgerMenu = document.getElementById('burger-menu');
    const sidebar = document.querySelector('.sidebar');
    navItems.forEach(item => {
        item.addEventListener('click', function (e) {
            e.stopPropagation();
            const subMenu = this.nextElementSibling;
            if (subMenu && subMenu.tagName === 'UL') {
                this.classList.toggle('open');
                subMenu.classList.toggle('open');
            }
        });
    });

    // if (burgerMenu) {
    //     burgerMenu.addEventListener('click', () => {
    //         sidebar.classList.toggle('open');
    //         burgerMenu.classList.toggle('open'); // Добавляем класс для анимации
    //     });
    // }


    // Handle burger menu click
    burgerMenu.addEventListener('click', () => {
        sidebar.classList.toggle('open');
        burgerMenu.classList.toggle('open')
        const icon = burgerMenu.querySelector('.material-icons');
        icon.textContent = sidebar.classList.contains('open') ? 'close' : 'menu';
    });

    // Close sidebar when clicking outside on mobile
    document.addEventListener('click', (e) => {
        if (window.innerWidth <= 768 &&
            !sidebar.contains(e.target) &&
            !burgerMenu.contains(e.target) &&
            sidebar.classList.contains('open')) {
            sidebar.classList.remove('open');
            burgerMenu.querySelector('.material-icons').textContent = 'menu';
        }
    });

    // Handle window resize
    window.addEventListener('resize', () => {
        if (window.innerWidth > 768) {
            sidebar.classList.remove('open');
            burgerMenu.querySelector('.material-icons').textContent = 'menu';
        }
    });
});