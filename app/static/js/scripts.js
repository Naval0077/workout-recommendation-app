// Example: Add interactivity to the login form
document.addEventListener('DOMContentLoaded', function () {
    const loginForm = document.querySelector('form');
    if (loginForm) {
        loginForm.addEventListener('submit', function (event) {
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;
            if (!email || !password) {
                alert('Please fill in all fields.');
                event.preventDefault();
            }
        });
    }
});