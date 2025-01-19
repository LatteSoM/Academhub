// Theme management
const themeToggle = document.getElementById('themeToggle');
const themeToggleIcon = themeToggle.querySelector('.theme-toggle-icon');

// Check for saved theme preference
const savedTheme = localStorage.getItem('theme');
if (savedTheme) {
    document.body.className = savedTheme;
    updateThemeIcon(savedTheme);
}

// Toggle theme function
function toggleTheme() {
    const currentTheme = document.body.className;
    const newTheme = currentTheme === 'light' ? 'dark' : 'light';

    document.body.className = newTheme;
    localStorage.setItem('theme', newTheme);
    updateThemeIcon(newTheme);
}

// Update theme icon
function updateThemeIcon(theme) {
    themeToggleIcon.textContent = theme === 'light' ? '🌙' : '☀️';
}

// Event listener for theme toggle
themeToggle.addEventListener('click', toggleTheme);