"""
Django management command to seed the database with sample data.
Usage: python manage.py seed_db
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.accounts.models import StatusUpdate
import random

User = get_user_model()


class Command(BaseCommand):
    help = 'Seeds the database with sample users and status updates'

    def add_arguments(self, parser):
        parser.add_argument(
            '--users',
            type=int,
            default=10,
            help='Number of users to create (default: 10)'
        )

    def handle(self, *args, **options):
        num_users = options['users']
        
        self.stdout.write(self.style.NOTICE('Starting database seeding...'))
        
        # Create superuser if it doesn't exist
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser(
                username='admin',
                email='admin@example.com',
                password='admin123',
                first_name='Admin',
                last_name='User'
            )
            self.stdout.write(self.style.SUCCESS('Created superuser: admin / admin123'))
        else:
            self.stdout.write(self.style.WARNING('Superuser "admin" already exists'))

        # Sample data
        first_names = ['Alice', 'Bob', 'Charlie', 'Diana', 'Eve', 'Frank', 'Grace', 'Henry', 'Ivy', 'Jack',
                       'Kate', 'Leo', 'Mia', 'Noah', 'Olivia', 'Peter', 'Quinn', 'Rose', 'Sam', 'Tina']
        last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis', 
                      'Rodriguez', 'Martinez', 'Wilson', 'Anderson', 'Taylor', 'Thomas', 'Moore']
        bios = [
            'Passionate about learning new things every day.',
            'Love to share knowledge and help others grow.',
            'Always curious, always exploring.',
            'Dedicated to excellence in education.',
            'Lifelong learner and educator.',
            'Enthusiastic about technology and innovation.',
            'Committed to making a difference through education.',
            'Believer in the power of knowledge.',
            '',  # Some users without bio
            '',
        ]
        status_messages = [
            'Just finished an amazing course on Python!',
            'Looking forward to the new semester.',
            'Anyone interested in a study group?',
            'Great lecture today on machine learning.',
            'Finally understood recursion! 🎉',
            'Working on my final project.',
            'Coffee and coding - perfect combination.',
            'Just enrolled in a new course!',
            'Learning something new every day.',
            'Excited about the upcoming workshop!',
            'Completed my first assignment!',
            'Study time! 📚',
        ]

        users_created = 0
        teachers_created = 0
        students_created = 0
        
        for i in range(num_users):
            first_name = random.choice(first_names)
            last_name = random.choice(last_names)
            username = f'{first_name.lower()}{last_name.lower()}{random.randint(1, 99)}'
            
            # Skip if username already exists
            if User.objects.filter(username=username).exists():
                continue
            
            # 30% teachers, 70% students
            user_type = random.choices(
                [User.UserType.STUDENT, User.UserType.TEACHER],
                weights=[70, 30]
            )[0]
            
            user = User.objects.create_user(
                username=username,
                email=f'{username}@example.com',
                password='password123',
                first_name=first_name,
                last_name=last_name,
                user_type=user_type,
                bio=random.choice(bios)
            )
            users_created += 1
            if user.is_teacher:
                teachers_created += 1
            else:
                students_created += 1
            
            # Create 0-3 status updates per user
            num_statuses = random.randint(0, 3)
            for _ in range(num_statuses):
                StatusUpdate.objects.create(
                    user=user,
                    content=random.choice(status_messages)
                )
            
            role = 'Teacher' if user.is_teacher else 'Student'
            self.stdout.write(f'  Created {role}: {username}')

        self.stdout.write(self.style.SUCCESS(
            f'\nSeeding complete! Created {users_created} users:'
        ))
        self.stdout.write(self.style.SUCCESS(f'  - {teachers_created} Teachers'))
        self.stdout.write(self.style.SUCCESS(f'  - {students_created} Students'))
        self.stdout.write(self.style.NOTICE(
            'Default password for all seeded users: password123'
        ))
