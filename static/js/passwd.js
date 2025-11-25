(function() {
    try {
        let passwd_input = document.getElementById('modal_password');
        let toggle_btn = document.getElementById('modal_password_toggle');
        if (toggle_btn && passwd_input) {
            toggle_btn.addEventListener('click', function () {
                let icon = toggle_btn.querySelector('i');
                if (passwd_input.type === 'password') {
                    passwd_input.type = 'text';
                    if (icon) {
                        icon.classList.remove('bi-eye');
                        icon.classList.add('bi-eye-slash');
                    }
                    toggle_btn.setAttribute('aria-label', 'Jelszó elrejtése');
                }
                else {
                    passwd_input.type = 'password';
                    if (icon) {
                        icon.classList.remove('bi-eye-slash');
                        icon.classList.add('bi-eye');
                    }
                    toggle_btn.setAttribute('aria-label', 'Jelszó megjelenítése');
                }
                passwd_input.focus();
            });
        }
    }
    catch (e) {
        console.error('password toggle init error', e);
    }
})();
