from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User  # Use Django's default User model
from .forms import UserRegisterForm, ProductForm, CategoryForm, RefundForm,  VeterinarianRegistrationForm, VeterinarianProfileForm, ProductFilterForm,  ReviewForm, ForumPostForm, ForumReplyForm, ResourceForm, RefundRequestForm
from .models import Product, Category, Order, OrderItem, Refund, AuditLog, Veterinarian, Review, VetAvailability, Appointment, ForumPost, ForumReply, Resource, ResourceCategory
from django.contrib.admin.views.decorators import staff_member_required
import razorpay
from django.conf import settings
from django.utils.timezone import localtime, now, timedelta
from django.db.models import Sum, Count
from .utils import send_email, send_vet_registration_email, send_vet_approval_email, send_login_notification_email, generate_invoice,  send_order_confirmation_email, send_appointment_confirmation_email
from django.views.decorators.http import require_POST
from .cart import Cart
from django.views.decorators.csrf import csrf_exempt
from django.http import FileResponse,  HttpResponse
from django.core.mail import send_mail
from datetime import datetime, timedelta
import csv
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Spacer, Paragraph, Image  # Import Spacer, Paragraph, Image
from reportlab.lib.styles import getSampleStyleSheet  # Import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
import io
import os
from django.contrib.staticfiles import finders
import matplotlib
matplotlib.use('Agg')  # Use non-GUI backend before importing pyplot
import matplotlib.pyplot as plt
from django.db.models import Q
from django.contrib import messages

def register(request):
    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()

            subject = "User Registration Successful"
            message = f"Dear {user.username},\n\nYour registration was successful. Welcome to our platform!"
            send_email(subject, message, user.email)

            login(request, user)
            messages.success(request, "Registration successful!")
            return redirect("login")
        else:
            # Print errors to console for debugging
            print(form.errors)
            messages.error(request, "Registration failed. Please fix the errors below.")
    else:
        form = UserRegisterForm()
        
    return render(request, "users/register.html", {"form": form})




def home(request):
    query = request.GET.get('q', '').strip()  # Get the search query

    if query:
        # Filter products where the name contains the search query OR category name matches
        products = Product.objects.filter(
            Q(name__icontains=query) | 
            Q(category__name__icontains=query)
        ).distinct()
    else:
        products = Product.objects.all()  # Show all products if no search term

    return render(request, "users/home.html", {'products': products, 'query': query})


  

def vet(request):
    return render(request, "users/vet_base.html")

def about_us(request):
    return render(request, "users/about.html")

def contact_us(request):
    return render(request, "users/contact.html")


def user_login(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, "Logged in successfully!")

            # ✅ Log admin login action
            if user.is_staff:
                AuditLog.objects.create(
                    admin=user,
                    action="LOGIN",
                    model_name="Admin",
                    item_id=user.id,
                    description=f"Admin {user.username} logged in."
                )

            return redirect_role_based(user)
    else:
        form = AuthenticationForm()
    
    return render(request, "users/login.html", {"form": form})


def user_logout(request):
    if request.user.is_authenticated and request.user.is_staff:
        # ✅ Log admin logout action
        AuditLog.objects.create(
            admin=request.user,
            action="LOGOUT",
            model_name="Admin",
            item_id=request.user.id,
            description=f"Admin {request.user.username} logged out."
        )

    logout(request)
    messages.success(request, "Logged out successfully!")
    return redirect("home")

@login_required
def profile(request):
    orders = Order.objects.filter(user=request.user).order_by('-order_date')
    return render(request, 'users/profile.html', {'orders': orders})


# Check if user is an admin
def is_admin(user):
    return user.is_authenticated and user.is_staff

@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    return render(request, "users/admin_dashboard.html")

@login_required
def customer_dashboard(request):
    return render(request, "users/home.html")

def redirect_role_based(user):
    if user.is_authenticated:
        if user.is_staff:
            return redirect("admin_dashboard")
        elif user.groups.filter(name="User").exists():
            return redirect("profile")
    return redirect("home")

@login_required
def login_redirect(request):
    return redirect_role_based(request.user)

# Product Management
@login_required
@user_passes_test(is_admin)
def product_list(request):
    products = Product.objects.all()
    return render(request, 'users/product_list.html', {'products': products})

@login_required
@user_passes_test(is_admin)
def product_form(request, pk=None):
    if pk:
        product = get_object_or_404(Product, pk=pk)
        action = "UPDATE"
    else:
        product = None
        action = "CREATE"

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            product = form.save()

            # Log the admin action
            AuditLog.objects.create(
                admin=request.user,
                action=action,
                model_name="Product",
                item_id=product.id,
                description=f"Admin {request.user} {action.lower()}d product '{product.name}'."
            )

            messages.success(request, 'Product saved successfully!')
            return redirect('product_list')
    else:
        form = ProductForm(instance=product)

    return render(request, 'users/product_form.html', {'form': form})

@login_required
@user_passes_test(is_admin)
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product_name = product.name
        product_id = product.id
        product.delete()

        # Log the admin action
        AuditLog.objects.create(
            admin=request.user,
            action="DELETE",
            model_name="Product",
            item_id=product_id,
            description=f"Admin {request.user} deleted product '{product_name}'."
        )

        messages.success(request, 'Product deleted successfully!')
        return redirect('product_list')

    return render(request, 'users/product_confirm_delete.html', {'product': product})

# Category Management
@login_required
@user_passes_test(is_admin)
def manage_categories(request):
    categories = Category.objects.all()

    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save()
            
            # Log the action in AuditLog
            AuditLog.objects.create(
                admin=request.user,
                action="CREATE",
                model_name="Category",
                item_id=category.id,
                description=f"Admin {request.user} added category '{category.name}'."
            )

            messages.success(request, 'Category added successfully!')
            return redirect('manage_categories')
    else:
        form = CategoryForm()

    return render(request, 'users/manage_categories.html', {
        'categories': categories,
        'form': form
    })


@login_required
@user_passes_test(is_admin)
def add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save()
            AuditLog.objects.create(
                admin=request.user,
                action="CREATE",
                model_name="Category",
                item_id=category.id,
                description=f"Admin {request.user} added category '{category.name}'."
            )
            messages.success(request, f"Category '{category.name}' added successfully!")
        else:
            messages.error(request, "Error adding category. Please check the form.")

        return redirect('manage_categories')

@login_required
@user_passes_test(is_admin)
def delete_category(request, category_id):
    if request.method == 'POST':
        category = get_object_or_404(Category, id=category_id)
        category_name = category.name
        category.delete()
        AuditLog.objects.create(
            admin=request.user,
            action="DELETE",
            model_name="Category",
            item_id=category_id,
            description=f"Admin {request.user} deleted category '{category_name}'."
        )
        messages.success(request, f"Category '{category_name}' deleted successfully!")

    return redirect('manage_categories')

@login_required
@user_passes_test(is_admin)
def edit_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)

    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            category = form.save()
            # Log the action
            AuditLog.objects.create(
                admin=request.user,
                action="UPDATE",
                model_name="Category",
                item_id=category.id,
                description=f"Admin {request.user} updated category '{category.name}'."
            )
            messages.success(request, f"Category '{category.name}' updated successfully!")
            return redirect('manage_categories')  # Redirect to clear messages after update
        else:
            messages.error(request, "Error updating category. Please check the form.")
    else:
        form = CategoryForm(instance=category)  # This ensures 'form' is always defined

    return render(request, 'users/edit_category.html', {'form': form, 'category': category})

# Order Management
@staff_member_required
def order_list(request):
    orders = Order.objects.all().order_by('-order_date')
    return render(request, 'users/order_list.html', {'orders': orders})

@staff_member_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'users/order_detail.html', {'order': order})

@staff_member_required
def update_order_status(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        order.status = new_status
        order.save()
        return redirect('order_list')
    return render(request, 'users/update_order_status.html', {'order': order})

def order_confirmation(request, order_id):
    order = Order.objects.get(id=order_id)
    return render(request, 'users/order_confirmation.html', {'order': order})

def download_invoice(request, order_id):
    invoice = generate_invoice(order_id)
    return FileResponse(invoice, as_attachment=True, filename=f"Invoice_{order_id}.pdf")


# Refund Requests
razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

def refund_requests(request):
    refunds = Refund.objects.all()
    return render(request, 'users/refund_requests.html', {'refunds': refunds})

def process_refund(request, refund_id):
    refund = get_object_or_404(Refund, id=refund_id)

    if request.method == "POST":
        form = RefundForm(request.POST, instance=refund)
        if form.is_valid():
            refund_status = form.cleaned_data['status']
            refund.status = refund_status
            refund.save()

            # If refund is approved, process payment via Razorpay
            if refund_status == "approved":
                try:
                    order = refund.order
                    payment_id = order.payment_id  # Ensure your Order model has a 'payment_id'
                    
                    refund_response = razorpay_client.payment.refund(payment_id, {
                        "amount": int(order.total_price * 100),  # Convert to paise
                        "speed": "normal",
                        "notes": {"reason": refund.reason}
                    })

                    messages.success(request, f"Refund approved and processed. Razorpay Refund ID: {refund_response['id']}")
                except Exception as e:
                    messages.error(request, f"Error processing refund: {e}")
            else:
                messages.warning(request, "Refund request has been rejected.")

            return redirect('refund_requests')

    else:
        form = RefundForm(instance=refund)

    return render(request, 'users/process_refund.html', {'form': form, 'refund': refund})

# Audit Logs
@login_required
def audit_logs(request):
    logs = AuditLog.objects.all().order_by('-timestamp')
    for log in logs:
        log.timestamp = localtime(log.timestamp)
    return render(request, 'users/audit_logs.html', {'logs': logs})

@login_required
def sales_report(request):
    current_year = now().year

    # Get values from request
    selected_year = request.GET.get('year')
    selected_month = request.GET.get('month')
    report_type = request.GET.get('download')  # 'csv' or 'pdf'

    # Convert selected_year and selected_month safely
    try:
        selected_year = int(selected_year) if selected_year else current_year
    except ValueError:
        selected_year = current_year  # Default if invalid

    try:
        selected_month = int(selected_month) if selected_month and selected_month.isdigit() else None
    except ValueError:
        selected_month = None  # Ignore invalid month values  

    # Apply filters for paid orders
    filters = {'payment_status': True}
    filters['order_date__year'] = selected_year

    if selected_month:
        filters['order_date__month'] = selected_month

    # Aggregate order data
    total_sales = Order.objects.filter(**filters).aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    completed_orders = Order.objects.filter(status='Delivered', **filters).count()
    paid_orders = Order.objects.filter(**filters)
    refunded_orders = Refund.objects.filter(
        
        order__in=paid_orders,
        status='approved'
    ).count()

    # Define available years and months
    available_years = list(range(2025, current_year + 1))
    available_months = [
        (1, "January"), (2, "February"), (3, "March"), (4, "April"),
        (5, "May"), (6, "June"), (7, "July"), (8, "August"),
        (9, "September"), (10, "October"), (11, "November"), (12, "December")
    ]

    # Prepare context
    context = {
        'total_sales': total_sales,
        'completed_orders': completed_orders,
        'refunded_orders': refunded_orders,
        'selected_month': selected_month,
        'selected_year': selected_year,
        'available_months': available_months,
        'available_years': available_years,
    }

    # Handle report downloads
    if report_type == 'csv':
        return generate_csv_report(total_sales, completed_orders, refunded_orders, selected_year, selected_month)
    elif report_type == 'pdf':
        return generate_pdf_report(total_sales, completed_orders, refunded_orders, selected_year, selected_month)

    return render(request, 'users/sales_report.html', context)


def generate_csv_report(total_sales, completed_orders, refunded_orders, year, month):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="sales_report_{year}_{month or "all"}.csv"'

    writer = csv.writer(response)
    writer.writerow(['Metric', 'Value'])
    writer.writerow(['Total Sales Revenue', total_sales])
    writer.writerow(['Completed Orders', completed_orders])
    writer.writerow(['Refunded Orders', refunded_orders])

    return response

def generate_pdf_report(total_sales, completed_orders, refunded_orders, year, month):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    
    styles = getSampleStyleSheet()
    title_style = styles['Title']
    title_style.fontSize = 18
    title_style.alignment = 1  # Center Alignment

    # ✅ Find the logo dynamically from the static folder
    logo_path = finders.find("images/Paw.jpg")  # Ensure logo is inside `static/images/`
    if logo_path and os.path.exists(logo_path):
        logo = Image(logo_path, width=80, height=80)
        elements.append(logo)

    # ✅ Add Company Name "Petopia"
    company_name = Paragraph("Petopia", title_style)
    elements.append(company_name)
    elements.append(Spacer(1, 10))  # Space below company name

    # ✅ Title with Selected Date
    title_text = f"Sales Report for {month or 'All Months'} {year}"
    elements.append(Paragraph(title_text, title_style))
    elements.append(Spacer(1, 10))

    # ✅ Sales Data Table
    data = [
        ['Metric', 'Value'],
        ['Total Sales Revenue', f'Rs. {total_sales}'],
        ['Completed Orders', completed_orders],
        ['Refunded Orders', refunded_orders]
    ]

    table = Table(data, colWidths=[250, 150])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))

    elements.append(table)
    elements.append(Spacer(1, 20))  # Space before the charts

    # ✅ Generate and add charts
    chart_path = generate_sales_charts(total_sales, completed_orders, refunded_orders)
    if os.path.exists(chart_path):
        elements.append(Image(chart_path, width=400, height=300))

    # ✅ Footer with date & page number
    elements.append(Spacer(1, 20))
    footer_text = f"Report generated on {now().strftime('%d %B %Y')}"
    elements.append(Paragraph(footer_text, styles['Normal']))

    doc.build(elements)
    buffer.seek(0)

    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="sales_report_{year}_{month or "all"}.pdf"'
    return response


def generate_sales_charts(total_sales, completed_orders, refunded_orders):
    matplotlib.use('Agg')  # Ensure we use a non-GUI backend
    fig, ax = plt.subplots(1, 2, figsize=(10, 5))

    categories = ['Total Sales', 'Completed Orders', 'Refunded Orders']
    values = [total_sales, completed_orders, refunded_orders]

    # Bar Chart
    ax[0].bar(categories, values, color=['blue', 'green', 'red'])
    ax[0].set_title('Sales Overview')

    # Pie Chart
    ax[1].pie(values, labels=categories, autopct='%1.1f%%', colors=['blue', 'green', 'red'])
    ax[1].set_title('Sales Distribution')

    chart_path = "sales_chart.png"
    plt.savefig(chart_path)
    plt.close(fig)  # ✅ Ensure plot is closed properly

    return chart_path


@login_required
def download_sales_report_pdf(request):
    """Generate and download sales report as a PDF file."""
    today = now().date()
    week_start = today - timedelta(days=today.weekday())  
    month_start = today.replace(day=1)  
    year_start = today.replace(month=1, day=1)  

    def get_sales_data(start_date):
        return Order.objects.filter(status="Completed", order_date__gte=start_date).aggregate(Sum("total_amount"))["total_amount__sum"] or 0

    def get_order_count(start_date, status):
        return Order.objects.filter(status=status, order_date__gte=start_date).count()

    # Sales Data
    week_sales = get_sales_data(week_start)
    month_sales = get_sales_data(month_start)
    year_sales = get_sales_data(year_start)

    # Order Counts
    week_orders = get_order_count(week_start, "Completed")
    month_orders = get_order_count(month_start, "Completed")
    year_orders = get_order_count(year_start, "Completed")

    week_refunds = get_order_count(week_start, "Refunded")
    month_refunds = get_order_count(month_start, "Refunded")
    year_refunds = get_order_count(year_start, "Refunded")

    # Create PDF
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    p.setTitle("Sales Report")
    
    p.setFont("Helvetica-Bold", 14)
    p.drawString(200, 800, "Sales Report")
    
    p.setFont("Helvetica", 12)
    p.drawString(50, 770, f"Date: {now().strftime('%d-%m-%Y')}")
    p.drawString(50, 750, "--------------------------------------------")

    p.drawString(50, 730, f"Weekly Sales Revenue: ₹{week_sales}")
    p.drawString(50, 710, f"Monthly Sales Revenue: ₹{month_sales}")
    p.drawString(50, 690, f"Yearly Sales Revenue: ₹{year_sales}")

    p.drawString(50, 670, f"Completed Orders This Week: {week_orders}")
    p.drawString(50, 650, f"Completed Orders This Month: {month_orders}")
    p.drawString(50, 630, f"Completed Orders This Year: {year_orders}")

    p.drawString(50, 610, f"Refunded Orders This Week: {week_refunds}")
    p.drawString(50, 590, f"Refunded Orders This Month: {month_refunds}")
    p.drawString(50, 570, f"Refunded Orders This Year: {year_refunds}")

    p.showPage()
    p.save()
    
    buffer.seek(0)
    response = HttpResponse(buffer, content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="sales_report.pdf"'
    return response


@login_required
def download_sales_report_csv(request):
    """Generate and download sales report as a CSV file."""
    today = now().date()
    week_start = today - timedelta(days=today.weekday())  
    month_start = today.replace(day=1)  
    year_start = today.replace(month=1, day=1)  

    def get_sales_data(start_date):
        return Order.objects.filter(status="Completed", order_date__gte=start_date).aggregate(Sum("total_amount"))["total_amount__sum"] or 0

    def get_order_count(start_date, status):
        return Order.objects.filter(status=status, order_date__gte=start_date).count()

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="sales_report.csv"'
    
    writer = csv.writer(response)
    writer.writerow(["Metric", "Weekly", "Monthly", "Yearly"])
    writer.writerow(["Sales Revenue (₹)", get_sales_data(week_start), get_sales_data(month_start), get_sales_data(year_start)])
    writer.writerow(["Completed Orders", get_order_count(week_start, "Completed"), get_order_count(month_start, "Completed"), get_order_count(year_start, "Completed")])
    writer.writerow(["Refunded Orders", get_order_count(week_start, "Refunded"), get_order_count(month_start, "Refunded"), get_order_count(year_start, "Refunded")])

    return response


# Ensure only admins can access
def admin_required(user):
    return user.is_superuser

# Helper function to check if user is an admin
def admin_required(user):
    return user.is_staff

@user_passes_test(admin_required)
def pending_veterinarians(request):
    pending_vets = Veterinarian.objects.filter(is_verified=False)  # Use is_verified instead of verified
    return render(request, 'users/vet_verification.html', {'pending_vets': pending_vets})

@user_passes_test(admin_required)
def verify_veterinarian(request, vet_id):
    vet = get_object_or_404(Veterinarian, id=vet_id)
    vet.is_verified = True  # Ensure correct field name
    vet.save()

    # Log the action
    AuditLog.objects.create(
        admin=request.user,
        action="APPROVE",
        model_name="Veterinarian",
        item_id=vet.id,
        description=f"Admin {request.user} approved veterinarian {vet.user.username}."
    )

    # Send approval email
    send_vet_approval_email(vet.user.email)

    messages.success(request, f"✅ Veterinarian {vet.user.username} has been approved!")
    return redirect("pending_veterinarians")


@user_passes_test(admin_required)
def reject_veterinarian(request, vet_id):
    vet = get_object_or_404(Veterinarian, id=vet_id)
    
    # Log the rejection
    AuditLog.objects.create(
        admin=request.user,
        action="REJECT",
        model_name="Veterinarian",
        item_id=vet.id,
        description=f"Admin {request.user} rejected veterinarian {vet.user.username}."
    )

    vet.delete()  # Remove rejected vet profile

    messages.warning(request, f"❌ Veterinarian {vet.user.username} has been rejected and removed!")
    return redirect('pending_veterinarians')

def veterinarian_register(request):
    if request.method == "POST":
        form = VeterinarianRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            vet = form.save(commit=False)
            vet.is_verified = False  # Pending admin approval
            vet.save()

            # Send email notification
            send_vet_registration_email(vet.user.email)

            messages.success(request, "Registration successful! You will be notified once approved.")
            return redirect("veterinarian_register")

    else:
        form = VeterinarianRegistrationForm()

    return render(request, "users/veterinarian_register.html", {"form": form})

def veterinarian_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            # Check if user is a verified veterinarian
            if hasattr(user, 'veterinarian') and user.veterinarian.is_verified:
                login(request, user)

                # Send login notification email
                send_login_notification_email(user.email)

                messages.success(request, "✅ Welcome, Veterinarian!")
                return redirect('vet_dashboard')  # Redirect to Veterinarian Dashboard
            else:
                messages.error(request, "❌ Your account is not verified as a veterinarian.")
        else:
            messages.error(request, "❌ Invalid username or password.")

    return render(request, 'users/vet_login.html')



def is_veterinarian(user):
    return hasattr(user, 'veterinarian') and user.veterinarian.is_verified

@login_required
@user_passes_test(is_veterinarian)
def update_vet_profile(request):
    veterinarian = request.user.veterinarian

    if request.method == 'POST':
        form = VeterinarianProfileForm(request.POST, request.FILES, instance=veterinarian)
        if form.is_valid():
            form.save()
            messages.success(request, '✅ Profile updated successfully!')
            return redirect('vet_dashboard')
    else:
        form = VeterinarianProfileForm(instance=veterinarian)

    return render(request, 'users/update_vet_profile.html', {'form': form})


@login_required
def vet_dashboard(request):
    return render(request, 'users/vet_dashboard.html')

def shop(request):
    products = Product.objects.all()
    form = ProductFilterForm(request.GET)

    if form.is_valid():
        if form.cleaned_data['search']:
            products = products.filter(name__icontains=form.cleaned_data['search'])
        if form.cleaned_data['category']:
            products = products.filter(category=form.cleaned_data['category'])
        if form.cleaned_data['min_price']:
            products = products.filter(price__gte=form.cleaned_data['min_price'])
        if form.cleaned_data['max_price']:
            products = products.filter(price__lte=form.cleaned_data['max_price'])

    return render(request, 'users/shop.html', {'products': products, 'form': form})

def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    reviews = Review.objects.filter(product=product)  # Show only approved reviews
    # Get recommended products from the same category
    recommended_products = Product.objects.filter(category=product.category).exclude(id=product.id)[:4]

    if request.method == "POST":
        if not request.user.is_authenticated:
            messages.error(request, "You must be logged in to submit a review.")
            return redirect('login')

        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.product = product
            review.user = request.user
            review.is_approved = False  # Set review as pending for moderation
            review.save()
            messages.success(request, "Review submitted successfully! It will be visible once approved.")
            return redirect('product_detail', product_id=product.id)
    else:
        form = ReviewForm()

    return render(request, 'users/product_detail.html', {
        'product': product,
        'reviews': reviews,
        'form': form,
        'recommended_products': recommended_products
    })

@login_required
def submit_review(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.product = product
            review.user = request.user
            review.is_approved = True  # No approval needed, publish immediately
            review.save()
            messages.success(request, "Your review has been submitted successfully!")
            return redirect('product_detail', product_id=product.id)
    else:
        form = ReviewForm()

    return render(request, 'reviews/submit_review.html', {'form': form, 'product': product})

@login_required
@user_passes_test(is_admin)
def admin_reviews(request):
    reviews = Review.objects.all()  # Fetch all reviews since they are auto-approved
    return render(request, 'users/review_moderation.html', {'reviews': reviews})

# Check if user is admin
def is_admin(user):
    return user.is_superuser

@login_required
@user_passes_test(is_admin)
def delete_review(request, review_id):
    review = get_object_or_404(Review, id=review_id)

    if request.method == 'POST':
        review.delete()
        messages.success(request, "Review deleted successfully!")
        return redirect('admin_reviews')  # Redirect to review list

    return redirect('admin_reviews')  # Ensure correct redirect



@require_POST
def add_to_cart(request, product_id):
    if not request.user.is_authenticated:
        messages.info(request, "Please log in to add products to your cart.")
        return redirect('login')  # Redirect to login page
    
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    quantity = int(request.POST.get('quantity', 1))
    cart.add(product=product, quantity=quantity)
    return redirect('cart_detail')

@require_POST
def update_cart(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    quantity = int(request.POST.get('quantity', 1))
    if quantity < 1:  # Prevent quantity from going below 1
        quantity = 1
    cart.add(product=product, quantity=quantity, update_quantity=True)
    return redirect('cart_detail')

@require_POST
def remove_from_cart(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    return redirect('cart_detail')

def cart_detail(request):
    cart = Cart(request)
    return render(request, 'users/cart.html', {'cart': cart})

@require_POST
def buy_now(request, product_id):
    if not request.user.is_authenticated:
        messages.info(request, "Please log in to proceed with the purchase.")
        return redirect('login')  # Redirect to login page

    product = get_object_or_404(Product, id=product_id)
    cart = Cart(request)
    cart.clear()  # Clear cart before buying directly
    cart.add(product=product, quantity=1)

    # Ensure price is saved correctly after adding the product
    request.session[settings.CART_SESSION_ID] = cart.cart
    request.session.modified = True

    return redirect('checkout') 

# Redirect to checkout page
@login_required
def checkout(request):
    cart = Cart(request)
    
    if request.method == "POST":
        address = request.POST.get("address")
        if not address:
            return render(request, "users/checkout.html", {"cart": cart, "error": "Address is required"})

        # Create the order
        order = Order.objects.create(
            user=request.user,
            address=address,
            total_amount=cart.get_total_price(),
            payment_status=False  # Payment pending
        )

        # Add items to the order
        for item in cart:
            product = get_object_or_404(Product, id=item.get('product_id'))  # Ensure retrieval
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=item['quantity'],
                price=item['price']
            )

        # Initialize Razorpay
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        payment_data = {
            "amount": int(order.total_amount * 100),  # Convert Decimal to int (paise)
            "currency": "INR",
            "receipt": f"order_{order.id}",
            "payment_capture": "1",
        }
        payment = client.order.create(data=payment_data)
        order_id = payment["id"]

        # Store order ID in session for later reference
        request.session["order_id"] = order.id
        request.session["razorpay_order_id"] = order_id

        return render(request, "users/payment.html", {"order": order, "order_id": order_id, "razorpay_key": settings.RAZORPAY_KEY_ID})

    return render(request, "users/checkout.html", {"cart": cart})



@login_required
def payment_success(request):
    """Handles payment success, updates order status, and sends confirmation email."""
    order_id = request.session.get("order_id")
    if not order_id:
        return redirect("checkout")

    try:
        order = Order.objects.get(id=order_id)
        order.payment_status = True  # Mark as paid
        order.save()

        # Send Order Confirmation Email
        send_order_confirmation_email(order)

        # Clear the cart
        cart = Cart(request)
        cart.clear()

        return redirect("order_confirmation", order_id=order.id)
    
    except Order.DoesNotExist:
        return redirect("checkout")



@csrf_exempt
def order_success(request):
    if request.method == "POST":
        order_id = request.POST.get("order_id")
        razorpay_payment_id = request.POST.get("razorpay_payment_id")

        order = get_object_or_404(Order, id=order_id)
        order.payment_status = True  # Mark as paid
        order.status = "Pending"
        order.save()

        # Clear cart
        cart = Cart(request)
        cart.clear()
        
        return render(request, "users/order_success.html", {"order": order, "payment_id": razorpay_payment_id})
        
    return redirect("cart_detail")

# Helper function to check if the user is a vet
def is_veterinarian(user):
    return hasattr(user, 'veterinarian')

# View to select a veterinarian
@login_required
def select_veterinarian(request):
    veterinarians = Veterinarian.objects.filter(is_verified=True)
    return render(request, 'users/select_veterinarian.html', {'veterinarians': veterinarians})

# View to select a date
@login_required
def select_date(request, vet_id):
    veterinarian = get_object_or_404(Veterinarian, id=vet_id)
    return render(request, 'users/select_date.html', {'veterinarian': veterinarian})

# View to fetch available slots dynamically
@login_required
def get_available_slots(request, vet_id, selected_date):
    veterinarian = get_object_or_404(Veterinarian, id=vet_id)
    availability = VetAvailability.objects.filter(veterinarian=veterinarian).first()

    if not availability:
        messages.error(request, "No availability found for this veterinarian.")
        return redirect("select_date", vet_id=vet_id)

    available_days = availability.available_days.split(", ")

    selected_day = datetime.strptime(selected_date, "%Y-%m-%d").strftime("%A")
    if selected_day not in available_days:
        messages.error(request, "No available slots for this selected date.")
        return redirect("select_date", vet_id=vet_id)

    start_time = availability.start_time
    end_time = availability.end_time
    slot_duration = timedelta(minutes=30)

    slots = []
    current_time = start_time
    while current_time < end_time:
        if not Appointment.objects.filter(veterinarian=veterinarian, date=selected_date, time_slot=current_time).exists():
            slots.append(current_time.strftime("%H:%M"))
        current_time = (datetime.combine(datetime.today(), current_time) + slot_duration).time()

    return render(request, "users/select_slots.html", {
        "veterinarian": veterinarian,
        "selected_date": selected_date,
        "slots": slots,
    })


# View to confirm and proceed with booking
@login_required
def confirm_booking(request, vet_id, selected_date):
    veterinarian = get_object_or_404(Veterinarian, id=vet_id)
    user = request.user

    if request.method == "POST":
        selected_slot = request.POST.get("selected_slot")

        if not selected_slot:
            messages.error(request, "Please select a time slot.")
            return redirect("select_date", vet_id=vet_id)

        if Appointment.objects.filter(veterinarian=veterinarian, date=selected_date, time_slot=selected_slot).exists():
            messages.error(request, "This time slot is already booked.")
            return redirect("select_date", vet_id=vet_id)

        # Create a pending appointment
        appointment = Appointment.objects.create(
            user=user,
            veterinarian=veterinarian,
            date=selected_date,
            time_slot=selected_slot,
            is_paid=False
        )

        # Initialize Razorpay
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        payment_data = {
            "amount": 10000,  # Rs. 100 in paise
            "currency": "INR",
            "receipt": f"appointment_{appointment.id}",
            "payment_capture": "1",
        }
        payment = client.order.create(data=payment_data)
        order_id = payment["id"]

        # Store order ID in session
        request.session["appointment_id"] = appointment.id
        request.session["razorpay_order_id"] = order_id

        return render(request, "users/vet_payment.html", {
            "appointment": appointment,
            "order_id": order_id,
            "razorpay_key": settings.RAZORPAY_KEY_ID
        })

    return redirect("select_date", vet_id=vet_id)

# Appointment success page
def appointment_success(request):
    return render(request, 'users/success.html')

@login_required
def payment_success_appointment(request):
    """Handles successful appointment payment, updates status, and sends confirmation email."""
    appointment_id = request.session.get("appointment_id")
    if not appointment_id:
        return redirect("select_veterinarian")

    try:
        appointment = Appointment.objects.get(id=appointment_id)
        appointment.is_paid = True  # Mark as paid
        appointment.save()

        # Send confirmation email
        send_mail(
            subject="Appointment Confirmation",
            message=f"Your appointment with {appointment.veterinarian.user.username} is confirmed on {appointment.date} at {appointment.time_slot}.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[appointment.user.email],
        )

        messages.success(request, "Appointment successfully booked!")
        return redirect("appointment_success")
    
    except Appointment.DoesNotExist:
        return redirect("select_veterinarian")

def manage_availability(request):
    """Allows veterinarians to manage their availability."""
    veterinarian = request.user.veterinarian

    all_days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

    if request.method == "POST":
        print("POST Data:", request.POST)
        available_days = request.POST.getlist("available_days")  # Get multiple selected days
        start_time = request.POST.get("start_time")
        end_time = request.POST.get("end_time")

        if not available_days or not start_time or not end_time:
            messages.error(request, "All fields are required!")
            return redirect("manage_availability")

        available_days_str = ", ".join(available_days)  # Convert list to comma-separated string

        # Safely create or get the availability object with default values
        availability, created = VetAvailability.objects.get_or_create(
            veterinarian=veterinarian,
            defaults={
                'available_days': available_days_str,
                'start_time': start_time,
                'end_time': end_time
            }
        )

        # If the object already exists, update the values
        if not created:
            availability.available_days = available_days_str
            availability.start_time = start_time
            availability.end_time = end_time
            availability.save()

        messages.success(request, "Availability updated successfully!")
        return redirect("vet_dashboard")

    # Fetch availability, ensuring it is not None
    availability = VetAvailability.objects.filter(veterinarian=veterinarian).first()

    # Ensure selected_days is an empty list if availability does not exist
    selected_days = availability.available_days.split(", ") if availability and availability.available_days else []

    return render(request, "users/manage_availability.html", {
        "availability": availability,
        "selected_days": selected_days,
        "all_days": all_days,
    })

@login_required
def cancel_appointment(request, appointment_id):
    """Allows veterinarians to cancel an appointment and notify the user."""
    veterinarian = request.user.veterinarian
    appointment = get_object_or_404(Appointment, id=appointment_id, veterinarian=veterinarian)

    if request.method == "POST":
        # Notify the user via email
        send_mail(
            subject="Appointment Canceled",
            message=f"Your appointment with Dr. {veterinarian.user.get_full_name()} on {appointment.date} at {appointment.time_slot} has been canceled.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[appointment.user.email],
        )

        # Delete the appointment
        appointment.delete()
        messages.success(request, "Appointment canceled successfully.")
        return redirect("vet_dashboard")

    return render(request, "users/cancel_appointment.html", {"appointment": appointment})


# View all posts
def forum_list(request):
    posts = ForumPost.objects.all().order_by("-created_at")
    return render(request, "users/forum_list.html", {"posts": posts})

# View single post & replies
def forum_detail(request, post_id):
    post = get_object_or_404(ForumPost, id=post_id)
    replies = post.replies.all()
    reply_form = ForumReplyForm()

    if request.method == "POST":
        reply_form = ForumReplyForm(request.POST)
        if reply_form.is_valid():
            reply = reply_form.save(commit=False)
            reply.user = request.user
            reply.post = post
            reply.save()
            messages.success(request, "Your reply has been posted!")
            return redirect("forum_detail", post_id=post.id)

    return render(request, "users/forum_detail.html", {
        "post": post,
        "replies": replies,
        "reply_form": reply_form
    })

# Create a new post
@login_required
def new_post(request):
    if request.method == "POST":
        form = ForumPostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.save()
            messages.success(request, "Your post has been added!")
            return redirect("forum_list")
    else:
        form = ForumPostForm()
    return render(request, "users/new_post.html", {"form": form})

# View all resources
def resource_list(request):
    categories = ResourceCategory.objects.all()
    selected_category = request.GET.get('category')
    
    if selected_category:
        resources = Resource.objects.filter(category__name=selected_category).order_by("-created_at")
    else:
        resources = Resource.objects.all().order_by("-created_at")

    return render(request, "users/resource_list.html", {
        "resources": resources,
        "categories": categories
    })

# View a single resource
def resource_detail(request, resource_id):
    resource = get_object_or_404(Resource, id=resource_id)
    return render(request, "users/resource_detail.html", {"resource": resource})

# Admin-only: Add a new resource
@login_required
@user_passes_test(lambda u: u.is_staff)
def add_resource(request):
    if request.method == "POST":
        form = ResourceForm(request.POST, request.FILES)
        if form.is_valid():
            resource = form.save(commit=False)
            resource.added_by = request.user
            resource.save()
            messages.success(request, "Resource added successfully!")
            return redirect("resource_list")
    else:
        form = ResourceForm()
    return render(request, "users/add_resource.html", {"form": form})

@login_required
def request_refund(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)

    if Refund.objects.filter(order=order).exists():
        messages.info(request, "Refund already requested.")
        return redirect("profile")

    if request.method == "POST":
        form = RefundRequestForm(request.POST)
        if form.is_valid():
            refund = form.save(commit=False)
            refund.order = order
            refund.status = "pending"
            refund.save()
            messages.success(request, "Refund request submitted successfully.")
            return redirect("profile")
    else:
        form = RefundRequestForm()

    return render(request, "users/request_refund.html", {"form": form, "order": order})
