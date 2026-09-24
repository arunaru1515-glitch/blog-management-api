// ============================================================
// AI SUPPORT CHAT
// ============================================================

const questionInput =
    document.getElementById("questionInput");

const sendButton =
    document.getElementById("sendButton");

const chatMessages =
    document.getElementById("chatMessages");


// ============================================================
// SEND MESSAGE
// ============================================================

async function sendMessage() {

    const message =
        questionInput.value.trim();


    // --------------------------------------------------------
    // EMPTY MESSAGE
    // --------------------------------------------------------

    if (!message) {
        return;
    }


    // --------------------------------------------------------
    // DISPLAY USER MESSAGE
    // --------------------------------------------------------

    addUserMessage(message);


    // --------------------------------------------------------
    // CLEAR INPUT
    // --------------------------------------------------------

    questionInput.value = "";


    // --------------------------------------------------------
    // SHOW TYPING MESSAGE
    // --------------------------------------------------------

    const loadingMessage =
        addBotMessage("Thinking...");


    try {

        // ----------------------------------------------------
        // SEND REQUEST TO FASTAPI
        // ----------------------------------------------------

        const response =
            await fetch(
                "/api/ai-support/",
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify({
                        message: message
                    })
                }
            );


        // ----------------------------------------------------
        // CHECK RESPONSE
        // ----------------------------------------------------

        if (!response.ok) {

            let errorText =
                "Unable to process your request.";

            try {

                const errorData =
                    await response.json();

                console.error(
                    "AI Support API Error:",
                    errorData
                );

                if (errorData.detail) {

                    errorText =
                        Array.isArray(errorData.detail)
                            ? errorData.detail
                                .map(item => item.msg)
                                .join(", ")
                            : errorData.detail;
                }

            } catch (error) {

                console.error(
                    "Error reading API error:",
                    error
                );
            }

            throw new Error(errorText);
        }


        // ----------------------------------------------------
        // READ RESPONSE
        // ----------------------------------------------------

        const data =
            await response.json();


        console.log(
            "AI Support Response:",
            data
        );


        // ----------------------------------------------------
        // REMOVE THINKING MESSAGE
        // ----------------------------------------------------

        if (loadingMessage) {

            loadingMessage.remove();

        }


        // ----------------------------------------------------
        // DISPLAY AI RESPONSE
        // ----------------------------------------------------

        addBotMessage(
            data.ai_response ||
            "I couldn't generate a response."
        );


    } catch (error) {

        console.error(
            "AI Support Error:",
            error
        );


        // ----------------------------------------------------
        // REMOVE THINKING MESSAGE
        // ----------------------------------------------------

        if (loadingMessage) {

            loadingMessage.remove();

        }


        // ----------------------------------------------------
        // DISPLAY ERROR
        // ----------------------------------------------------

        addBotMessage(
            "Sorry, I couldn't process your request right now. Please try again."
        );

    }


    // --------------------------------------------------------
    // SCROLL TO BOTTOM
    // --------------------------------------------------------

    scrollToBottom();
}


// ============================================================
// ADD USER MESSAGE
// ============================================================

function addUserMessage(message) {

    const row =
        document.createElement("div");

    row.className =
        "message-row user-row";


    const bubble =
        document.createElement("div");

    bubble.className =
        "message user-message";


    bubble.textContent =
        message;


    row.appendChild(bubble);

    chatMessages.appendChild(row);


    scrollToBottom();
}


// ============================================================
// ADD BOT MESSAGE
// ============================================================

function addBotMessage(message) {

    const row =
        document.createElement("div");

    row.className =
        "message-row bot-row";


    const avatar =
        document.createElement("div");

    avatar.className =
        "message-avatar";

    avatar.textContent =
        "✦";


    const bubble =
        document.createElement("div");

    bubble.className =
        "message bot-message";


    bubble.textContent =
        message;


    row.appendChild(avatar);

    row.appendChild(bubble);

    chatMessages.appendChild(row);


    scrollToBottom();


    return row;
}


// ============================================================
// SCROLL CHAT TO BOTTOM
// ============================================================

function scrollToBottom() {

    if (!chatMessages) {
        return;
    }


    chatMessages.scrollTop =
        chatMessages.scrollHeight;
}


// ============================================================
// ENTER KEY SUPPORT
// ============================================================

if (questionInput) {

    questionInput.addEventListener(
        "keydown",
        function(event) {

            if (
                event.key === "Enter" &&
                !event.shiftKey
            ) {

                event.preventDefault();

                sendMessage();
            }

        }
    );

}


// ============================================================
// BUTTON ENTER SUPPORT
// ============================================================

if (sendButton) {

    sendButton.addEventListener(
        "click",
        function() {

            sendMessage();

        }
    );

}