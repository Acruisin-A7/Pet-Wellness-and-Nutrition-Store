from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.utils.timezone import now
# Category Model
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

# Create a default category
def get_default_category_id():
    return Category.objects.get_or_create(name='Default Category')[0].id

# Product Model

class Product(models.Model):
    name = models.CharField(max_length=200)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products', default=get_default_category_id)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField()
    image = models.ImageField(upload_to='product_images/', default='default.jpg')

    def average_rating(self):
        reviews = self.reviews.all()
        if reviews.exists():
            return round(sum(review.rating for review in reviews) / reviews.count(), 1)
        return 0

    def __str__(self):
        return self.name

class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=False) 
    
    def __str__(self):
        return f"Review by {self.user.username} for {self.product.name}"


# Order Model
class Order(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Shipped', 'Shipped'),
        ('Delivered', 'Delivered'),
        ('Canceled', 'Canceled'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    address = models.TextField( blank=True, null=True)
    order_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_status = models.BooleanField(default=False)

    def __str__(self):
        return f"Order #{self.id} - {self.user.username} - {self.status}"

# Order Item Model
class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='order_items', on_delete=models.CASCADE)  # Ensure related_name
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

# Refund Model
class Refund(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name="refund")
    reason = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')

    def __str__(self):
        return f"Refund for Order {self.order.id} - {self.status}"

# Audit Log Model
class AuditLog(models.Model):
    ACTION_CHOICES = [
        ('CREATE', 'Created'),
        ('UPDATE', 'Updated'),
        ('DELETE', 'Deleted'),
    ]

    admin = models.ForeignKey(User, on_delete=models.CASCADE)
    action = models.CharField(max_length=10, choices=ACTION_CHOICES)
    model_name = models.CharField(max_length=50)
    item_id = models.IntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.admin} {self.get_action_display()} {self.model_name} (ID: {self.item_id}) on {self.timestamp}"

# Veterinarian Model
class Veterinarian(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15)
    license_number = models.CharField(max_length=50, unique=True)
    specialization = models.CharField(max_length=255)
    clinic_address = models.TextField()
    experience = models.IntegerField()
    certification = models.FileField(upload_to='vet_certifications/')
    is_verified = models.BooleanField(default=False)  # Admin approval
    additional_documents = models.FileField(upload_to='vet_documents/', blank=True, null=True) 
    profile_photo = models.ImageField(upload_to='vet_photos/', blank=True, null=True)

    def __str__(self):
        return self.user.username

# Model for Veterinarian's Availability
class VetAvailability(models.Model):
    DAYS_OF_WEEK = [
        ('Monday', 'Monday'),
        ('Tuesday', 'Tuesday'),
        ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'),
        ('Friday', 'Friday'),
        ('Saturday', 'Saturday'),
        ('Sunday', 'Sunday'),
    ]
    
    veterinarian = models.OneToOneField(Veterinarian, on_delete=models.CASCADE)
    available_days = models.CharField(max_length=255,   blank=True, null=True,help_text="Comma-separated days (e.g., Monday, Tuesday)")
    start_time = models.TimeField(help_text="Start time of availability (e.g., 07:00 AM)")
    end_time = models.TimeField(help_text="End time of availability (e.g., 04:00 PM)")

    def __str__(self):
        return f"{self.veterinarian.user.username} - Available: {self.available_days}"

# Model for Appointment Bookings
class Appointment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    veterinarian = models.ForeignKey(Veterinarian, on_delete=models.CASCADE)
    date = models.DateField()
    time_slot = models.TimeField(  blank=True, null=True)
    is_paid = models.BooleanField(default=False)

    class Meta:
        unique_together = ('veterinarian', 'date', 'time_slot')  # Ensures each slot is booked only once

    def __str__(self):
        return f"Appointment with {self.veterinarian.user.username} on {self.date} at {self.time_slot}"

class ForumPost(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    content = models.TextField()
    created_at = models.DateTimeField(default=now)

    def __str__(self):
        return self.title

class ForumReply(models.Model):
    post = models.ForeignKey(ForumPost, on_delete=models.CASCADE, related_name="replies")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(default=now)

    def __str__(self):
        return f"Reply by {self.user.username} on {self.post.title}"

class ResourceCategory(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name

    @classmethod
    def create_default_categories(cls):
        default_categories = ["Health", "Training", "Nutrition", "General"]
        for category in default_categories:
            cls.objects.get_or_create(name=category)


class Resource(models.Model):
    CATEGORY_CHOICES = [
        ('health', 'Health'),
        ('training', 'Training'),
        ('nutrition', 'Nutrition'),
        ('general', 'General'),
    ]

    title = models.CharField(max_length=255)
    category = models.ForeignKey(ResourceCategory, on_delete=models.CASCADE)
    content = models.TextField()
    video_url = models.URLField(blank=True, null=True)  # Optional video link
    image = models.ImageField(upload_to='resource_images/', blank=True, null=True)
    created_at = models.DateTimeField(default=now)
    added_by = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.title
