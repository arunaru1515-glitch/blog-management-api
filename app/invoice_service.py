from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
import os


def generate_invoice(
    username,
    email,
    plan_name,
    price,
    start_date,
    end_date,
    transaction_id
):
    # Create invoice folder
    invoice_dir = os.path.join("media", "invoices")
    os.makedirs(invoice_dir, exist_ok=True)

    # Invoice file name
    filename = f"invoice_{transaction_id}.pdf"
    filepath = os.path.join(invoice_dir, filename)

    # Create PDF
    pdf = canvas.Canvas(filepath, pagesize=A4)

    width, height = A4

    # Title
    pdf.setFont("Helvetica-Bold", 20)
    pdf.drawString(30 * mm, height - 30 * mm, "BLOG MANAGEMENT API")

    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(30 * mm, height - 45 * mm, "SUBSCRIPTION INVOICE")

    # Line
    pdf.line(
        30 * mm,
        height - 50 * mm,
        width - 30 * mm,
        height - 50 * mm
    )

    # User details
    y = height - 70 * mm

    pdf.setFont("Helvetica-Bold", 11)
    pdf.drawString(30 * mm, y, "Customer Details")

    y -= 8 * mm

    pdf.setFont("Helvetica", 10)
    pdf.drawString(30 * mm, y, f"Username: {username}")

    y -= 6 * mm
    pdf.drawString(30 * mm, y, f"Email: {email}")

    # Subscription details
    y -= 15 * mm

    pdf.setFont("Helvetica-Bold", 11)
    pdf.drawString(30 * mm, y, "Subscription Details")

    y -= 8 * mm

    pdf.setFont("Helvetica", 10)
    pdf.drawString(30 * mm, y, f"Plan: {plan_name}")

    y -= 6 * mm
    pdf.drawString(30 * mm, y, f"Price: Rs. {price}")

    y -= 6 * mm
    pdf.drawString(30 * mm, y, f"Start Date: {start_date}")

    y -= 6 * mm
    pdf.drawString(30 * mm, y, f"End Date: {end_date}")

    y -= 6 * mm
    pdf.drawString(30 * mm, y, f"Transaction ID: {transaction_id}")

    # Footer
    y -= 20 * mm

    pdf.line(
        30 * mm,
        y,
        width - 30 * mm,
        y
    )

    y -= 10 * mm

    pdf.setFont("Helvetica", 9)
    pdf.drawString(
        30 * mm,
        y,
        "Thank you for subscribing to Blog Management API."
    )

    # Save PDF
    pdf.save()

    return filepath