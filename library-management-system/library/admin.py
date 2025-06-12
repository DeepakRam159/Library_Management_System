from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import Category, Book, Member, BookIssue, BookReservation, Visitor, LibrarySettings

# Customize User Admin
class MemberInline(admin.StackedInline):
    model = Member
    can_delete = False
    verbose_name_plural = 'Member Info'

class CustomUserAdmin(UserAdmin):
    inlines = (MemberInline,)

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'created_at']
    search_fields = ['name']

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'isbn', 'category', 'total_copies', 'available_copies', 'is_available']
    list_filter = ['category', 'publication_date', 'added_date']
    search_fields = ['title', 'author', 'isbn']
    readonly_fields = ['added_date', 'updated_date']
    actions = ['delete_selected']
    
    def has_delete_permission(self, request, obj=None):
        return True

@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'member_id', 'member_type', 'department', 'is_active', 'date_joined']
    list_filter = ['member_type', 'department', 'is_active']
    search_fields = ['user__first_name', 'user__last_name', 'member_id', 'enrollment_number']

@admin.register(BookIssue)
class BookIssueAdmin(admin.ModelAdmin):
    list_display = ['book', 'member', 'issue_date', 'due_date', 'is_returned', 'is_overdue', 'fine_amount']
    list_filter = ['is_returned', 'issue_date', 'due_date']
    search_fields = ['book__title', 'member__user__first_name', 'member__user__last_name']
    readonly_fields = ['issue_date']

@admin.register(BookReservation)
class BookReservationAdmin(admin.ModelAdmin):
    list_display = ['book', 'member', 'reservation_date', 'is_active', 'notified']
    list_filter = ['is_active', 'notified', 'reservation_date']

@admin.register(Visitor)
class VisitorAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'phone', 'purpose', 'visit_date', 'ip_address']
    list_filter = ['visit_date']
    search_fields = ['name', 'email', 'purpose']
    readonly_fields = ['visit_date', 'ip_address']

@admin.register(LibrarySettings)
class LibrarySettingsAdmin(admin.ModelAdmin):
    list_display = ['library_name', 'max_books_per_member', 'loan_period_days', 'fine_per_day']
    
    def has_add_permission(self, request):
        return not LibrarySettings.objects.exists()
