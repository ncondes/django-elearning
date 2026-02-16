import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


class NotificationConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for real-time notifications."""
    
    async def connect(self):
        """Handle WebSocket connection."""
        if self.scope['user'].is_anonymous:
            await self.close()
            return
        
        self.user = self.scope['user']
        self.group_name = f'notifications_{self.user.id}'
        
        # Join user's notification group
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Send current unread count
        unread_count = await self.get_unread_count()
        await self.send(text_data=json.dumps({
            'type': 'unread_count',
            'count': unread_count
        }))
    
    async def disconnect(self, close_code):
        """Handle WebSocket disconnection."""
        if hasattr(self, 'group_name'):
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name
            )
    
    async def receive(self, text_data):
        """Handle incoming WebSocket messages."""
        pass
    
    async def notification_message(self, event):
        """Send notification to WebSocket."""
        await self.send(text_data=json.dumps({
            'type': 'new_notification',
            'notification': event['notification']
        }))
    
    async def unread_count_update(self, event):
        """Send updated unread count."""
        await self.send(text_data=json.dumps({
            'type': 'unread_count',
            'count': event['count']
        }))
    
    @database_sync_to_async
    def get_unread_count(self):
        """Get unread notification count for user."""
        from apps.notifications.models import Notification
        return Notification.objects.filter(recipient=self.user, is_read=False).count()


def send_notification_to_user(user_id, notification_data):
    """
    Helper function to send a notification to a user via WebSocket.
    Call this from signals after creating a notification.
    """
    channel_layer = get_channel_layer()
    group_name = f'notifications_{user_id}'
    
    async_to_sync(channel_layer.group_send)(
        group_name,
        {
            'type': 'notification_message',
            'notification': notification_data
        }
    )
