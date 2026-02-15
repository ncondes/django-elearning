from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.courses.models import Enrollment, CourseMaterial, CourseFeedback
from apps.notifications.models import Notification


def send_realtime_notification(notification):
    """Send notification via WebSocket for real-time updates."""
    try:
        from apps.notifications.consumers import send_notification_to_user
        notification_data = {
            'id': notification.id,
            'type': notification.notification_type,
            'title': notification.title,
            'message': notification.message,
            'course_id': notification.course.id if notification.course else None,
            'course_title': notification.course.title if notification.course else None,
            'created_at': notification.created_at.isoformat(),
        }
        send_notification_to_user(notification.recipient.id, notification_data)
    except Exception:
        pass


@receiver(post_save, sender=Enrollment)
def notify_teacher_on_enrollment(sender, instance, created, **kwargs):
    """Notify teacher when a student enrolls in their course."""
    if created and instance.is_active:
        notification = Notification.objects.create(
            recipient=instance.course.teacher,
            notification_type=Notification.NotificationType.ENROLLMENT,
            title='New Student Enrollment',
            message=f'{instance.student.get_full_name() or instance.student.username} enrolled in your course "{instance.course.title}".',
            course=instance.course,
            actor=instance.student
        )
        send_realtime_notification(notification)


@receiver(post_save, sender=CourseMaterial)
def notify_students_on_new_material(sender, instance, created, **kwargs):
    """Notify enrolled students when new material is uploaded."""
    if created:
        course = instance.course
        enrollments = course.enrollments.filter(is_active=True, is_blocked=False)
        
        for enrollment in enrollments:
            notification = Notification.objects.create(
                recipient=enrollment.student,
                notification_type=Notification.NotificationType.NEW_MATERIAL,
                title='New Course Material',
                message=f'New material "{instance.title}" has been uploaded to "{course.title}".',
                course=course,
                actor=course.teacher
            )
            send_realtime_notification(notification)


@receiver(post_save, sender=CourseFeedback)
def notify_teacher_on_rating(sender, instance, created, **kwargs):
    """Notify teacher when a student rates their course."""
    if created:
        course = instance.enrollment.course
        student = instance.enrollment.student
        
        notification = Notification.objects.create(
            recipient=course.teacher,
            notification_type=Notification.NotificationType.NEW_RATING,
            title='New Course Rating',
            message=f'{student.get_full_name() or student.username} rated your course "{course.title}" with {instance.rating} stars.',
            course=course,
            actor=student
        )
        send_realtime_notification(notification)
