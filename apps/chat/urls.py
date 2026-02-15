from django.urls import path

from apps.chat import views

app_name = 'chat'

urlpatterns = [
    path('course/<int:course_pk>/', views.chat_room, name='room'),
    path('api/user-chats/', views.get_user_chats, name='user_chats'),
    path('api/messages/<int:room_id>/', views.get_chat_messages, name='get_messages'),
]
