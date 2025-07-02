from django.core.mail import send_mail
from django.conf import settings
from .models import Order
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import Table, TableStyle
from django.contrib.staticfiles import finders
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from .models import Order  # Import the Order model
from io import BytesIO  # Import BytesIO
from reportlab.pdfgen import canvas  # Import canvas
from reportlab.lib.pagesizes import letter  # Import letter page size
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image  # Import necessary classes from reportlab.platypus
from reportlab.lib.styles import getSampleStyleSheet  # Import getSampleStyleSheet
from reportlab.lib import colors  # Import colors
from django.contrib.staticfiles import finders  # Import finders
import os 
from datetime import datetime, timedelta  # Import timedelta
import csv
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Spacer, Paragraph, Image  # Import Spacer, Paragraph, Image
from reportlab.lib.styles import getSampleStyleSheet  # Import getSampleStyleSheet
from reportlab.lib import colors
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Paragraph, Spacer
from django.conf import settings
import os

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet

import io
import os
from django.http import HttpResponse
from django.utils.timezone import now
from django.contrib.staticfiles import finders

import matplotlib
matplotlib.use('Agg')  # Use non-GUI backend before importing pyplot
import matplotlib.pyplot as plt
import os
from io import BytesIO
from django.conf import settings
from django.contrib.staticfiles import finders
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import Table, TableStyle, Image, Paragraph, SimpleDocTemplate, Spacer
from users.models import Order
import os
from io import BytesIO
from django.conf import settings
from django.contrib.staticfiles import finders
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import Table, TableStyle, Image, Paragraph, SimpleDocTemplate, Spacer
from users.models import Order

import os
from io import BytesIO
from django.http import FileResponse
from django.contrib.staticfiles import finders
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from users.models import Order

# 🟢 Generate Invoice PDF
def generate_invoice(order_id):
    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        raise ValueError(f"Order with ID {order_id} does not exist.")
    
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    pdf.setTitle(f"Invoice_{order.id}.pdf")
    width, height = letter  # 612 x 792 points

    # 🟢 Set up styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        name='Title',
        fontName='Helvetica-Bold',
        fontSize=26,
        textColor=colors.HexColor('#2c3e50'),
        spaceAfter=10,
        alignment=1  # Center
    )
    normal_style = ParagraphStyle(
        name='Normal',
        fontName='Helvetica',
        fontSize=12,
        textColor=colors.HexColor('#2c3e50'),
        spaceAfter=6
    )
    bold_style = ParagraphStyle(
        name='Bold',
        fontName='Helvetica-Bold',
        fontSize=12,
        textColor=colors.HexColor('#2c3e50'),
        spaceAfter=6
    )
    table_cell_style = ParagraphStyle(
        name='TableCell',
        fontName='Helvetica',
        fontSize=10,
        textColor=colors.HexColor('#2c3e50'),
        leading=12,
        alignment=0  # Left-align for product names
    )

    # 🟢 Background Watermark (Paw Prints) - Retained
    pdf.setFillColor(colors.HexColor('#f1c40f'), alpha=0.05)
    pdf.setFont("Helvetica", 100)
    pdf.rotate(45)
    pdf.drawString(200, -100, "🐾")
    pdf.drawString(400, 100, "🐾")
    pdf.drawString(600, 300, "🐾")
    pdf.rotate(-45)

    # 🟢 New Header: Logo, Company Name, and Invoice Details
    # Logo
    logo_path = os.path.join(settings.STATIC_ROOT, "images/Paw.jpg")
    if os.path.exists(logo_path):
        pdf.drawImage(logo_path, 40, height - 90, width=50, height=50, preserveAspectRatio=True, mask='auto')

    # Company Name and Tagline
    pdf.setFont("Helvetica-Bold", 26)
    pdf.setFillColor(colors.HexColor('#2c3e50'))
    pdf.drawString(100, height - 60, "Petopia")

    pdf.setFont("Helvetica", 10)
    pdf.setFillColor(colors.HexColor('#7f8c8d'))
    pdf.drawString(100, height - 75, "Your Trusted Pet Store")

    # Invoice Details (Right-aligned)
    pdf.setFont("Helvetica-Bold", 12)
    pdf.setFillColor(colors.HexColor('#2c3e50'))
    pdf.drawString(width - 180, height - 60, "INVOICE")
    pdf.setFont("Helvetica", 10)
    pdf.drawString(width - 180, height - 75, f"Date: {order.order_date.strftime('%d-%m-%Y')}")
    pdf.drawString(width - 180, height - 90, f"Invoice #: {order.id}")

    # 🟢 Divider (Paw Print Line)
    pdf.setFillColor(colors.HexColor('#f1c40f'))
    pdf.setFont("Helvetica", 20)
    x = 40
    while x < width - 40:
        pdf.drawString(x, height - 110, "🐾")
        x += 30
    pdf.setFillColor(colors.HexColor('#2c3e50'))

    # 🟢 Customer Information
    y_position = height - 150
    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(40, y_position, "Bill To:")
    y_position -= 20

    pdf.setFont("Helvetica", 12)
    pdf.drawString(40, y_position, f"{order.user.get_full_name()} ({order.user.username})")
    y_position -= 15
    pdf.drawString(40, y_position, f"Address: {order.address}")
    y_position -= 30

    # 🟢 Order Details
    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(40, y_position, "Order Details:")
    y_position -= 20

    # Create Table for Products
    data = [["Product", "Quantity", "Unit Price (Rs.)", "Total (Rs.)"]]
    order_items = order.order_items.all()
    if not order_items:
        data.append([Paragraph("No items found in this order.", table_cell_style), "", "", ""])
    else:
        for item in order_items:
            product_name = Paragraph(item.product.name, table_cell_style)
            data.append([
                product_name,
                str(item.quantity),
                f"Rs. {item.price:.2f}",
                f"Rs. {(item.quantity * item.price):.2f}"
            ])

    table = Table(data, colWidths=[250, 80, 90, 90])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),  # Dark blue header
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f0f4f8')),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor('#2c3e50')),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e8ecef')),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#2c3e50')),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    
    table.wrapOn(pdf, 40, height - 500)
    table_height = table._height
    table.drawOn(pdf, 40, y_position - table_height)
    y_position -= (table_height + 20)

    # 🟢 Total Amount
    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(width - 200, y_position, f"Total Amount: Rs. {order.total_amount:.2f}")

    # 🟢 Footer with Pet Theme - Retained
    pdf.setFillColor(colors.HexColor('#f1c40f'), alpha=0.3)
    pdf.rect(0, 0, width, 80, fill=True, stroke=False)
    
    pdf.setFont("Helvetica", 10)
    pdf.setFillColor(colors.HexColor('#2c3e50'))
    pdf.drawCentredString(width / 2, 50, "Thank you for shopping with Petopia! 🐾")
    pdf.drawCentredString(width / 2, 35, "For inquiries, contact support@petopia.com")

    pdf.showPage()
    pdf.save()
    buffer.seek(0)
    
    return buffer




def send_email(subject, message, recipient_email, from_email='admin@example.com'):
    """Utility function to send emails."""
    try:
        send_mail(
            subject,
            message,
            from_email,
            [recipient_email],
            fail_silently=False
        )
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False
    

def send_vet_registration_email(user_email):
    """Send email after veterinarian registration."""
    subject = "Veterinarian Registration Successful ✅"
    message = (
        f"Dear Veterinarian,\n\n"
        "Your registration has been received and is pending approval. "
        "You will be notified once the admin approves your account.\n\n"
        "Thank you for joining our platform!\n\nBest Regards,\nPetCare Team"
    )
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user_email])

def send_vet_approval_email(user_email):
    """Send email after admin approves the veterinarian."""
    subject = "Your Veterinarian Account Has Been Approved! 🎉"
    message = (
        f"Dear Veterinarian,\n\n"
        "Congratulations! Your account has been approved. You can now log in and manage your profile.\n\n"
        "Login here: http://127.0.0.1:8000/login/\n\n"
        "Best Regards,\nPetCare Team"
    )
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user_email])

def send_login_notification_email(user_email):
    """Send email after successful login."""
    subject = "Login Notification 🚀"
    message = (
        f"Dear Veterinarian,\n\n"
        "We noticed a login to your account. If this was you, ignore this email.\n"
        "If you did not log in, please contact support immediately.\n\n"
        "Best Regards,\nPetCare Team"
    )
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user_email])

def generate_invoice(order_id):
    order = Order.objects.get(id=order_id)
    
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    pdf.setTitle(f"Invoice_{order.id}.pdf")
    width, height = letter  # 612 x 792 points

    # 🟢 Set up styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        name='Title',
        fontName='Helvetica-Bold',
        fontSize=24,
        textColor=colors.HexColor('#2c3e50'),
        spaceAfter=12,
        alignment=1  # Center
    )
    normal_style = ParagraphStyle(
        name='Normal',
        fontName='Helvetica',
        fontSize=12,
        textColor=colors.HexColor('#2c3e50'),
        spaceAfter=6
    )
    bold_style = ParagraphStyle(
        name='Bold',
        fontName='Helvetica-Bold',
        fontSize=12,
        textColor=colors.HexColor('#2c3e50'),
        spaceAfter=6
    )

    # 🟢 Background Watermark (Paw Prints)
    pdf.setFillColor(colors.HexColor('#f1c40f'), alpha=0.1)
    pdf.setFont("Helvetica", 100)
    pdf.rotate(45)
    pdf.drawString(200, -100, "🐾")
    pdf.drawString(400, 100, "🐾")
    pdf.drawString(600, 300, "🐾")
    pdf.rotate(-45)

    # 🟢 Header: Logo and Company Name
    logo_path = os.path.join(settings.STATIC_ROOT, "images/Paw.jpg")
    if os.path.exists(logo_path):
        pdf.drawImage(logo_path, 40, height - 100, width=60, height=60, preserveAspectRatio=True, mask='auto')
    
    pdf.setFont("Helvetica-Bold", 24)
    pdf.setFillColor(colors.HexColor('#2c3e50'))
    pdf.drawCentredString(width / 2, height - 60, "Petopia Invoice")

    # 🟢 Invoice Details (Date and Invoice #)
    pdf.setFont("Helvetica", 12)
    pdf.setFillColor(colors.HexColor('#2c3e50'))
    pdf.drawString(width - 180, height - 40, f"Date: {order.order_date.strftime('%d-%m-%Y')}")
    pdf.drawString(width - 180, height - 55, f"Invoice #: {order.id}")

    # 🟢 Customer Information
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(40, height - 130, "Billing To:")
    pdf.setFont("Helvetica", 12)
    pdf.drawString(40, height - 145, f"{order.user.get_full_name()} ({order.user.username})")
    pdf.drawString(40, height - 160, f"Address: {order.address}")

    # 🟢 Order Summary
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(40, height - 190, "Order Details:")

    # 🟢 Create Table for Products
    data = [["Product", "Quantity", "Unit Price (₹)", "Total (₹)"]]
    for item in order.order_items.all():
        data.append([
            item.product.name,
            str(item.quantity),
            f"₹{item.price:.2f}",
            f"₹{(item.quantity * item.price):.2f}"
        ])

    # If no items, add a placeholder row
    if len(data) == 1:
        data.append(["No items found", "", "", ""])

    table = Table(data, colWidths=[200, 100, 100, 100])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f1c40f')),  # Petopia yellow header
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f0f4f8')),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor('#2c3e50')),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 11),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e8ecef')),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#2c3e50')),
    ]))
    
    table.wrapOn(pdf, 40, height - 500)
    table.drawOn(pdf, 40, height - 250)

    # 🟢 Total Amount
    pdf.setFont("Helvetica-Bold", 14)
    pdf.setFillColor(colors.HexColor('#2c3e50'))
    pdf.drawString(width - 200, height - 280, f"Total Amount: ₹{order.total_amount:.2f}")

    # 🟢 Footer with Pet Theme
    pdf.setFillColor(colors.HexColor('#f1c40f'), alpha=0.3)
    pdf.rect(0, 0, width, 80, fill=True, stroke=False)
    
    pdf.setFont("Helvetica", 10)
    pdf.setFillColor(colors.HexColor('#2c3e50'))
    pdf.drawCentredString(width / 2, 50, "Thank you for shopping with Petopia! 🐾")
    pdf.drawCentredString(width / 2, 35, "For inquiries, contact support@petopia.com")

    pdf.showPage()
    pdf.save()
    buffer.seek(0)
    
    return buffer


def send_order_confirmation_email(order):
    subject = "Order Confirmation - PetPlatform"
    message = f"Dear {order.user.username},\n\nYour order #{order.id} has been successfully placed.\nTotal Amount: ₹{order.total_price}\n\nThank you for shopping with us!"
    
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [order.user.email],
        fail_silently=False,
    )

def send_appointment_confirmation_email(appointment):
    subject = "Appointment Confirmation"
    message_user = f"Dear {appointment.user.username},\n\nYour appointment with {appointment.veterinarian.user.username} has been confirmed for {appointment.appointment_date} at {appointment.appointment_time}."
    message_vet = f"Dear Dr. {appointment.veterinarian.user.username},\n\nA new appointment has been booked for {appointment.appointment_date} at {appointment.appointment_time}."

    send_mail(subject, message_user, settings.DEFAULT_FROM_EMAIL, [appointment.user.email])
    send_mail(subject, message_vet, settings.DEFAULT_FROM_EMAIL, [appointment.veterinarian.user.email])

