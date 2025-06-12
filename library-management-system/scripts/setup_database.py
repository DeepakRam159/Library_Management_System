#!/usr/bin/env python
"""
Database setup script for Library Management System
Run this script to create initial data
"""

import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'library_project.settings')
django.setup()

from django.contrib.auth.models import User, Group
from library.models import Category, Book, Member, LibrarySettings
from datetime import date

def create_initial_data():
    print("Creating initial data for Library Management System...")
    
    # Create superuser if not exists
    if not User.objects.filter(username='admin').exists():
        admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@library.com',
            password='admin123',
            first_name='Library',
            last_name='Administrator'
        )
        print("✓ Created admin user (username: admin, password: admin123)")
    
    # Create groups
    librarian_group, created = Group.objects.get_or_create(name='Librarian')
    if created:
        print("✓ Created Librarian group")
    
    # Create librarian user
    if not User.objects.filter(username='librarian').exists():
        librarian_user = User.objects.create_user(
            username='librarian',
            email='librarian@library.com',
            password='lib123',
            first_name='John',
            last_name='Librarian'
        )
        librarian_user.groups.add(librarian_group)
        print("✓ Created librarian user (username: librarian, password: lib123)")
    
    # Create sample student user
    if not User.objects.filter(username='student').exists():
        student_user = User.objects.create_user(
            username='student',
            email='student@library.com',
            password='student123',
            first_name='Jane',
            last_name='Student'
        )
        
        # Create member profile for student
        Member.objects.create(
            user=student_user,
            member_id='STU001',
            phone='123-456-7890',
            address='123 Student St, City, State',
            member_type='student',
            department='Computer Science',
            enrollment_number='CS2024001',
            is_active=True
        )
        print("✓ Created student user and member profile (username: student, password: student123)")
    
    # Create categories
    categories_data = [
        {'name': 'Fiction', 'description': 'Fictional books and novels'},
        {'name': 'Non-Fiction', 'description': 'Non-fictional books'},
        {'name': 'Science', 'description': 'Science and technology books'},
        {'name': 'History', 'description': 'Historical books'},
        {'name': 'Biography', 'description': 'Biographical books'},
        {'name': 'Technology', 'description': 'Technology and programming books'},
        {'name': 'Literature', 'description': 'Classic and modern literature'},
        {'name': 'Reference', 'description': 'Reference books and manuals'},
    ]
    
    for cat_data in categories_data:
        category, created = Category.objects.get_or_create(
            name=cat_data['name'],
            defaults={'description': cat_data['description']}
        )
        if created:
            print(f"✓ Created category: {cat_data['name']}")
    
    # Create sample books
    books_data = [
        {
            'title': 'Python Programming for Beginners',
            'author': 'John Smith',
            'isbn': '9781234567890',
            'category': 'Technology',
            'total_copies': 5,
            'available_copies': 5,
            'publication_date': date(2023, 1, 15),
            'publisher': 'Tech Books Publishing',
            'description': 'A comprehensive guide to Python programming for beginners.'
        },
        {
            'title': 'The Great Gatsby',
            'author': 'F. Scott Fitzgerald',
            'isbn': '9780743273565',
            'category': 'Literature',
            'total_copies': 3,
            'available_copies': 3,
            'publication_date': date(1925, 4, 10),
            'publisher': 'Scribner',
            'description': 'A classic American novel set in the Jazz Age.'
        },
        {
            'title': 'Introduction to Algorithms',
            'author': 'Thomas H. Cormen',
            'isbn': '9780262033848',
            'category': 'Technology',
            'total_copies': 4,
            'available_copies': 4,
            'publication_date': date(2009, 7, 31),
            'publisher': 'MIT Press',
            'description': 'Comprehensive introduction to algorithms and data structures.'
        },
        {
            'title': 'A Brief History of Time',
            'author': 'Stephen Hawking',
            'isbn': '9780553380163',
            'category': 'Science',
            'total_copies': 2,
            'available_copies': 2,
            'publication_date': date(1988, 4, 1),
            'publisher': 'Bantam Books',
            'description': 'Popular science book on cosmology by Stephen Hawking.'
        },
        {
            'title': 'To Kill a Mockingbird',
            'author': 'Harper Lee',
            'isbn': '9780061120084',
            'category': 'Literature',
            'total_copies': 4,
            'available_copies': 4,
            'publication_date': date(1960, 7, 11),
            'publisher': 'J.B. Lippincott & Co.',
            'description': 'A novel about racial injustice in the American South.'
        },
        {
            'title': 'The Art of War',
            'author': 'Sun Tzu',
            'isbn': '9781590302255',
            'category': 'History',
            'total_copies': 3,
            'available_copies': 3,
            'publication_date': date(2003, 3, 7),
            'publisher': 'Shambhala Publications',
            'description': 'Ancient Chinese military treatise.'
        },
        {
            'title': 'Steve Jobs',
            'author': 'Walter Isaacson',
            'isbn': '9781451648539',
            'category': 'Biography',
            'total_copies': 2,
            'available_copies': 2,
            'publication_date': date(2011, 10, 24),
            'publisher': 'Simon & Schuster',
            'description': 'Biography of Apple co-founder Steve Jobs.'
        },
        {
            'title': 'Clean Code',
            'author': 'Robert C. Martin',
            'isbn': '9780132350884',
            'category': 'Technology',
            'total_copies': 3,
            'available_copies': 3,
            'publication_date': date(2008, 8, 1),
            'publisher': 'Prentice Hall',
            'description': 'A handbook of agile software craftsmanship.'
        }
    ]
    
    for book_data in books_data:
        category = Category.objects.get(name=book_data['category'])
        book, created = Book.objects.get_or_create(
            isbn=book_data['isbn'],
            defaults={
                'title': book_data['title'],
                'author': book_data['author'],
                'category': category,
                'total_copies': book_data['total_copies'],
                'available_copies': book_data['available_copies'],
                'publication_date': book_data['publication_date'],
                'publisher': book_data['publisher'],
                'description': book_data['description']
            }
        )
        if created:
            print(f"✓ Created book: {book_data['title']}")
    
    # Create library settings
    if not LibrarySettings.objects.exists():
        LibrarySettings.objects.create(
            library_name="Central Library Management System",
            max_books_per_member=3,
            loan_period_days=14,
            fine_per_day=1.00,
            library_email="library@example.com",
            library_phone="555-0123",
            library_address="123 Library Street, City, State 12345"
        )
        print("✓ Created library settings")
    
    print("\n" + "="*50)
    print("Initial data creation completed successfully!")
    print("="*50)
    print("\nLogin Credentials:")
    print("Admin: username=admin, password=admin123")
    print("Librarian: username=librarian, password=lib123")
    print("Student: username=student, password=student123")
    print("\nYou can now run the server with: python manage.py runserver")

if __name__ == '__main__':
    create_initial_data()
