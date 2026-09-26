/* =========================================================
   GLOBAL VARIABLES
========================================================= */

let activityChart = null;
let activityMixChart = null;
let notifications = [];


/* =========================================================
   PAGE INITIALIZATION
========================================================= */

window.addEventListener("load", function () {

    loadDashboard();

});


/* =========================================================
   LOAD DASHBOARD
   Auth0 session is handled by the backend.
========================================================= */

async function loadDashboard() {

    const message = document.getElementById("message");
    const tokenSection = document.getElementById("tokenSection");
    const welcomeText = document.getElementById("welcomeText");

    /*
     * Hide the old manual JWT section.
     * Authentication is now handled through Auth0 + backend session.
     */

    if (tokenSection) {
        tokenSection.style.display = "none";
    }


    if (message) {
        message.innerText = "Loading dashboard...";
        message.style.color = "#667085";
    }


    try {

        const response = await fetch(
            "/user/dashboard",
            {
                method: "GET",
                credentials: "include"
            }
        );


        /* =====================================================
           NOT AUTHENTICATED
        ===================================================== */

        if (response.status === 401 || response.status === 403) {

            if (welcomeText) {
                welcomeText.innerText =
                    "Please login to access your dashboard.";
            }

            if (message) {
                message.innerText =
                    "Your login session has expired. Please login again.";
                message.style.color = "#dc2626";
            }

            return;
        }


        /* =====================================================
           OTHER API ERROR
        ===================================================== */

        if (!response.ok) {

            let errorMessage =
                "Failed to load dashboard.";

            try {

                const errorData =
                    await response.json();

                errorMessage =
                    errorData.detail ||
                    errorMessage;

            }

            catch (error) {

                console.error(
                    "Dashboard error response:",
                    error
                );

            }

            throw new Error(
                errorMessage
            );
        }


        /* =====================================================
           DASHBOARD DATA
        ===================================================== */

        const data =
            await response.json();


        console.log(
            "Dashboard Data:",
            data
        );


        /* =====================================================
           USER
        ===================================================== */

        if (welcomeText) {

            welcomeText.innerText =
                "Welcome back, " +
                (data.username || "User");

        }


        /* =====================================================
           STATISTICS
        ===================================================== */

        document.getElementById(
            "totalPosts"
        ).innerText =
            data.total_posts || 0;


        document.getElementById(
            "totalComments"
        ).innerText =
            data.total_comments || 0;


        document.getElementById(
            "totalLikesMade"
        ).innerText =
            data.total_likes_made || 0;


        document.getElementById(
            "totalLikesReceived"
        ).innerText =
            data.total_likes_received || 0;


        document.getElementById(
            "totalViews"
        ).innerText =
            data.total_views || 0;


        /* =====================================================
           ACTIVITY BAR CHART
        ===================================================== */

        if (activityChart) {

            activityChart.destroy();

        }


        const activityCanvas =
            document.getElementById(
                "activityChart"
            );


        if (activityCanvas) {

            const activityContext =
                activityCanvas.getContext("2d");


            activityChart =
                new Chart(
                    activityContext,
                    {

                        type: "bar",

                        data: {

                            labels: [
                                "Posts",
                                "Comments",
                                "Likes Made",
                                "Likes Received"
                            ],

                            datasets: [

                                {

                                    label:
                                        "Activity",

                                    data: [

                                        data.total_posts || 0,

                                        data.total_comments || 0,

                                        data.total_likes_made || 0,

                                        data.total_likes_received || 0

                                    ],

                                    borderWidth: 1,

                                    borderRadius: 8,

                                    backgroundColor: [
                                        "#6366f1",
                                        "#8b5cf6",
                                        "#ec4899",
                                        "#f59e0b"
                                    ]

                                }

                            ]

                        },

                        options: {

                            responsive: true,

                            maintainAspectRatio: false,

                            scales: {

                                y: {

                                    beginAtZero: true,

                                    ticks: {

                                        precision: 0

                                    }

                                }

                            },

                            plugins: {

                                legend: {

                                    display: false

                                }

                            }

                        }

                    }
                );

        }


        /* =====================================================
           ACTIVITY MIX DONUT CHART
        ===================================================== */

        if (activityMixChart) {

            activityMixChart.destroy();

        }


        const mixCanvas =
            document.getElementById(
                "activityMixChart"
            );


        if (mixCanvas) {

            const mixContext =
                mixCanvas.getContext("2d");


            activityMixChart =
                new Chart(
                    mixContext,
                    {

                        type: "doughnut",

                        data: {

                            labels: [
                                "Posts",
                                "Comments",
                                "Likes Made",
                                "Likes Received"
                            ],

                            datasets: [

                                {

                                    data: [

                                        data.total_posts || 0,

                                        data.total_comments || 0,

                                        data.total_likes_made || 0,

                                        data.total_likes_received || 0

                                    ],

                                    backgroundColor: [
                                        "#6366f1",
                                        "#8b5cf6",
                                        "#ec4899",
                                        "#f59e0b"
                                    ],

                                    borderWidth: 2

                                }

                            ]

                        },

                        options: {

                            responsive: true,

                            maintainAspectRatio: false,

                            cutout: "62%",

                            plugins: {

                                legend: {

                                    position: "bottom"

                                }

                            }

                        }

                    }
                );

        }


        /* =====================================================
           NOTIFICATIONS
        ===================================================== */

        await loadNotifications();


        /* =====================================================
           SUCCESS
        ===================================================== */

        if (message) {

            message.innerText =
                "Dashboard loaded successfully.";

            message.style.color =
                "#15803d";

        }

    }


    catch (error) {

        console.error(
            "Dashboard Error:",
            error
        );


        if (message) {

            message.innerText =
                "Error: " +
                error.message;

            message.style.color =
                "#dc2626";

        }

    }

}


/* =========================================================
   LOAD NOTIFICATIONS
========================================================= */

async function loadNotifications() {

    const notificationList =
        document.getElementById(
            "notificationList"
        );


    if (!notificationList) {
        return;
    }


    notificationList.innerHTML = `

        <div class="notification-loading">
            Loading notifications...
        </div>

    `;


    try {

        const response =
            await fetch(
                "/notifications/",
                {
                    method: "GET",
                    credentials: "include"
                }
            );


        if (response.status === 401 ||
            response.status === 403) {

            notificationList.innerHTML = `

                <div class="empty-notifications">
                    Please login to view notifications.
                </div>

            `;

            return;
        }


        if (!response.ok) {

            throw new Error(
                "Failed to load notifications"
            );

        }


        notifications =
            await response.json();


        renderNotifications();

    }


    catch (error) {

        console.error(
            "Notification Error:",
            error
        );


        notificationList.innerHTML = `

            <div class="empty-notifications">
                Unable to load notifications.
            </div>

        `;

    }

}


/* =========================================================
   RENDER NOTIFICATIONS
========================================================= */

function renderNotifications() {

    const notificationList =
        document.getElementById(
            "notificationList"
        );


    const notificationBadge =
        document.getElementById(
            "notificationBadge"
        );


    if (!notificationList ||
        !notificationBadge) {

        return;

    }


    if (
        !notifications ||
        notifications.length === 0
    ) {

        notificationList.innerHTML = `

            <div class="empty-notifications">
                No notifications yet.
            </div>

        `;


        notificationBadge.style.display =
            "none";


        return;

    }


    const unreadCount =
        notifications.filter(
            notification =>
                !notification.is_read
        ).length;


    if (unreadCount > 0) {

        notificationBadge.innerText =
            unreadCount > 99
                ? "99+"
                : unreadCount;


        notificationBadge.style.display =
            "flex";

    }

    else {

        notificationBadge.style.display =
            "none";

    }


    notificationList.innerHTML =
        notifications
            .map(
                notification => {

                    const unreadClass =
                        notification.is_read
                            ? ""
                            : "unread";


                    const notificationType =
                        notification.notification_type ||
                        "notification";


                    const message =
                        escapeHtml(
                            notification.message ||
                            ""
                        );


                    const timestamp =
                        formatTimestamp(
                            notification.created_at
                        );


                    return `

                        <div
                            class="notification-item ${unreadClass}"
                            onclick="markNotificationAsRead(${notification.id})"
                        >

                            <span class="notification-type">

                                ${escapeHtml(
                                    notificationType
                                )}

                            </span>


                            <p class="notification-message">

                                ${message}

                            </p>


                            <div class="notification-time">

                                ${timestamp}

                            </div>


                            ${
                                !notification.is_read
                                    ? `

                                        <button
                                            class="notification-read-button"
                                            onclick="
                                                event.stopPropagation();
                                                markNotificationAsRead(${notification.id})
                                            "
                                        >
                                            Mark read
                                        </button>

                                    `
                                    : ""
                            }

                        </div>

                    `;

                }
            )
            .join("");

}


/* =========================================================
   MARK NOTIFICATION AS READ
========================================================= */

async function markNotificationAsRead(
    notificationId
) {

    try {

        const response =
            await fetch(
                `/notifications/${notificationId}/read`,
                {
                    method: "PUT",
                    credentials: "include"
                }
            );


        if (!response.ok) {

            throw new Error(
                "Failed to mark notification as read"
            );

        }


        const notification =
            notifications.find(
                item =>
                    item.id === notificationId
            );


        if (notification) {

            notification.is_read =
                true;

        }


        renderNotifications();

    }


    catch (error) {

        console.error(
            "Mark Read Error:",
            error
        );

    }

}


/* =========================================================
   MARK ALL NOTIFICATIONS AS READ
========================================================= */

async function markAllNotificationsAsRead() {

    try {

        const response =
            await fetch(
                "/notifications/read-all",
                {
                    method: "PUT",
                    credentials: "include"
                }
            );


        if (!response.ok) {

            throw new Error(
                "Failed to mark all notifications as read"
            );

        }


        notifications.forEach(
            notification => {

                notification.is_read =
                    true;

            }
        );


        renderNotifications();

    }


    catch (error) {

        console.error(
            "Mark All Read Error:",
            error
        );

    }

}


/* =========================================================
   TOGGLE NOTIFICATIONS
========================================================= */

function toggleNotifications() {

    const dropdown =
        document.getElementById(
            "notificationDropdown"
        );


    if (!dropdown) {
        return;
    }


    dropdown.classList.toggle(
        "show"
    );


    if (
        dropdown.classList.contains("show")
    ) {

        loadNotifications();

    }

}


/* =========================================================
   CLOSE NOTIFICATION DROPDOWN
========================================================= */

document.addEventListener(
    "click",
    function(event) {

        const wrapper =
            document.querySelector(
                ".notification-wrapper"
            );


        const dropdown =
            document.getElementById(
                "notificationDropdown"
            );


        if (
            wrapper &&
            dropdown &&
            !wrapper.contains(
                event.target
            )
        ) {

            dropdown.classList.remove(
                "show"
            );

        }

    }
);


/* =========================================================
   FORMAT TIMESTAMP
========================================================= */

function formatTimestamp(
    timestamp
) {

    if (!timestamp) {
        return "";
    }


    const date =
        new Date(timestamp);


    if (
        Number.isNaN(
            date.getTime()
        )
    ) {

        return timestamp;

    }


    return date.toLocaleString(
        "en-IN",
        {

            day: "2-digit",

            month: "short",

            year: "numeric",

            hour: "2-digit",

            minute: "2-digit"

        }
    );

}


/* =========================================================
   ESCAPE HTML
========================================================= */

function escapeHtml(
    value
) {

    const div =
        document.createElement(
            "div"
        );


    div.textContent =
        value;


    return div.innerHTML;

}


/* =========================================================
   AI CHAT
========================================================= */

function toggleAIChat() {

    const chatWindow =
        document.getElementById(
            "aiChatWindow"
        );


    if (!chatWindow) {
        return;
    }


    chatWindow.classList.toggle(
        "show"
    );

}


/* =========================================================
   SEND AI MESSAGE
========================================================= */

async function sendAIMessage() {

    const questionInput =
        document.getElementById(
            "questionInput"
        );


    const sendButton =
        document.getElementById(
            "sendButton"
        );


    if (!questionInput ||
        !sendButton) {

        return;

    }


    const message =
        questionInput.value.trim();


    if (!message) {
        return;
    }


    addUserMessage(
        message
    );


    questionInput.value =
        "";


    sendButton.disabled =
        true;


    const thinkingMessage =
        addBotMessage(
            "Thinking..."
        );


    try {

        const response =
            await fetch(
                "/api/ai-support/",
                {

                    method: "POST",

                    credentials: "include",

                    headers: {

                        "Content-Type":
                            "application/json"

                    },

                    body: JSON.stringify({

                        message:
                            message

                    })

                }
            );


        if (!response.ok) {

            let errorMessage =
                "Unable to process your request.";


            try {

                const errorData =
                    await response.json();


                if (errorData.detail) {

                    errorMessage =
                        Array.isArray(
                            errorData.detail
                        )

                            ? errorData.detail
                                .map(
                                    item =>
                                        item.msg
                                )
                                .join(", ")

                            : errorData.detail;

                }

            }

            catch (error) {

                console.error(
                    error
                );

            }


            throw new Error(
                errorMessage
            );

        }


        const data =
            await response.json();


        if (thinkingMessage) {

            thinkingMessage.remove();

        }


        addBotMessage(
            data.ai_response ||
            "I couldn't generate a response."
        );

    }


    catch (error) {

        console.error(
            "AI Support Error:",
            error
        );


        if (thinkingMessage) {

            thinkingMessage.remove();

        }


        addBotMessage(
            "Sorry, I couldn't process your request right now. Please try again."
        );

    }


    sendButton.disabled =
        false;


    scrollChatToBottom();

}


/* =========================================================
   ADD USER MESSAGE
========================================================= */

function addUserMessage(
    message
) {

    const row =
        document.createElement(
            "div"
        );


    row.className =
        "message-row user-row";


    const bubble =
        document.createElement(
            "div"
        );


    bubble.className =
        "message user-message";


    bubble.textContent =
        message;


    row.appendChild(
        bubble
    );


    const chatMessages =
        document.getElementById(
            "chatMessages"
        );


    if (chatMessages) {

        chatMessages.appendChild(
            row
        );

    }


    scrollChatToBottom();

}


/* =========================================================
   ADD BOT MESSAGE
========================================================= */

function addBotMessage(
    message
) {

    const row =
        document.createElement(
            "div"
        );


    row.className =
        "message-row bot-row";


    const avatar =
        document.createElement(
            "div"
        );


    avatar.className =
        "message-avatar";


    avatar.textContent =
        "✦";


    const bubble =
        document.createElement(
            "div"
        );


    bubble.className =
        "message bot-message";


    bubble.textContent =
        message;


    row.appendChild(
        avatar
    );


    row.appendChild(
        bubble
    );


    const chatMessages =
        document.getElementById(
            "chatMessages"
        );


    if (chatMessages) {

        chatMessages.appendChild(
            row
        );

    }


    scrollChatToBottom();


    return row;

}


/* =========================================================
   SCROLL CHAT
========================================================= */

function scrollChatToBottom() {

    const chatMessages =
        document.getElementById(
            "chatMessages"
        );


    if (!chatMessages) {
        return;
    }


    chatMessages.scrollTop =
        chatMessages.scrollHeight;

}


/* =========================================================
   ENTER KEY FOR AI
========================================================= */

document.addEventListener(
    "DOMContentLoaded",
    function() {

        const questionInput =
            document.getElementById(
                "questionInput"
            );


        if (!questionInput) {
            return;
        }


        questionInput.addEventListener(
            "keydown",
            function(event) {

                if (
                    event.key === "Enter" &&
                    !event.shiftKey
                ) {

                    event.preventDefault();

                    sendAIMessage();

                }

            }
        );

    }
);