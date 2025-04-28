const init = () => {
    let __selected_input = new Set();

    const header_input = document.getElementById('header');
    const inputs = document.getElementsByName('selected_ids');

    const set_selected_input = (checked, input) => {
        checked ? __selected_input.add(input) : __selected_input.delete(input);
        console.log(__selected_input);
    };

    header_input.addEventListener('change', function() {
        const event = new Event('change');

        inputs.forEach(input =>{
            input.checked = this.checked;
            input.dispatchEvent(event);
        });
    });

    inputs.forEach(input => {
        input.addEventListener('change', function() {
            set_selected_input(this.checked, this);
        });
    });
};

init();