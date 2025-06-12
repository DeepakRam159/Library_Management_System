from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Categories"
    
    def __str__(self):
        return self.name

class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=200)
    isbn = models.CharField(max_length=13, unique=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    total_copies = models.PositiveIntegerField(default=1)
    available_copies = models.PositiveIntegerField(default=1)
    publication_date = models.DateField()
    publisher = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    book_image = models.ImageField(upload_to='book_images/', blank=True, null=True)
    added_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.title} by {self.author}"
    
    @property
    def is_available(self):
        return self.available_copies > 0
    
    @property
    def issued_copies(self):
        return self.total_copies - self.available_copies

class Member(models.Model):
    MEMBER_TYPES = [
        ('student', 'Student'),
        ('faculty', 'Faculty'),
        ('staff', 'Staff'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    member_id = models.CharField(max_length=20, unique=True)
    phone = models.CharField(max_length=15)
    address = models.TextField()
    member_type = models.CharField(max_length=10, choices=MEMBER_TYPES, default='student')
    department = models.CharField(max_length=100)
    enrollment_number = models.CharField(max_length=20, blank=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.user.get_full_name()} ({self.member_id})"
    
    @property
    def full_name(self):
        return self.user.get_full_name()

class BookIssue(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    issue_date = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField()
    return_date = models.DateTimeField(null=True, blank=True)
    fine_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    is_returned = models.BooleanField(default=False)
    issued_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='issued_books')
    returned_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='returned_books', null=True, blank=True)
    
    def save(self, *args, **kwargs):
        if not self.due_date:
            self.due_date = timezone.now() + timedelta(days=14)  # 14 days loan period
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.book.title} - {self.member.user.get_full_name()}"
    
    @property
    def is_overdue(self):
        if not self.is_returned and timezone.now() > self.due_date:
            return True
        return False
    
    @property
    def days_overdue(self):
        if self.is_overdue:
            return (timezone.now() - self.due_date).days
        return 0
    
    def calculate_fine(self):
        if self.is_overdue:
            # Fine: $1 per day overdue
            self.fine_amount = self.days_overdue * 1.00
            return self.fine_amount
        return 0.00

class BookReservation(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    reservation_date = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    notified = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ['book', 'member']
    
    def __str__(self):
        return f"{self.book.title} reserved by {self.member.user.get_full_name()}"

class Visitor(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=15, blank=True)
    purpose = models.CharField(max_length=200)
    visit_date = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.name} - {self.visit_date.strftime('%Y-%m-%d %H:%M')}"

class LibrarySettings(models.Model):
    library_name = models.CharField(max_length=200, default="Library Management System")
    max_books_per_member = models.PositiveIntegerField(default=3)
    loan_period_days = models.PositiveIntegerField(default=14)
    fine_per_day = models.DecimalField(max_digits=5, decimal_places=2, default=1.00)
    library_email = models.EmailField(blank=True)
    library_phone = models.CharField(max_length=15, blank=True)
    library_address = models.TextField(blank=True)
    
    class Meta:
        verbose_name = "Library Settings"
        verbose_name_plural = "Library Settings"
    
    def __str__(self):
        return self.library_name
