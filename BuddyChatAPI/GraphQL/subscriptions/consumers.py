import json
from channels.generic.websocket import AsyncWebsocketConsumer

class MainConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = await self.scope['user']
        if not self.user or not self.user.is_authenticated:
            await self.close()
        else:
            self.group_name = f'user_{self.user.username}'
            await self.channel_layer.group_add(
                self.group_name,
                self.channel_name
            )
            protocol = self.scope.get('subprotocols')
            if protocol:
                await self.accept(subprotocol=protocol[0])
            else:
                await self.accept()
        
    async def disconnect(self, close_code):
        if self.user and self.user.is_authenticated:
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name
            )
        
    async def send_update(self, event):
        print(event)
        await self.send(text_data=json.dumps(event['data']))