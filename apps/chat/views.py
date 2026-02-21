from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_GET

from apps.chat.models import ChatRoom, ChatMessage
from apps.courses.models import Course, Enrollment


@login_required
def chat_room(request, course_pk):
    """View for course chat room."""
    course = get_object_or_404(Course, pk=course_pk)
    user = request.user
    has_access = False
    
    if course.teacher == user:
        has_access = True
    else:
        has_access = Enrollment.objects.filter(
            student=user,
            course=course,
            is_active=True,
            is_blocked=False
        ).exists()
    
    if not has_access:
        messages.error(request, 'You do not have access to this chat room.')
        return redirect('courses:course_detail', pk=course_pk)
    
    chat_room, created = ChatRoom.objects.get_or_create(course=course)
    
    recent_messages = ChatMessage.objects.filter(room=chat_room).select_related('user').order_by('-created_at')[:50]
    recent_messages = list(reversed(recent_messages))
    
    online_users = chat_room.online_users.select_related('user').all()
    
    context = {
        'course': course,
        'chat_room': chat_room,
        'chat_messages': recent_messages,
        'online_users': online_users,
    }
    return render(request, 'chat/chat_room.html', context)


@login_required
@require_GET
def get_user_chats(request):
    """Get all chat rooms available to the current user (API endpoint)."""
    user = request.user
    chat_rooms = []
    
    if user.is_teacher:
        # Teacher: get chat rooms for courses they teach
        courses = Course.objects.filter(teacher=user, is_active=True)
        for course in courses:
            room, _ = ChatRoom.objects.get_or_create(course=course)
            online_count = room.online_users.count()
            chat_rooms.append({
                'room_id': room.id,
                'course_id': course.id,
                'course_title': course.title,
                'online_count': online_count,
                'is_teacher': True,
            })
    else:
        # Student: get chat rooms for enrolled courses
        enrollments = Enrollment.objects.filter(
            student=user,
            is_active=True,
            is_blocked=False
        ).select_related('course')
        
        for enrollment in enrollments:
            course = enrollment.course
            room, _ = ChatRoom.objects.get_or_create(course=course)
            online_count = room.online_users.count()
            chat_rooms.append({
                'room_id': room.id,
                'course_id': course.id,
                'course_title': course.title,
                'online_count': online_count,
                'is_teacher': False,
            })
    
    return JsonResponse({'chats': chat_rooms})


@login_required
@require_GET
def get_chat_messages(request, room_id):
    """Get recent messages for a chat room (API endpoint)."""
    try:
        room = ChatRoom.objects.get(id=room_id)
    except ChatRoom.DoesNotExist:
        return JsonResponse({'error': 'Room not found'}, status=404)
    
    user = request.user
    course = room.course
    has_access = False
    
    if course.teacher == user:
        has_access = True
    else:
        has_access = Enrollment.objects.filter(
            student=user,
            course=course,
            is_active=True,
            is_blocked=False
        ).exists()
    
    if not has_access:
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    messages_qs = ChatMessage.objects.filter(room=room).select_related('user').order_by('-created_at')[:50]
    messages_list = [
        {
            'id': msg.id,
            'user_id': msg.user.id,
            'username': msg.user.username,
            'full_name': msg.user.get_full_name() or msg.user.username,
            'content': msg.content,
            'timestamp': msg.created_at.isoformat(),
        }
        for msg in reversed(messages_qs)
    ]
    
    online_users = [
        {
            'user_id': ou.user.id,
            'username': ou.user.username,
            'full_name': ou.user.get_full_name() or ou.user.username,
        }
        for ou in room.online_users.select_related('user').all()
    ]
    
    return JsonResponse({
        'messages': messages_list,
        'online_users': online_users,
        'course_title': course.title,
    })
