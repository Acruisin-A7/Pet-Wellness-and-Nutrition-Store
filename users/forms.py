from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Product, Category, Refund, Veterinarian,  Review, ForumPost, ForumReply, Resource
from django.core.exceptions import ValidationError



class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError("This email is already registered. Please use a different email.")
        return email


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'category', 'description', 'price', 'stock', 'image']

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']

class RefundForm(forms.ModelForm):
    class Meta:
        model = Refund
        fields = ['status']

class VeterinarianRegistrationForm(forms.ModelForm):
    username = forms.CharField(max_length=150)
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)
    
    class Meta:
        model = Veterinarian
        fields = ['phone', 'license_number', 'specialization', 'clinic_address', 'experience', 'certification']

    def save(self, commit=True):
        user = User.objects.create_user(
            username=self.cleaned_data['username'],
            email=self.cleaned_data['email'],
            password=self.cleaned_data['password']
        )
        veterinarian = super().save(commit=False)
        veterinarian.user = user
        if commit:
            veterinarian.save()
        return veterinarian

class VeterinarianProfileForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30, required=True, label="First Name")
    last_name = forms.CharField(max_length=30, required=True, label="Last Name")

    class Meta:
        model = Veterinarian
        fields = ['first_name', 'last_name', 'phone', 'experience', 'clinic_address', 'additional_documents', 'profile_photo']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and hasattr(self.instance, 'user'):
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name

    def save(self, commit=True):
        vet_instance = super().save(commit=False)
        user = vet_instance.user
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
            vet_instance.save()
        return vet_instance

class ProductFilterForm(forms.Form):
    search = forms.CharField(required=False, label="Search Products")
    category = forms.ModelChoiceField(queryset=Category.objects.all(), required=False)
    min_price = forms.DecimalField(required=False, min_value=0, label="Min Price")
    max_price = forms.DecimalField(required=False, min_value=0, label="Max Price")

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.Select(choices=[(i, i) for i in range(1, 6)], attrs={'class': 'form-control'}),
            'comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def save(self, commit=True):
        review = super().save(commit=False)
        review.is_approved = False  # Default to unapproved (for moderation)
        if commit:
            review.save()
        return review

class ForumPostForm(forms.ModelForm):
    class Meta:
        model = ForumPost
        fields = ['title', 'content']

class ForumReplyForm(forms.ModelForm):
    class Meta:
        model = ForumReply
        fields = ['content']

class ResourceForm(forms.ModelForm):
    class Meta:
        model = Resource
        fields = ['title', 'category', 'content', 'video_url', 'image']

class RefundRequestForm(forms.ModelForm):
    class Meta:
        model = Refund
        fields = ['reason']
        widgets = {
            'reason': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'})
        }