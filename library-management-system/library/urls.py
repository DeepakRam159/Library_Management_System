from django.urls import path
from . import views

urlpatterns = [
    # Authentication
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),

    # Home and Dashboard
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Books
    path('books/', views.book_list, name='book_list'),
    path('books/add/', views.book_add, name='book_add'),
    path('books/<int:pk>/edit/', views.book_edit, name='book_edit'),
    path('books/<int:pk>/delete/', views.book_delete, name='book_delete'),
    path('books/<int:pk>/issue/', views.issue_book_self, name='issue_book_self'),
    
    # Members
    path('members/', views.member_list, name='member_list'),
    path('members/add/', views.member_add, name='member_add'),
    path('members/<int:pk>/edit/', views.member_edit, name='member_edit'),
    
    # Book Issues and Returns
    path('issue/', views.issue_book, name='issue_book'),
    path('issues/', views.issue_list, name='issue_list'),
    path('return/<int:pk>/', views.return_book, name='return_book'),
    
    # My Books
    path('my-books/', views.my_books, name='my_books'),
    
    # Book Reservations
    path('reserve-book/<int:pk>/', views.reserve_book, name='reserve_book'),
    path('cancel-reservation/<int:pk>/', views.cancel_reservation, name='cancel_reservation'),

    # Visitors
    path('visitor/register/', views.visitor_register, name='visitor_register'),
    path('visitors/', views.visitor_list, name='visitor_list'),

    # Search
    path('search/', views.search, name='search'),
    
    # AJAX
    path('ajax/search-books/', views.search_books_ajax, name='search_books_ajax'),
    path('ajax/search-members/', views.search_members_ajax, name='search_members_ajax'),
]
