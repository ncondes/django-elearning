"""
Django management command to flush (clear) the database.
Usage: python manage.py flush_db
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.accounts.models import StatusUpdate
from apps.courses.models import Course, CourseMaterial, Enrollment, CourseFeedback

User = get_user_model()


class Command(BaseCommand):
    help = 'Flushes (clears) all user data from the database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--keep-superusers',
            action='store_true',
            help='Keep superuser accounts when flushing'
        )
        parser.add_argument(
            '--yes',
            action='store_true',
            help='Skip confirmation prompt'
        )

    def handle(self, *args, **options):
        keep_superusers = options['keep_superusers']
        skip_confirm = options['yes']
        
        # Count records
        user_count = User.objects.count()
        status_count = StatusUpdate.objects.count()
        course_count = Course.objects.count()
        enrollment_count = Enrollment.objects.count()
        
        if user_count == 0 and status_count == 0 and course_count == 0:
            self.stdout.write(self.style.WARNING('Database is already empty.'))
            return
        
        # Confirmation
        if not skip_confirm:
            self.stdout.write(self.style.WARNING(
                f'\nThis will delete:'
            ))
            if keep_superusers:
                regular_users = User.objects.filter(is_superuser=False).count()
                self.stdout.write(f'  - {regular_users} regular users (keeping superusers)')
            else:
                self.stdout.write(f'  - {user_count} users (including superusers)')
            self.stdout.write(f'  - {status_count} status updates')
            self.stdout.write(f'  - {course_count} courses')
            self.stdout.write(f'  - {enrollment_count} enrollments')
            
            confirm = input('\nAre you sure you want to continue? [y/N]: ')
            if confirm.lower() != 'y':
                self.stdout.write(self.style.NOTICE('Operation cancelled.'))
                return
        
        self.stdout.write(self.style.NOTICE('\nFlushing database...'))
        
        # Delete course-related data first (due to foreign keys)
        deleted_feedback = CourseFeedback.objects.all().delete()[0]
        self.stdout.write(f'  Deleted {deleted_feedback} course feedbacks')
        
        deleted_materials = CourseMaterial.objects.all().delete()[0]
        self.stdout.write(f'  Deleted {deleted_materials} course materials')
        
        deleted_enrollments = Enrollment.objects.all().delete()[0]
        self.stdout.write(f'  Deleted {deleted_enrollments} enrollments')
        
        deleted_courses = Course.objects.all().delete()[0]
        self.stdout.write(f'  Deleted {deleted_courses} courses')
        
        # Delete status updates
        deleted_statuses = StatusUpdate.objects.all().delete()[0]
        self.stdout.write(f'  Deleted {deleted_statuses} status updates')
        
        # Delete users
        if keep_superusers:
            deleted_users = User.objects.filter(is_superuser=False).delete()[0]
            self.stdout.write(f'  Deleted {deleted_users} regular users (superusers kept)')
        else:
            deleted_users = User.objects.all().delete()[0]
            self.stdout.write(f'  Deleted {deleted_users} users')
        
        self.stdout.write(self.style.SUCCESS('\nDatabase flushed successfully!'))
