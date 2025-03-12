const change_model = () => {
    const models = document.querySelectorAll('.model-item');
    const permissions_block = document.querySelectorAll('.permissions-block');

    let current_active_model = null;
    let current_active_permission_block = null;

    const find_permissions = (dataModel) => {
        return Array.from(permissions_block).find(block => block.getAttribute('data-model') === dataModel);
    };

    const remove_model_active = (remove_model) => {
        if (current_active_model) {
            current_active_model.classList.remove('model-active');
            current_active_permission_block.classList.add('permission_block_deactivate');
        }
    };

    const add_model_active = (add_model) => {
        const parent = add_model.parentElement;
        parent.classList.add('model-active');
        current_active_model = parent;

        const permission_block = find_permissions(add_model.getAttribute('data-model'));
        current_active_permission_block = permission_block;
        current_active_permission_block.classList.remove('permission_block_deactivate');
    };

    models.forEach(model => {
        model.addEventListener('click', function () {
            remove_model_active(this);
            add_model_active(this);
        });
    });
};

const generate_summary = () => {
    const summary_list = document.querySelector('.summary-list');
    const hiddenInput = document.querySelector(".hidden_permissions"); // Предполагаемый name
    let summary_items = {};

    const inputs_action = document.querySelectorAll('.permission-item > input[type="checkbox"]');

    const toggleActions = () => {
        const items = document.querySelectorAll('.model-name');
        items.forEach(item => {
            item.addEventListener("click", function () {
                const toggleIcon = item.querySelector('.toggle-icon');
                const actionList = this.nextElementSibling;

                actionList.classList.toggle('collapsed');
                toggleIcon.textContent = actionList.classList.contains('collapsed') ? '▶' : '▼';
            });
        });
    };

    const generate_items = () => {
        if (Object.keys(summary_items).length > 0) {
            let template = ``;
            for (const [model_name, actions] of Object.entries(summary_items)) {
                template += `<div class="summary-item">`;
                template += `
                    <div class="model-name">
                        ${model_name}
                        <span class="toggle-icon">▼</span>
                    </div>
                `;
                template += `<ul class="action-list">`;
                for (const action of actions) {
                    template += `<li class="action-item">${action}</li>`;
                }
                template += `</ul>`;
                template += `</div>`;
            }
            return template;
        }
        return '';
    };

    const get_template = () => {
        return `
            <h4>Выбранные права</h4>
            <div class="summary-items">
                ${generate_items()}
            </div>
        `;
    };

    const render_template = () => {
        summary_list.innerHTML = get_template();
        toggleActions();
    };

    const add_summary_item = (input) => {
        const model_name = input.getAttribute('data-model');
        const action_name = input.getAttribute('action_name');
        if (!(model_name in summary_items)) {
            summary_items[model_name] = [];
        }
        if (!summary_items[model_name].includes(action_name)) {
            summary_items[model_name].push(action_name);
        }
    };

    const remove_summary_item = (input) => {
        const model_name = input.getAttribute('data-model');
        const action_name = input.getAttribute('action_name');
        if (model_name in summary_items) {
            const index = summary_items[model_name].indexOf(action_name);
            if (index !== -1) {
                summary_items[model_name].splice(index, 1);
                if (summary_items[model_name].length === 0) {
                    delete summary_items[model_name];
                }
            }
        }
    };

    const updateHiddenInput = () => {
        const selectedIds = Array.from(inputs_action)
            .filter(input => input.checked)
            .map(input => input.value);
        hiddenInput.value = selectedIds.join(',');
    };

    const init_checkboxes = () => {
        const initialIds = hiddenInput.value ? hiddenInput.value.split(',').filter(id => id) : [];
        inputs_action.forEach(input => {
            if (initialIds.includes(input.value)) {
                input.checked = true;
                add_summary_item(input);
            }

            input.addEventListener("change", function () {
                if (this.checked) {
                    add_summary_item(this);
                } else {
                    remove_summary_item(this);
                }
                updateHiddenInput();
                render_template();
            });
        });
    };

    init_checkboxes();
    render_template();
    updateHiddenInput(); // Устанавливаем начальное значение hidden input
};

const init = () => {
    change_model();
    generate_summary();
};

init();