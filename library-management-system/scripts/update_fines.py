#!/usr/bin/env python
"""
Script to check for overdue books and update fines
Run this script periodically to update fine amounts for overdue books
"""

import os
import sys
import django
from datetime import datetime

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'library_project.settings')
django.setup()

from django.utils import timezone
from library.models import BookIssue, LibrarySettings

def update_fines():
    print("Checking for overdue books and updating fine amounts...")
    
    # Get library settings for fine amount per day
    try:
        settings = LibrarySettings.objects.first()
        fine_per_day = settings.fine_per_day if settings else 1.00
    except:
        fine_per_day = 1.00  # Default to $1 per day if settings not found
    
    # Get all overdue and non-returned books
    overdue_issues = BookIssue.objects.filter(
        is_returned=False,
        due_date__lt=timezone.now()
    )
    
    if not overdue_issues:
        print("No overdue books found.")
        return
    
    count = 0
    for issue in overdue_issues:
        old_fine = issue.fine_amount
        issue.calculate_fine()  # This will update the fine_amount based on days overdue
        
        if issue.fine_amount != old_fine:
            issue.save()
            count += 1
            print(f"Updated fine for '{issue.book.title}' borrowed by {issue.member.user.get_full_name()}: ${issue.fine_amount}")
    
    print(f"\nFines updated for {count} overdue books.")

if __name__ == '__main__':
    update_fines()
