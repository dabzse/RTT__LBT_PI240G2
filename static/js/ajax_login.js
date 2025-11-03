(function() {
    function getCookie(name) {
        let v = document.cookie.match('(^|;)\\s*' + name + '\\s*=\\s*([^;]+)');
        return v ? v.pop() : '';
    }

    document.addEventListener('DOMContentLoaded', function(){
        var form = document.getElementById('modal_login_form');
        if (!form) return;

        form.addEventListener('submit', function(ev){
            ev.preventDefault();
            var email = form.querySelector('[name="email"]').value;
            var password = form.querySelector('[name="password"]').value;
            var errEl = document.getElementById('login_error');
            errEl.textContent = '';

            fetch('/ajax/login/', {
                method: 'POST',
                credentials: 'same-origin',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: 'email=' + encodeURIComponent(email) + '&password=' + encodeURIComponent(password)
            }).then(function(resp) {
                return resp.json();
            }).then(function(data) {
                if (data && data.success) {
                    // Close modal and reload to update nav state
                    try {
                        var modalEl = document.getElementById('login_modal');
                        var modal = bootstrap.Modal.getInstance(modalEl) || new bootstrap.Modal(modalEl);
                        modal.hide();
                    } catch (e) {
                        // ignore
                    }
                    // reload to show authenticated UI
                    window.location.reload();
                } else {
                    errEl.textContent = data && data.error ? data.error : 'Ismeretlen hiba';
                }
            }).catch(function(err){
                errEl.textContent = 'Hálózati hiba';
                console.error('ajax login error', err);
            });
        });
    });
})();
