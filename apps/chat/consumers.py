import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async


class ChatConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for course chat rooms."""
    
    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'chat_{self.room_id}'
        self.user = self.scope['user']
        
        if not self.user.is_authenticated:
            await self.close()
            return
        
        # Check if user has access to this chat room
        has_access = await self.check_access()
        if not has_access:
            await self.close()
            return
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Add user to online users
        await self.add_online_user()
        
        # Notify others that user joined
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_join',
                'user_id': self.user.id,
                'username': self.user.username,
                'full_name': self.user.get_full_name() or self.user.username,
            }
        )
        
        # Send current online users to the new user
        online_users = await self.get_online_users()
        await self.send(text_data=json.dumps({
            'type': 'online_users',
            'users': online_users
        }))
    
    async def disconnect(self, close_code):
        if hasattr(self, 'user') and self.user.is_authenticated:
            # Remove user from online users
            await self.remove_online_user()
            
            # Notify others that user left
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'user_leave',
                    'user_id': self.user.id,
                    'username': self.user.username,
                }
            )
        
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        data = json.loads(text_data)
        message_type = data.get('type', 'chat_message')
        
        if message_type == 'chat_message':
            content = data.get('message', '').strip()
            if content:
                # Save message to database
                message_data = await self.save_message(content)
                
                # Broadcast message to room
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'chat_message',
                        'message': content,
                        'user_id': self.user.id,
                        'username': self.user.username,
                        'full_name': self.user.get_full_name() or self.user.username,
                        'timestamp': message_data['timestamp'],
                        'message_id': message_data['id'],
                    }
                )
                
                # Notify users not in the chat room (for badge updates)
                await self.notify_absent_users(content, message_data)
    
    async def chat_message(self, event):
        """Handle chat message event."""
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message': event['message'],
            'user_id': event['user_id'],
            'username': event['username'],
            'full_name': event['full_name'],
            'timestamp': event['timestamp'],
            'message_id': event['message_id'],
        }))
    
    async def user_join(self, event):
        """Handle user join event."""
        await self.send(text_data=json.dumps({
            'type': 'user_join',
            'user_id': event['user_id'],
            'username': event['username'],
            'full_name': event['full_name'],
        }))
    
    async def user_leave(self, event):
        """Handle user leave event."""
        await self.send(text_data=json.dumps({
            'type': 'user_leave',
            'user_id': event['user_id'],
            'username': event['username'],
        }))
    
    @database_sync_to_async
    def check_access(self):
        """Check if user has access to this chat room."""
        from apps.chat.models import ChatRoom
        from apps.courses.models import Enrollment
        
        try:
            room = ChatRoom.objects.get(id=self.room_id)
            course = room.course
            
            # Teacher always has access
            if course.teacher == self.user:
                return True
            
            # Check if student is enrolled
            return Enrollment.objects.filter(
                student=self.user,
                course=course,
                is_active=True,
                is_blocked=False
            ).exists()
        except ChatRoom.DoesNotExist:
            return False
    
    @database_sync_to_async
    def add_online_user(self):
        """Add user to online users list."""
        from apps.chat.models import ChatRoom, OnlineUser
        
        room = ChatRoom.objects.get(id=self.room_id)
        OnlineUser.objects.get_or_create(room=room, user=self.user)
    
    @database_sync_to_async
    def remove_online_user(self):
        """Remove user from online users list."""
        from apps.chat.models import ChatRoom, OnlineUser
        
        try:
            room = ChatRoom.objects.get(id=self.room_id)
            OnlineUser.objects.filter(room=room, user=self.user).delete()
        except ChatRoom.DoesNotExist:
            pass
    
    @database_sync_to_async
    def get_online_users(self):
        """Get list of online users in this room."""
        from apps.chat.models import ChatRoom
        
        try:
            room = ChatRoom.objects.get(id=self.room_id)
            return [
                {
                    'user_id': ou.user.id,
                    'username': ou.user.username,
                    'full_name': ou.user.get_full_name() or ou.user.username,
                }
                for ou in room.online_users.select_related('user').all()
            ]
        except ChatRoom.DoesNotExist:
            return []
    
    @database_sync_to_async
    def save_message(self, content):
        """Save message to database."""
        from apps.chat.models import ChatRoom, ChatMessage
        
        room = ChatRoom.objects.get(id=self.room_id)
        message = ChatMessage.objects.create(
            room=room,
            user=self.user,
            content=content
        )
        return {
            'id': message.id,
            'timestamp': message.created_at.isoformat(),
        }
    
    async def notify_absent_users(self, content, message_data):
        """Notify users who have access but are not in the chat room."""
        absent_user_ids = await self.get_absent_user_ids()
        
        for user_id in absent_user_ids:
            # Send to user's personal chat notification group
            await self.channel_layer.group_send(
                f'chat_notifications_{user_id}',
                {
                    'type': 'new_message_notification',
                    'room_id': int(self.room_id),
                    'sender_id': self.user.id,
                    'sender_name': self.user.get_full_name() or self.user.username,
                    'message_preview': content[:50] + ('...' if len(content) > 50 else ''),
                    'timestamp': message_data['timestamp'],
                }
            )
    
    @database_sync_to_async
    def get_absent_user_ids(self):
        """Get user IDs who have access to this room but are not currently online in it."""
        from apps.chat.models import ChatRoom, OnlineUser
        from apps.courses.models import Enrollment
        
        try:
            room = ChatRoom.objects.get(id=self.room_id)
            course = room.course
            
            # Get all users with access
            user_ids = set()
            
            # Add teacher
            user_ids.add(course.teacher_id)
            
            # Add enrolled students
            enrolled_ids = Enrollment.objects.filter(
                course=course,
                is_active=True,
                is_blocked=False
            ).values_list('student_id', flat=True)
            user_ids.update(enrolled_ids)
            
            # Remove sender
            user_ids.discard(self.user.id)
            
            # Remove users currently online in the room
            online_ids = set(OnlineUser.objects.filter(room=room).values_list('user_id', flat=True))
            user_ids -= online_ids
            
            return list(user_ids)
        except ChatRoom.DoesNotExist:
            return []


class ChatNotificationConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for global chat notifications (badge updates)."""
    
    async def connect(self):
        if self.scope['user'].is_anonymous:
            await self.close()
            return
        
        self.user = self.scope['user']
        self.group_name = f'chat_notifications_{self.user.id}'
        
        # Join user's personal notification group
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        
        await self.accept()
    
    async def disconnect(self, close_code):
        if hasattr(self, 'group_name'):
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name
            )
    
    async def receive(self, text_data):
        """Handle incoming messages (not used, but required)."""
        pass
    
    async def new_message_notification(self, event):
        """Send new message notification to the client."""
        await self.send(text_data=json.dumps({
            'type': 'new_message',
            'room_id': event['room_id'],
            'sender_id': event['sender_id'],
            'sender_name': event['sender_name'],
            'message_preview': event['message_preview'],
            'timestamp': event['timestamp'],
        }))
