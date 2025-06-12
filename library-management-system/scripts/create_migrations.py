#!/usr/bin/env python
"""
Create and apply migrations for the Library Management System
"""

import os
import sys
import subprocess

def run_command(command):
    """Run a command and print its output"""
    print(f"Running: {command}")
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(f"Error: {result.stderr}")
    
    return result.returncode == 0

def main():
    print("Creating and applying migrations for Library Management System...")
    print("="*60)
    
    # Create migrations
    print("\n1. Creating migrations...")
    if not run_command("python manage.py makemigrations"):
        print("Failed to create migrations!")
        return False
    
    # Apply migrations
    print("\n2. Applying migrations...")
    if not run_command("python manage.py migrate"):
        print("Failed to apply migrations!")
        return False
    
    print("\n" + "="*60)
    print("Migrations completed successfully!")
    print("You can now run the setup script to create initial data.")
    
    return True

if __name__ == '__main__':
    main()
