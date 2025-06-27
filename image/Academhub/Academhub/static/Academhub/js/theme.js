function initTheme() {
    const themeToggle = document.getElementById('theme-toggle');
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)');
    
    // Set initial theme
    const savedTheme = localStorage.getItem('theme') || 
        (prefersDark.matches ? 'dark' : 'light');
    setTheme(savedTheme);

    // Theme toggle handler
    themeToggle.addEventListener('click', () => {
        const currentTheme = document.body.classList.contains('theme-dark') ? 
            'dark' : 'light';
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        setTheme(newTheme);
    });
}

function setTheme(theme) {
    document.body.classList.remove('theme-light', 'theme-dark');
    document.body.classList.add(`theme-${theme}`);
    localStorage.setItem('theme', theme);
    
    const icon = document.querySelector('.theme-toggle .material-icons');
    icon.textContent = theme === 'dark' ? 'light_mode' : 'dark_mode';
}

initTheme();