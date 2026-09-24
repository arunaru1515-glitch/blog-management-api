from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.ai_support import AISupportActivity


# ============================================================
# ROUTER
# ============================================================

router = APIRouter(
    prefix="/api/ai-support",
    tags=["AI Support"]
)


# ============================================================
# REQUEST SCHEMA
# ============================================================

class AISupportRequest(BaseModel):
    message: str


# ============================================================
# PREDEFINED AI RESPONSES
# ============================================================

AI_RESPONSES = {

    "greeting": (
        "Hello! 👋 I'm your Blog Management Assistant. "
        "I can help you with posts, comments, likes, "
        "subscriptions, billing, profiles and dashboard analytics."
    ),

    "create": (
        "To create a post, log in to your account and use the "
        "Create Post option. Enter the title and content, "
        "then submit the post."
    ),

    "edit": (
        "To edit a post, open your post and select the Edit option. "
        "Update the required details and save the changes."
    ),

    "delete": (
        "To delete a post, open your post and select the Delete option. "
        "Only the appropriate post owner should perform this action."
    ),

    "comment": (
        "You can add a comment by opening a post and submitting "
        "your comment in the comment section."
    ),

    "like": (
        "You can like a post using the Like option. "
        "The dashboard also tracks the likes you make and the likes "
        "received on your posts."
    ),

    "subscription": (
        "The Blog Management platform provides different subscription "
        "plans with different limits for posts, images, likes and comments."
    ),

    "billing": (
        "Billing information is available through the subscription "
        "and billing features. Your billing history contains your "
        "previous transactions and invoice information."
    ),

    "profile": (
        "You can manage your profile information through your user "
        "account and update the available profile details."
    ),

    "dashboard": (
        "The dashboard provides information about your blog activity, "
        "including posts created, comments made, likes, likes received "
        "and post views."
    ),

    "platform": (
        "The Blog Management Platform is a FastAPI-based blogging system "
        "where users can create and manage posts, add comments, like posts, "
        "manage subscriptions, view billing information, receive notifications "
        "and monitor their activity through the dashboard."
    ),

    "notification": (
        "The notification center shows important activities such as "
        "likes, comments and subscription updates. You can also mark "
        "individual notifications or all notifications as read."
    ),

    "help": (
        "I can help you with creating, editing and deleting posts, "
        "comments, likes, subscriptions, billing, profiles, "
        "notifications and dashboard analytics."
    ),
}


# ============================================================
# AI RESPONSE LOGIC
# ============================================================

def get_ai_response(message: str) -> str:

    text = message.lower().strip()

    # --------------------------------------------------------
    # EMPTY MESSAGE
    # --------------------------------------------------------

    if not text:

        return (
            "Please enter a question and I'll help you "
            "with the Blog Management Platform."
        )


    # --------------------------------------------------------
    # GREETINGS
    # --------------------------------------------------------

    greeting_words = [
        "hi",
        "hello",
        "hey",
        "hai",
        "good morning",
        "good afternoon",
        "good evening"
    ]

    if any(word == text or text.startswith(word + " ")
           for word in greeting_words):

        return AI_RESPONSES["greeting"]


    # --------------------------------------------------------
    # CREATE POST
    # --------------------------------------------------------

    if (
        "create" in text
        and "post" in text
    ):

        return AI_RESPONSES["create"]


    if (
        "new post" in text
        or "add post" in text
        or "make a post" in text
    ):

        return AI_RESPONSES["create"]


    # --------------------------------------------------------
    # EDIT POST
    # --------------------------------------------------------

    if (
        "edit" in text
        and "post" in text
    ):

        return AI_RESPONSES["edit"]


    if (
        "update post" in text
        or "modify post" in text
    ):

        return AI_RESPONSES["edit"]


    # --------------------------------------------------------
    # DELETE POST
    # --------------------------------------------------------

    if (
        "delete" in text
        and "post" in text
    ):

        return AI_RESPONSES["delete"]


    if (
        "remove post" in text
        or "remove a post" in text
    ):

        return AI_RESPONSES["delete"]


    # --------------------------------------------------------
    # COMMENTS
    # --------------------------------------------------------

    if (
        "comment" in text
        or "comments" in text
    ):

        return AI_RESPONSES["comment"]


    # --------------------------------------------------------
    # LIKES
    # --------------------------------------------------------

    if (
        "like" in text
        or "likes" in text
    ):

        return AI_RESPONSES["like"]


    # --------------------------------------------------------
    # SUBSCRIPTION
    # --------------------------------------------------------

    if (
        "subscription" in text
        or "subscriptions" in text
        or "plan" in text
        or "plans" in text
        or "premium" in text
        or "pro plan" in text
    ):

        return AI_RESPONSES["subscription"]


    # --------------------------------------------------------
    # BILLING
    # --------------------------------------------------------

    if (
        "billing" in text
        or "payment" in text
        or "payments" in text
        or "invoice" in text
        or "invoices" in text
    ):

        return AI_RESPONSES["billing"]


    # --------------------------------------------------------
    # PROFILE / ACCOUNT
    # --------------------------------------------------------

    if (
        "profile" in text
        or "account" in text
    ):

        return AI_RESPONSES["profile"]


    # --------------------------------------------------------
    # DASHBOARD / ANALYTICS
    # --------------------------------------------------------

    if (
        "dashboard" in text
        or "analytics" in text
        or "activity" in text
        or "statistics" in text
        or "stats" in text
    ):

        return AI_RESPONSES["dashboard"]


    # --------------------------------------------------------
    # NOTIFICATIONS
    # --------------------------------------------------------

    if (
        "notification" in text
        or "notifications" in text
        or "alert" in text
    ):

        return AI_RESPONSES["notification"]


    # --------------------------------------------------------
    # PLATFORM QUESTIONS
    # --------------------------------------------------------

    if (
        "what is this" in text
        or "what is the platform" in text
        or "what is blog management" in text
        or "blog management platform" in text
        or "about the platform" in text
    ):

        return AI_RESPONSES["platform"]


    # --------------------------------------------------------
    # HELP
    # --------------------------------------------------------

    if (
        "help" in text
        or "what can you do" in text
        or "what can i ask" in text
    ):

        return AI_RESPONSES["help"]


    # --------------------------------------------------------
    # DEFAULT RESPONSE
    # --------------------------------------------------------

    return (
        "I'm here to help with the Blog Management Platform. "
        "You can ask me about creating, editing or deleting posts, "
        "comments, likes, subscriptions, billing, profiles, "
        "notifications or dashboard analytics."
    )


# ============================================================
# AI SUPPORT ENDPOINT
# ============================================================

@router.post("/")
def ai_support(
    request: AISupportRequest,
    db: Session = Depends(get_db)
):

    message = request.message.strip()

    ai_response = get_ai_response(message)


    # ========================================================
    # SAVE AI SUPPORT ACTIVITY
    # ========================================================

    activity = AISupportActivity(
        user_id=1,
        question=message,
        ai_response=ai_response
    )

    db.add(activity)

    db.commit()

    db.refresh(activity)


    # ========================================================
    # RESPONSE
    # ========================================================

    return {
        "question": message,
        "ai_response": ai_response
    }