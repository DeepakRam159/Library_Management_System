from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q, Count
from django.utils import timezone
from django.core.paginator import Paginator
from datetime import timedelta
import json

from .models import Book, Member, BookIssue, Category, BookReservation, Visitor, LibrarySettings
from .forms import BookForm, MemberForm, BookIssueForm, VisitorForm, UserRegistrationForm, MemberRegistrationForm

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def is_admin_or_librarian(user):
    return user.is_superuser or user.groups.filter(name='Librarian').exists()

def is_admin(user):
    return user.is_superuser

# Home page for all visitors
def home(request):
    """Landing page for the library management system."""
    return render(request, 'library/home.html')

# Authentication Views
def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        if username and password:
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {user.get_full_name() or user.username}!')
                return redirect('dashboard')
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Please enter both username and password.')
    
    return render(request, 'library/login.html')

def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('home')

def register_view(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        member_form = MemberRegistrationForm(request.POST)
        
        if form.is_valid() and member_form.is_valid():
            try:
                user = form.save()
                member = member_form.save(commit=False)
                member.user = user
                member.is_active = True
                member.save()
                
                messages.success(request, 'Registration successful! You can now login with your credentials.')
                return redirect('login')
            except Exception as e:
                messages.error(request, f'Registration failed: {str(e)}')
        else:
            # Display form errors
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
            for field, errors in member_form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = UserRegistrationForm()
        member_form = MemberRegistrationForm()
    
    return render(request, 'library/register.html', {
        'form': form,
        'member_form': member_form
    })

# Dashboard
@login_required
def dashboard(request):
    context = {}
    
    # Get statistics
    total_books = Book.objects.count()
    total_members = Member.objects.filter(is_active=True).count()
    issued_books = BookIssue.objects.filter(is_returned=False).count()
    returned_books = BookIssue.objects.filter(is_returned=True).count()
    overdue_books = BookIssue.objects.filter(
        is_returned=False,
        due_date__lt=timezone.now()
    ).count()
    
    context.update({
        'total_books': total_books,
        'total_members': total_members,
        'issued_books': issued_books,
        'returned_books': returned_books,
        'overdue_books': overdue_books,
    })
    
    # Recent activities
    recent_issues = BookIssue.objects.select_related('book', 'member__user').order_by('-issue_date')[:5]
    recent_returns = BookIssue.objects.filter(is_returned=True).select_related('book', 'member__user').order_by('-return_date')[:5]
    
    context.update({
        'recent_issues': recent_issues,
        'recent_returns': recent_returns,
    })
    
    # Popular books
    popular_books = Book.objects.annotate(
        issue_count=Count('bookissue')
    ).order_by('-issue_count')[:5]
    
    context['popular_books'] = popular_books
    
    return render(request, 'library/dashboard.html', context)

# Book Management
@login_required
def book_list(request):
    books = Book.objects.select_related('category').all()
    categories = Category.objects.all()
    
    # Search and filter
    search_query = request.GET.get('search', '')
    category_filter = request.GET.get('category', '')
    
    if search_query:
        books = books.filter(
            Q(title__icontains=search_query) |
            Q(author__icontains=search_query) |
            Q(isbn__icontains=search_query)
        )
    
    if category_filter:
        books = books.filter(category_id=category_filter)
    
    # Pagination
    paginator = Paginator(books, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'categories': categories,
        'search_query': search_query,
        'category_filter': category_filter,
    }
    
    return render(request, 'library/book_list.html', context)

@login_required
@user_passes_test(is_admin_or_librarian)
def book_add(request):
    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Book added successfully!')
            return redirect('book_list')
    else:
        form = BookForm()
    
    return render(request, 'library/book_form.html', {'form': form, 'title': 'Add Book'})

@login_required
@user_passes_test(is_admin_or_librarian)
def book_edit(request, pk):
    book = get_object_or_404(Book, pk=pk)
    
    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES, instance=book)
        if form.is_valid():
            form.save()
            messages.success(request, 'Book updated successfully!')
            return redirect('book_list')
    else:
        form = BookForm(instance=book)
    
    return render(request, 'library/book_form.html', {'form': form, 'title': 'Edit Book'})

@login_required
@user_passes_test(is_admin_or_librarian)
def book_delete(request, pk):
    book = get_object_or_404(Book, pk=pk)
    
    if request.method == 'POST':
        book.delete()
        messages.success(request, 'Book deleted successfully!')
        return redirect('book_list')
    
    return render(request, 'library/book_confirm_delete.html', {'book': book})

# Member Management
@login_required
@user_passes_test(is_admin_or_librarian)
def member_list(request):
    members = Member.objects.select_related('user').all()
    
    # Search
    search_query = request.GET.get('search', '')
    if search_query:
        members = members.filter(
            Q(user__first_name__icontains=search_query) |
            Q(user__last_name__icontains=search_query) |
            Q(member_id__icontains=search_query) |
            Q(enrollment_number__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(members, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'library/member_list.html', {
        'page_obj': page_obj,
        'search_query': search_query,
    })

@login_required
@user_passes_test(is_admin_or_librarian)
def member_add(request):
    if request.method == 'POST':
        form = MemberForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Member added successfully!')
            return redirect('member_list')
    else:
        form = MemberForm()
    
    return render(request, 'library/member_form.html', {'form': form, 'title': 'Add Member'})

@login_required
@user_passes_test(is_admin_or_librarian)
def member_edit(request, pk):
    member = get_object_or_404(Member, pk=pk)
    
    if request.method == 'POST':
        form = MemberForm(request.POST, instance=member)
        if form.is_valid():
            form.save()
            messages.success(request, 'Member updated successfully!')
            return redirect('member_list')
    else:
        form = MemberForm(instance=member)
    
    return render(request, 'library/member_form.html', {'form': form, 'title': 'Edit Member'})

# Self-service book issuing for members
@login_required
def issue_book_self(request, pk):
    """Allow members to issue books to themselves"""
    book = get_object_or_404(Book, pk=pk)
    
    try:
        member = request.user.member
        
        # Check if member already has this book
        existing_issue = BookIssue.objects.filter(
            book=book, 
            member=member, 
            is_returned=False
        ).exists()
        
        if existing_issue:
            messages.warning(request, 'You have already issued this book.')
            return redirect('book_list')
        
        # Check if book is available
        if not book.is_available:
            messages.error(request, 'This book is not available.')
            return redirect('book_list')
        
        # Check member's current book limit
        current_issues = BookIssue.objects.filter(
            member=member, 
            is_returned=False
        ).count()
        
        settings = LibrarySettings.objects.first()
        max_books = settings.max_books_per_member if settings else 3
        
        if current_issues >= max_books:
            messages.error(request, f'You have reached the maximum limit of {max_books} books.')
            return redirect('book_list')
        
        # Issue the book
        book_issue = BookIssue.objects.create(
            book=book,
            member=member,
            issued_by=request.user
        )
        
        # Update available copies
        book.available_copies -= 1
        book.save()
        
        messages.success(request, f'Book "{book.title}" has been issued to you successfully!')
        
    except Member.DoesNotExist:
        messages.error(request, 'You are not registered as a library member.')
    
    return redirect('book_list')

# Admin book issuing
@login_required
@user_passes_test(is_admin_or_librarian)
def issue_book(request):
    if request.method == 'POST':
        form = BookIssueForm(request.POST)
        if form.is_valid():
            book_issue = form.save(commit=False)
            book_issue.issued_by = request.user
            
            # Check if book is available
            if book_issue.book.available_copies > 0:
                book_issue.save()
                
                # Update available copies
                book_issue.book.available_copies -= 1
                book_issue.book.save()
                
                messages.success(request, 'Book issued successfully!')
                return redirect('issue_list')
            else:
                messages.error(request, 'Book is not available!')
    else:
        form = BookIssueForm()
    
    return render(request, 'library/issue_book.html', {'form': form})

# Book Return
@login_required
@user_passes_test(is_admin_or_librarian)
def return_book(request, pk):
    book_issue = get_object_or_404(BookIssue, pk=pk, is_returned=False)
    
    if request.method == 'POST':
        book_issue.return_date = timezone.now()
        book_issue.is_returned = True
        book_issue.returned_by = request.user
        
        # Calculate fine if overdue
        if book_issue.is_overdue:
            book_issue.calculate_fine()
        
        book_issue.save()
        
        # Update available copies
        book = book_issue.book
        book.available_copies += 1
        book.save()
        
        # Check if there are active reservations for this book
        reservations = BookReservation.objects.filter(
            book=book, 
            is_active=True,
            notified=False
        ).order_by('reservation_date')
        
        if reservations.exists():
            oldest_reservation = reservations.first()
            oldest_reservation.notified = True
            oldest_reservation.save()
            
            messages.info(
                request, 
                f"Member {oldest_reservation.member.user.get_full_name()} has been waiting for this book. "
                f"Please notify them that it's now available."
            )
        
        messages.success(request, f'Book returned successfully! Fine: ${book_issue.fine_amount}')
        return redirect('issue_list')
    
    return render(request, 'library/return_book.html', {'book_issue': book_issue})

@login_required
def issue_list(request):
    issues = BookIssue.objects.select_related('book', 'member__user').all()
    
    # Filter
    status_filter = request.GET.get('status', '')
    if status_filter == 'issued':
        issues = issues.filter(is_returned=False)
    elif status_filter == 'returned':
        issues = issues.filter(is_returned=True)
    elif status_filter == 'overdue':
        issues = issues.filter(is_returned=False, due_date__lt=timezone.now())
    
    # Pagination
    paginator = Paginator(issues, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'library/issue_list.html', {
        'page_obj': page_obj,
        'status_filter': status_filter,
    })

# Visitor Management
def visitor_register(request):
    if request.method == 'POST':
        form = VisitorForm(request.POST)
        if form.is_valid():
            visitor = form.save(commit=False)
            visitor.ip_address = get_client_ip(request)
            visitor.save()
            messages.success(request, 'Thank you for visiting our library!')
            return redirect('home')
    else:
        form = VisitorForm()
    
    return render(request, 'library/visitor_form.html', {'form': form})

@login_required
@user_passes_test(is_admin)
def visitor_list(request):
    visitors = Visitor.objects.all().order_by('-visit_date')
    
    # Pagination
    paginator = Paginator(visitors, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'library/visitor_list.html', {'page_obj': page_obj})

# My Books (for members)
@login_required
def my_books(request):
    try:
        member = request.user.member
        issued_books = BookIssue.objects.filter(
            member=member, 
            is_returned=False
        ).select_related('book')
        
        book_history = BookIssue.objects.filter(
            member=member, 
            is_returned=True
        ).select_related('book').order_by('-return_date')[:10]
        
        reservations = BookReservation.objects.filter(
            member=member, 
            is_active=True
        ).select_related('book')
        
        context = {
            'issued_books': issued_books,
            'book_history': book_history,
            'reservations': reservations,
        }
        
        return render(request, 'library/my_books.html', context)
    except Member.DoesNotExist:
        messages.error(request, 'You are not registered as a library member.')
        return redirect('dashboard')

# Book reservation functionality
@login_required
def reserve_book(request, pk):
    """Reserve a book that is currently unavailable"""
    book = get_object_or_404(Book, pk=pk)
    
    try:
        member = request.user.member
        
        # Check if the book is already reserved by this member
        existing_reservation = BookReservation.objects.filter(book=book, member=member, is_active=True).exists()
        
        if existing_reservation:
            messages.warning(request, 'You have already reserved this book.')
        elif book.is_available:
            messages.info(request, 'This book is currently available for checkout.')
        else:
            # Create the reservation
            BookReservation.objects.create(book=book, member=member)
            messages.success(request, f"Book '{book.title}' has been reserved. You will be notified when it becomes available.")
    
    except Member.DoesNotExist:
        messages.error(request, 'You need to be registered as a member to reserve books.')
    
    return redirect('book_list')

@login_required
def cancel_reservation(request, pk):
    """Cancel an existing book reservation"""
    reservation = get_object_or_404(BookReservation, pk=pk, member=request.user.member)
    
    if reservation.is_active:
        reservation.is_active = False
        reservation.save()
        messages.success(request, f"Reservation for '{reservation.book.title}' has been canceled.")
    else:
        messages.warning(request, "This reservation is no longer active.")
    
    return redirect('my_books')

# Search functionality
def search(request):
    """Advanced search functionality for books"""
    categories = Category.objects.all()
    results = None
    
    if request.GET:
        query = Book.objects.select_related('category').all()
        
        # Apply filters
        title = request.GET.get('title', '')
        if title:
            query = query.filter(title__icontains=title)
            
        author = request.GET.get('author', '')
        if author:
            query = query.filter(author__icontains=author)
            
        isbn = request.GET.get('isbn', '')
        if isbn:
            query = query.filter(isbn__icontains=isbn)
            
        category = request.GET.get('category', '')
        if category:
            query = query.filter(category_id=category)
            
        availability = request.GET.get('availability', '')
        if availability == 'available':
            query = query.filter(available_copies__gt=0)
        elif availability == 'unavailable':
            query = query.filter(available_copies=0)
            
        # Sort results
        sort_by = request.GET.get('sort', '')
        if sort_by == 'title':
            query = query.order_by('title')
        elif sort_by == 'author':
            query = query.order_by('author')
        elif sort_by == 'date':
            query = query.order_by('-publication_date')
        else:
            query = query.order_by('title')  # Default sort
            
        results = query
    
    return render(request, 'library/search.html', {
        'categories': categories,
        'results': results,
    })

# AJAX Views
@login_required
def search_books_ajax(request):
    query = request.GET.get('q', '')
    books = Book.objects.filter(
        Q(title__icontains=query) | Q(author__icontains=query)
    )[:10]
    
    results = []
    for book in books:
        results.append({
            'id': book.id,
            'title': book.title,
            'author': book.author,
            'available': book.is_available
        })
    
    return JsonResponse({'results': results})

@login_required
def search_members_ajax(request):
    query = request.GET.get('q', '')
    members = Member.objects.filter(
        Q(user__first_name__icontains=query) | 
        Q(user__last_name__icontains=query) |
        Q(member_id__icontains=query)
    )[:10]
    
    results = []
    for member in members:
        results.append({
            'id': member.id,
            'name': member.full_name,
            'member_id': member.member_id
        })
    
    return JsonResponse({'results': results})
