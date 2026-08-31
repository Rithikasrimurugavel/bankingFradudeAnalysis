// Auto-dismiss flash messages after a few seconds for a cleaner UX.
document.addEventListener("DOMContentLoaded", function () {
    const flashMessages = document.querySelectorAll(".flash");

    flashMessages.forEach(function (flash) {
        setTimeout(function () {
            flash.style.transition = "opacity 0.4s ease";
            flash.style.opacity = "0";
            setTimeout(function () {
                flash.remove();
            }, 400);
        }, 4000);
    });
});
