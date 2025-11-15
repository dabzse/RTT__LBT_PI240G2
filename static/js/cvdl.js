document.addEventListener('click', function (ev) {
    let a = ev.target.closest ? ev.target.closest('a[href="#cvdl_modal"]') : null;
    if (a) {
        ev.preventDefault();
        try {
            let modalEl = document.getElementById('cvdl_modal');
            if (modalEl) {
                let modal = bootstrap.Modal.getInstance(modalEl) || new bootstrap.Modal(modalEl);
                modal.show();
            }
        } catch (e) {
            console.error('cvdl modal open error', e);
        }
    }
});
