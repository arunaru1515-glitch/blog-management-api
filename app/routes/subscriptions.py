from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import uuid
import os

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from app.database.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.subscription import SubscriptionPlan
from app.models.billing_history import BillingHistory

from app.services.notification_service import create_notification


router = APIRouter(
    prefix="/subscriptions",
    tags=["Subscriptions"]
)


# ============================================================
# INVOICE GENERATION
# ============================================================

def generate_invoice(
    username: str,
    plan_name: str,
    price: float,
    start_date: datetime,
    end_date: datetime,
    transaction_id: str
):
    invoice_directory = os.path.join(
        "media",
        "invoices"
    )

    os.makedirs(
        invoice_directory,
        exist_ok=True
    )

    file_name = f"invoice_{transaction_id}.pdf"

    file_path = os.path.join(
        invoice_directory,
        file_name
    )

    pdf = canvas.Canvas(
        file_path,
        pagesize=A4
    )

    width, height = A4

    # ========================================================
    # INVOICE HEADER
    # ========================================================

    pdf.setFont(
        "Helvetica-Bold",
        20
    )

    pdf.drawString(
        50,
        height - 70,
        "BLOG MANAGEMENT API"
    )

    pdf.setFont(
        "Helvetica-Bold",
        16
    )

    pdf.drawString(
        50,
        height - 110,
        "SUBSCRIPTION INVOICE"
    )

    # ========================================================
    # INVOICE DETAILS
    # ========================================================

    pdf.setFont(
        "Helvetica",
        11
    )

    y = height - 160

    pdf.drawString(
        50,
        y,
        f"User Name: {username}"
    )

    y -= 30

    pdf.drawString(
        50,
        y,
        f"Plan Name: {plan_name}"
    )

    y -= 30

    pdf.drawString(
        50,
        y,
        f"Price: Rs. {price:.2f}"
    )

    y -= 30

    pdf.drawString(
        50,
        y,
        f"Start Date: {start_date.strftime('%Y-%m-%d %H:%M:%S')}"
    )

    y -= 30

    pdf.drawString(
        50,
        y,
        f"End Date: {end_date.strftime('%Y-%m-%d %H:%M:%S')}"
    )

    y -= 30

    pdf.drawString(
        50,
        y,
        f"Transaction ID: {transaction_id}"
    )

    # ========================================================
    # PAYMENT STATUS
    # ========================================================

    y -= 60

    pdf.setFont(
        "Helvetica-Bold",
        12
    )

    pdf.drawString(
        50,
        y,
        "Payment Status: SUCCESS"
    )

    y -= 40

    pdf.setFont(
        "Helvetica",
        10
    )

    pdf.drawString(
        50,
        y,
        "This is a sample invoice generated for the"
    )

    y -= 18

    pdf.drawString(
        50,
        y,
        "Blog Management API subscription."
    )

    # ========================================================
    # FOOTER
    # ========================================================

    pdf.setFont(
        "Helvetica",
        9
    )

    pdf.drawString(
        50,
        50,
        "Thank you for subscribing to Blog Management API."
    )

    pdf.save()

    return file_path


# ============================================================
# GET ALL SUBSCRIPTION PLANS
# ============================================================

@router.get("/plans")
def get_plans(
    db: Session = Depends(get_db)
):
    plans = db.query(SubscriptionPlan).all()

    if not plans:

        basic = SubscriptionPlan(
            name="Basic",
            price=0.0,
            max_posts=1,
            max_images_per_post=1,
            max_likes=5,
            max_comments=5
        )

        premium = SubscriptionPlan(
            name="Premium",
            price=499.0,
            max_posts=2,
            max_images_per_post=2,
            max_likes=20,
            max_comments=20
        )

        pro = SubscriptionPlan(
            name="Pro",
            price=999.0,
            max_posts=None,
            max_images_per_post=None,
            max_likes=None,
            max_comments=None
        )

        db.add_all([
            basic,
            premium,
            pro
        ])

        db.commit()

        plans = db.query(
            SubscriptionPlan
        ).all()

    return plans


# ============================================================
# SUBSCRIBE TO A PLAN
# ============================================================

@router.post("/subscribe/{plan_name}")
def subscribe_to_plan(
    plan_name: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    # ========================================================
    # FIND REQUESTED PLAN
    # ========================================================

    plan = db.query(
        SubscriptionPlan
    ).filter(
        SubscriptionPlan.name.ilike(plan_name)
    ).first()

    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subscription plan not found"
        )

    # ========================================================
    # SET SUBSCRIPTION PERIOD
    # ========================================================

    start_date = datetime.utcnow()

    end_date = start_date + timedelta(
        days=30
    )

    # ========================================================
    # GENERATE TRANSACTION ID
    # ========================================================

    transaction_id = (
        f"TXN-{uuid.uuid4().hex[:12].upper()}"
    )

    # ========================================================
    # UPDATE USER'S ACTIVE SUBSCRIPTION
    # ========================================================

    current_user.subscription_plan_id = plan.id

    # ========================================================
    # CREATE BILLING HISTORY
    # ========================================================

    billing = BillingHistory(
        user_id=current_user.id,
        plan_id=plan.id,
        start_date=start_date,
        end_date=end_date,
        transaction_id=transaction_id
    )

    db.add(billing)

    db.commit()

    db.refresh(billing)

    # ========================================================
    # GENERATE INVOICE PDF
    # ========================================================

    invoice_path = generate_invoice(
        username=current_user.username,
        plan_name=plan.name,
        price=plan.price,
        start_date=start_date,
        end_date=end_date,
        transaction_id=transaction_id
    )

    # ========================================================
    # STORE INVOICE PATH
    # ========================================================

    billing.invoice_path = invoice_path

    db.commit()

    db.refresh(billing)

    # ========================================================
    # CREATE IN-APP SUBSCRIPTION NOTIFICATION
    # ========================================================

    create_notification(
        db=db,
        user_id=current_user.id,
        message=(
            f"Your {plan.name} subscription has been "
            f"activated successfully."
        ),
        notification_type="subscription"
    )

    # ========================================================
    # RESPONSE
    # ========================================================

    return {
        "message": "Subscription activated successfully",
        "username": current_user.username,
        "plan": plan.name,
        "price": plan.price,
        "start_date": start_date,
        "end_date": end_date,
        "transaction_id": transaction_id,
        "invoice_path": invoice_path
    }


# ============================================================
# GET CURRENT USER SUBSCRIPTION
# ============================================================

@router.get("/my-subscription")
def get_my_subscription(
    current_user: User = Depends(get_current_user)
):

    if not current_user.subscription_plan:

        return {
            "username": current_user.username,
            "subscription_plan": None,
            "message": "No active subscription"
        }

    plan = current_user.subscription_plan

    return {
        "username": current_user.username,
        "subscription_plan": plan.name,
        "price": plan.price,
        "max_posts": plan.max_posts,
        "max_images_per_post": plan.max_images_per_post,
        "max_likes": plan.max_likes,
        "max_comments": plan.max_comments
    }