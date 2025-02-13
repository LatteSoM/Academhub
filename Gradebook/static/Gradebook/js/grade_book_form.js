const init = () => {

    const select_group = document.getElementById('id_group')

    select_group.addEventListener('change', function(event) {
        group_id =  event.target.value;

        let url = new URL(location.href);

        url.searchParams.set('group_id', group_id);

        location.href = url;
    });

};

init();