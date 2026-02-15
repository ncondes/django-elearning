"""
Django management command to seed the database with sample data.
Usage: python manage.py seed_db [--large]
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.accounts.models import StatusUpdate
from apps.courses.models import Course, Enrollment, CourseFeedback
import random

User = get_user_model()


class Command(BaseCommand):
    help = 'Seeds the database with sample users, courses, and status updates'

    def add_arguments(self, parser):
        parser.add_argument(
            '--users',
            type=int,
            default=10,
            help='Number of users to create (default: 10, ignored if --large)'
        )
        parser.add_argument(
            '--large',
            action='store_true',
            help='Create a large dataset (50 users, 20 courses, 100+ enrollments)'
        )

    def handle(self, *args, **options):
        large_mode = options['large']
        num_users = 50 if large_mode else options['users']
        
        if large_mode:
            self.stdout.write(self.style.NOTICE('Starting LARGE database seeding...'))
        else:
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
            f'\nUsers created: {users_created}'
        ))
        self.stdout.write(self.style.SUCCESS(f'  - {teachers_created} Teachers'))
        self.stdout.write(self.style.SUCCESS(f'  - {students_created} Students'))
        
        # Create sample courses (by teachers)
        course_titles_base = [
            ('Introduction to Python', 'Learn the fundamentals of Python programming, from basic syntax to object-oriented programming.'),
            ('Web Development with Django', 'Build modern web applications using the Django framework.'),
            ('Data Science Fundamentals', 'Explore data analysis, visualization, and machine learning basics.'),
            ('JavaScript Essentials', 'Master JavaScript for front-end and back-end development.'),
            ('Database Design', 'Learn relational database design and SQL.'),
            ('Machine Learning 101', 'Introduction to machine learning algorithms and applications.'),
            ('Mobile App Development', 'Create cross-platform mobile applications.'),
            ('Cloud Computing Basics', 'Understand cloud services and deployment strategies.'),
        ]
        
        # Extended courses for large mode
        course_titles_extended = [
            ('Advanced Python Programming', 'Deep dive into Python with decorators, generators, and async programming.'),
            ('React Fundamentals', 'Build interactive UIs with React and modern JavaScript.'),
            ('DevOps Essentials', 'Learn CI/CD, Docker, and deployment automation.'),
            ('Cybersecurity Basics', 'Introduction to security principles and best practices.'),
            ('UI/UX Design Principles', 'Design user-friendly interfaces and experiences.'),
            ('Algorithms & Data Structures', 'Master fundamental algorithms and data structures.'),
            ('API Design & Development', 'Build robust RESTful APIs.'),
            ('Agile Project Management', 'Learn Scrum, Kanban, and agile methodologies.'),
            ('Natural Language Processing', 'Introduction to NLP and text analysis.'),
            ('Computer Vision Basics', 'Image processing and computer vision fundamentals.'),
            ('Blockchain Fundamentals', 'Understanding blockchain technology and applications.'),
            ('IoT Development', 'Building Internet of Things applications.'),
        ]
        
        course_titles = course_titles_base + (course_titles_extended if large_mode else [])
        
        teachers = list(User.objects.filter(user_type='teacher'))
        students = list(User.objects.filter(user_type='student'))
        courses_created = 0
        enrollments_created = 0
        feedback_created = 0
        
        feedback_comments = [
            'Great course!',
            'Very informative.',
            'Learned a lot!',
            'Excellent teaching.',
            'Well structured content.',
            'The instructor explains concepts clearly.',
            'Highly recommended!',
            'Good pace and examples.',
            'Could use more practical exercises.',
            'Perfect for beginners.',
            '',
        ]
        
        if teachers:
            self.stdout.write(self.style.NOTICE('\nCreating courses...'))
            for title, description in course_titles:
                if Course.objects.filter(title=title).exists():
                    continue
                teacher = random.choice(teachers)
                course = Course.objects.create(
                    title=title,
                    description=description,
                    teacher=teacher,
                    is_active=True
                )
                courses_created += 1
                self.stdout.write(f'  Created course: {title} (by {teacher.username})')
                
                # Enroll students - more in large mode
                if students:
                    max_enrollments = min(15 if large_mode else 5, len(students))
                    num_enrollments = random.randint(3 if large_mode else 1, max_enrollments)
                    enrolled_students = random.sample(students, num_enrollments)
                    for student in enrolled_students:
                        enrollment, created = Enrollment.objects.get_or_create(
                            student=student,
                            course=course,
                            defaults={'is_active': True}
                        )
                        if created:
                            enrollments_created += 1
                        # More feedback in large mode
                        feedback_chance = 0.6 if large_mode else 0.5
                        if created and random.random() < feedback_chance:
                            CourseFeedback.objects.create(
                                enrollment=enrollment,
                                rating=random.randint(2, 5),
                                comment=random.choice(feedback_comments)
                            )
                            feedback_created += 1
            
            self.stdout.write(self.style.SUCCESS(f'\nCourses created: {courses_created}'))
            self.stdout.write(self.style.SUCCESS(f'Enrollments created: {enrollments_created}'))
            self.stdout.write(self.style.SUCCESS(f'Feedback created: {feedback_created}'))
        
        # Summary
        self.stdout.write(self.style.NOTICE('\n' + '='*50))
        self.stdout.write(self.style.SUCCESS('Seeding Summary:'))
        self.stdout.write(f'  Users: {users_created} ({teachers_created} teachers, {students_created} students)')
        self.stdout.write(f'  Courses: {courses_created}')
        self.stdout.write(f'  Enrollments: {enrollments_created}')
        self.stdout.write(f'  Feedback: {feedback_created}')
        self.stdout.write(f'  Status Updates: {StatusUpdate.objects.count()}')
        self.stdout.write(self.style.NOTICE('='*50))
        self.stdout.write(self.style.NOTICE(
            '\nDefault password for all seeded users: password123'
        ))
