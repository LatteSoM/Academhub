document.addEventListener('DOMContentLoaded', function() {
    // Инициализация всех полей ввода Excel
    document.querySelectorAll('.coursework-coords-widget .excel-cell-input').forEach(function(input) {
        input.addEventListener('input', function() {
            this.value = this.value.toUpperCase();
        });
        
        input.addEventListener('keydown', function(e) {
            if (!/[A-Za-z0-9:]|Backspace|Delete|Arrow/.test(e.key)) {
                e.preventDefault();
            }
        });
    });
});