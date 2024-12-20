import json
from channels.generic.websocket import AsyncWebsocketConsumer
from ..schema import schema

class MainConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope.get('user')
        if not self.user:
            await self.close()
        else:
            self.user = await self.user
            if not self.user.is_authenticated:
                await self.close()
            else:
                self.group_name = f'user_{self.user.username}'
                await self.channel_layer.group_add(
                    self.group_name,
                    self.channel_name
                )
                protocols = self.scope.get('subprotocols')
                await self.accept(subprotocol=protocols[0])
            
    async def disconnect(self, close_code):
        if self.user and self.user.is_authenticated:
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name
            )
        else:
            await self.close(close_code)
        
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_type = text_data_json.get('type')
        
        if message_type == 'connection_init':
            await self.send(text_data=json.dumps({'type': 'connection_ack'}))
        elif message_type == 'subscribe':
            subscription_id = text_data_json.get('id')
            query = text_data_json.get('payload').get('query')
            variables = text_data_json.get('payload').get('variables')
            result = self.execute_query(query, variables)
            async for item in result:
                await self.send(text_data=json.dumps({
                    'type': 'next',
                    'id': subscription_id,
                    'payload': item.data
                }))

        elif message_type == 'disconnect':
            await self.send(text_data=json.dumps({'type': 'complete', 'id': text_data_json.get('id')}))
            await self.close()
            
    async def execute_query(self, query, variables):
        result = await schema.subscribe(query, variables, context_value={'user': self.user})
        async for item in result:
            yield item
            
    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'type': 'next',
            'message': event['message'],
            'chat_id': event['chat_id']
        }))
        print('Message sent from consumer')
        print(f'From consumer: {self.group_name}')
    