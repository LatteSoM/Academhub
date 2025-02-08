const init = () => {
    let __selected_input = new Set();
    
    const header_input = document.getElementById('header');
    const inputs = document.getElementsByName('selected_ids');

    header_input.addEventListener('change', function() {
        if (this.chacked)
        {
            inputs.forEach(input =>{
    
            });
        }
        else
        {
            inputs.forEach(input =>{
    
            });
        }
    });

    inputs.forEach(input => {
        input.addEventListener('change', function() {
            this.checked ? __selected_input.add(this) : __selected_input.delete(this);
        });
    });

};

init();