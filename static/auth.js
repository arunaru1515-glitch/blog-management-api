/* =========================================================
   AUTHENTICATION / LOGOUT
========================================================= */

document.addEventListener("DOMContentLoaded", function () {

    const logoutBtn =
        document.getElementById("logoutBtn");


    /* =====================================================
       CHECK LOGOUT BUTTON
    ===================================================== */

    if (!logoutBtn) {
        return;
    }


    /* =====================================================
       LOGOUT CLICK
    ===================================================== */

    logoutBtn.addEventListener(
        "click",
        async function () {

            /* Disable button while logging out */

            logoutBtn.disabled = true;

            logoutBtn.innerHTML =
                '<span class="logout-icon">↪</span> Logging out...';


            try {

                /* -----------------------------------------
                   CALL BACKEND LOGOUT
                ----------------------------------------- */

                const response = await fetch(
                    "/auth/logout",
                    {
                        method: "GET",
                        credentials: "include"
                    }
                );


                /* -----------------------------------------
                   REMOVE LOCAL TOKEN
                ----------------------------------------- */

                localStorage.removeItem(
                    "access_token"
                );


                /* -----------------------------------------
                   SUCCESS
                ----------------------------------------- */

                if (response.ok) {

                    window.location.href =
                        "/login";

                    return;
                }


                /* -----------------------------------------
                   LOGOUT FAILED
                ----------------------------------------- */

                alert(
                    "Logout failed. Please try again."
                );


                logoutBtn.disabled = false;

                logoutBtn.innerHTML =
                    '<span class="logout-icon">↪</span> Logout';


            } catch (error) {

                console.error(
                    "Logout error:",
                    error
                );


                /* -----------------------------------------
                   CLEAR TOKEN EVEN IF REQUEST FAILS
                ----------------------------------------- */

                localStorage.removeItem(
                    "access_token"
                );


                /* -----------------------------------------
                   REDIRECT TO LOGIN
                ----------------------------------------- */

                window.location.href =
                    "/login";

            }

        }
    );

});