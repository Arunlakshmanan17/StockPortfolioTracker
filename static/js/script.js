/* =========================================
   SHOW / HIDE PASSWORD
========================================= */

function togglePassword() {

    const password =
        document.getElementById("password");

    const button =
        document.querySelector(".show-password");


    if (password.type === "password") {

        password.type = "text";

        button.textContent = "🙈";

    } else {

        password.type = "password";

        button.textContent = "👁";

    }

}



/* =========================================
   DEMO LOGIN
========================================= */

function demoLogin() {

    alert(
        "Demo mode will be connected to the dashboard soon."
    );

}