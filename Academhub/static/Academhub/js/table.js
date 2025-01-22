let select_inputs = new Set();

const header_input = document.querySelector('input[name=header]');
const selected_inputs = document.getElementsByName('selected_ids')

const send_change_event = (input, change_value) => {
    input.checked  = change_value;

    const event = new Event('change');

    input.dispatchEvent(event);
}

header_input.addEventListener('change', function() {
    selected_inputs.forEach(input => {
        send_change_event(input,this.checked);
    });
});

selected_inputs.forEach(input => {
    input.addEventListener('change', function() {
        this.checked ? select_inputs.add(this) : select_inputs.delete(this)
    });
});