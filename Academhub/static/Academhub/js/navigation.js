document.addEventListener('DOMContentLoaded', function () {
    const navItems = document.querySelectorAll('.nav-item.has-children');

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
});