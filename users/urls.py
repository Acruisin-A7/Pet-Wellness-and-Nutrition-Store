
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('password-reset/', 
         auth_views.PasswordResetView.as_view(template_name='users/password_reset.html'), 
         name='password_reset'),
         
    path('password-reset/done/', 
         auth_views.PasswordResetDoneView.as_view(template_name='users/password_reset_done.html'), 
         name='password_reset_done'),
         
    path('password-reset-confirm/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(template_name='users/password_reset_confirm.html'), 
         name='password_reset_confirm'),
         
    path('password-reset-complete/', 
         auth_views.PasswordResetCompleteView.as_view(template_name='users/password_reset_complete.html'), 
         name='password_reset_complete'),
    path('', views.home, name='home'),
    path('vet', views.vet, name='vet'),
    path('about-us', views.about_us, name='about_us'),
    path('contact-us', views.contact_us, name='contact_us'),
    path("register/", views.register, name="register"),
    path("login/", views.user_login, name="login"),
    path("logout/", views.user_logout, name="logout"),
    path('profile/', views.profile, name='profile'),
    path('order/<int:order_id>/refund/', views.request_refund, name='request_refund'),  # ✅ This is the missing URL
    path('download-invoice/<int:order_id>/', views.download_invoice, name='download_invoice'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('redirect-after-login/', views.login_redirect, name='login_redirect'),
    path('products/', views.product_list, name='product_list'),
    path('products/add/', views.product_form, name='product_add'),
    path('products/edit/<int:pk>/', views.product_form, name='product_edit'),
    path('products/delete/<int:pk>/', views.product_delete, name='product_delete'),
    path('categories/manage/', views.manage_categories, name='manage_categories'),
    path('categories/add/', views.add_category, name='add_category'),
    path('categories/delete/<int:category_id>/', views.delete_category, name='delete_category'),
    path('categories/edit/<int:category_id>/', views.edit_category, name='edit_category'),
    path('orders/', views.order_list, name='order_list'),
    path('orders/<int:order_id>/', views.order_detail, name='order_detail'),
    path('orders/update/<int:order_id>/', views.update_order_status, name='update_order_status'),
    path('order/confirmation/<int:order_id>/', views.order_confirmation, name='order_confirmation'),
    path('order/invoice/<int:order_id>/', views.download_invoice, name='download_invoice'),
    path('refunds/', views.refund_requests, name='refund_requests'),
    path('refunds/process/<int:refund_id>/', views.process_refund, name='process_refund'),  # FIXED
    path('audit-logs/', views.audit_logs, name='audit_logs'),
    path('sales-report/', views.sales_report, name='sales_report'),
    path("sales-report/pdf/", views.download_sales_report_pdf, name="download_sales_report_pdf"),
    path("sales-report/csv/", views.download_sales_report_csv, name="download_sales_report_csv"),
    path('vets/pending/', views.pending_veterinarians, name='pending_veterinarians'),
    path('vets/verify/<int:vet_id>/', views.verify_veterinarian, name='verify_veterinarian'),
    path('vets/reject/<int:vet_id>/', views.reject_veterinarian, name='reject_veterinarian'),
    path('veterinarian/register/', views.veterinarian_register, name='veterinarian_register'),
    path('vet/profile/', views.update_vet_profile, name='update_vet_profile'),
    path('vet/login/', views.veterinarian_login, name='vet_login'),
    path('vet/dashboard/', views.vet_dashboard, name='vet_dashboard'),
    path('logout/', LogoutView.as_view(next_page='vet_login'), name='logout'),
    path('shop/', views.shop, name='shop'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('product/<int:product_id>/review/', views.submit_review, name='submit_review'),
    path('reviews/', views.admin_reviews, name='admin_reviews'),
    path('review/<int:review_id>/delete/', views.delete_review, name='delete_review'),
    path('cart/', views.cart_detail, name='cart_detail'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/update/<int:product_id>/', views.update_cart, name='update_cart'),
    path('buy-now/<int:product_id>/', views.buy_now, name='buy_now'),
    path("checkout/", views.checkout, name="checkout"),
    path("order-success/", views.order_success, name="order_success"),
    path('payment-success/', views.payment_success, name='payment_success'),
    path('select-veterinarian/', views.select_veterinarian, name='select_veterinarian'),
    path('select-date/<int:vet_id>/', views.select_date, name='select_date'),
    path('get-slots/<int:vet_id>/<str:selected_date>/', views.get_available_slots, name='get_available_slots'),
    path("confirm-booking/<int:vet_id>/<str:selected_date>/", views.confirm_booking, name="confirm_booking"),
    path('success/', views.appointment_success, name='appointment_success'),
    path('payment-success-appointment/', views.payment_success_appointment, name='payment_success_appointment'),
    path("vet/availability/",views.manage_availability, name="manage_availability"),
    path("vet/appointment/cancel/<int:appointment_id>/", views.cancel_appointment, name="cancel_appointment"),
    path("forum", views.forum_list, name="forum_list"),
    path("post/<int:post_id>/", views.forum_detail, name="forum_detail"),
    path("new/", views.new_post, name="new_post"),
    path("resource", views.resource_list, name="resource_list"),
    path("resource/<int:resource_id>/", views.resource_detail, name="resource_detail"),
    path("add/", views.add_resource, name="add_resource"),
    
]






    








