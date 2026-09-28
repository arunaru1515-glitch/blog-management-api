/* =========================================================
   CREATE BLOG POST
   Publish Now / Draft / Schedule
========================================================= */

document.addEventListener("DOMContentLoaded", function () {

    const form = document.getElementById("createPostForm");

    const scheduleOption =
        document.getElementById("scheduleOption");

    const scheduleFields =
        document.getElementById("scheduleFields");

    const scheduledDate =
        document.getElementById("scheduledDate");

    const scheduledTime =
        document.getElementById("scheduledTime");

    const message =
        document.getElementById("message");

    const submitButton =
        document.querySelector(".submit-button");


    /* =====================================================
       CHECK FORM
    ===================================================== */

    if (!form) {
        console.error("Create post form not found.");
        return;
    }


    /* =====================================================
       SET MINIMUM DATE
    ===================================================== */

    const today = new Date();

    const year = today.getFullYear();

    const month = String(
        today.getMonth() + 1
    ).padStart(2, "0");

    const day = String(
        today.getDate()
    ).padStart(2, "0");

    scheduledDate.min =
        `${year}-${month}-${day}`;


    /* =====================================================
       PUBLISHING OPTION CHANGE
    ===================================================== */

    const publishOptions =
        document.querySelectorAll(
            'input[name="publish_option"]'
        );


    publishOptions.forEach(function (option) {

        option.addEventListener(
            "change",
            function () {

                if (
                    this.value === "schedule"
                ) {

                    scheduleFields.classList.remove(
                        "hidden"
                    );

                    scheduledDate.required = true;

                    scheduledTime.required = true;

                } else {

                    scheduleFields.classList.add(
                        "hidden"
                    );

                    scheduledDate.required = false;

                    scheduledTime.required = false;

                    scheduledDate.value = "";

                    scheduledTime.value = "";
                }

            }
        );

    });


    /* =====================================================
       SHOW MESSAGE
    ===================================================== */

    function showMessage(
        text,
        type = "error"
    ) {

        message.textContent = text;

        message.className =
            "message " + type;
    }


    /* =====================================================
       DASHBOARD
    ===================================================== */

    window.goToDashboard = function () {

        window.location.href =
            "/dashboard";

    };


    /* =====================================================
       CREATE POST
    ===================================================== */

    form.addEventListener(
        "submit",
        async function (event) {

            event.preventDefault();


            /* =============================================
               GET SELECTED OPTION
            ============================================= */

            const selectedOption =
                document.querySelector(
                    'input[name="publish_option"]:checked'
                );


            if (!selectedOption) {

                showMessage(
                    "Please select a publishing option."
                );

                return;
            }


            const publishOption =
                selectedOption.value;


            /* =============================================
               GET FORM VALUES
            ============================================= */

            const title =
                document.getElementById(
                    "title"
                ).value.trim();


            const content =
                document.getElementById(
                    "content"
                ).value.trim();


            const image =
                document.getElementById(
                    "image"
                ).files[0];


            /* =============================================
               BASIC VALIDATION
            ============================================= */

            if (!title) {

                showMessage(
                    "Please enter a blog title."
                );

                return;
            }


            if (!content) {

                showMessage(
                    "Please enter blog content."
                );

                return;
            }


            /* =============================================
               BUILD FORM DATA
            ============================================= */

            const formData =
                new FormData();


            formData.append(
                "title",
                title
            );


            formData.append(
                "content",
                content
            );


            formData.append(
                "publish_option",
                publishOption
            );


            /* =============================================
               SCHEDULE VALIDATION
            ============================================= */

            if (
                publishOption === "schedule"
            ) {

                if (
                    !scheduledDate.value ||
                    !scheduledTime.value
                ) {

                    showMessage(
                        "Please select both schedule date and time."
                    );

                    return;
                }


                /*
                 * Combine date + time
                 *
                 * Backend expects:
                 * YYYY-MM-DDTHH:MM:SS
                 */

                const scheduledDateTime =
                    `${scheduledDate.value}T${scheduledTime.value}:00`;


                const selectedDateTime =
                    new Date(
                        scheduledDateTime
                    );


                const currentDateTime =
                    new Date();


                /* =========================================
                   CHECK FUTURE TIME
                ========================================= */

                if (
                    selectedDateTime <=
                    currentDateTime
                ) {

                    showMessage(
                        "Scheduled time must be in the future."
                    );

                    return;
                }


                formData.append(
                    "scheduled_at",
                    scheduledDateTime
                );

            } else {

                /*
                 * Publish Now / Draft
                 * should not send scheduled_at
                 */

                formData.append(
                    "scheduled_at",
                    ""
                );
            }


            /* =============================================
               IMAGE
            ============================================= */

            if (image) {

                formData.append(
                    "image",
                    image
                );
            }


            /* =============================================
               GET ACCESS TOKEN
            ============================================= */

            const accessToken =
                localStorage.getItem(
                    "access_token"
                );


            if (!accessToken) {

                showMessage(
                    "Your session has expired. Please login again."
                );

                setTimeout(
                    function () {

                        window.location.href =
                            "/login";

                    },
                    1500
                );

                return;
            }


            /* =============================================
               DISABLE BUTTON
            ============================================= */

            submitButton.disabled = true;

            submitButton.textContent =
                "Creating...";


            showMessage(
                "Creating your blog post...",
                "info"
            );


            /* =============================================
               SEND REQUEST
            ============================================= */

            try {

                const response =
                    await fetch(
                        "/posts/",
                        {
                            method: "POST",

                            headers: {
                                "Authorization":
                                    `Bearer ${accessToken}`
                            },

                            body: formData
                        }
                    );


                /* =========================================
                   READ RESPONSE
                ========================================= */

                let result = {};

                try {

                    result =
                        await response.json();

                } catch (error) {

                    result = {};
                }


                /* =========================================
                   ERROR RESPONSE
                ========================================= */

                if (!response.ok) {

                    let errorMessage =
                        "Failed to create post.";


                    if (
                        result.detail
                    ) {

                        errorMessage =
                            result.detail;

                    }


                    showMessage(
                        errorMessage,
                        "error"
                    );


                    submitButton.disabled =
                        false;

                    submitButton.textContent =
                        "Create Post";

                    return;
                }


                /* =========================================
                   SUCCESS
                ========================================= */

                let successMessage =
                    "Blog post created successfully.";


                if (
                    publishOption === "publish"
                ) {

                    successMessage =
                        "Blog post published successfully.";

                } else if (
                    publishOption === "draft"
                ) {

                    successMessage =
                        "Blog post saved as draft successfully.";

                } else if (
                    publishOption === "schedule"
                ) {

                    successMessage =
                        "Blog post scheduled successfully.";
                }


                showMessage(
                    successMessage,
                    "success"
                );


                /* =========================================
                   REDIRECT TO DASHBOARD
                ========================================= */

                setTimeout(
                    function () {

                        window.location.href =
                            "/dashboard";

                    },
                    1200
                );


            } catch (error) {

                console.error(
                    "Create post error:",
                    error
                );


                showMessage(
                    "Unable to connect to the server. Please try again.",
                    "error"
                );


                submitButton.disabled =
                    false;

                submitButton.textContent =
                    "Create Post";
            }

        }
    );

});