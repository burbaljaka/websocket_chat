import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import AsyncJsonWebsocketConsumer

class ChatConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name

        #join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        #leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.room_name
        )

    #receive message from websocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        #send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )

    #receive message from room group
    async def chat_message(self, event):
        message = event['message']

        #send message to websocket
        await self.send(text_data=json.dumps({
            'message': message
        }
        ))

# docker run -p 6379:6379 -d redis:5