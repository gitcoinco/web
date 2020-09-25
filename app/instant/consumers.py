from channels.generic.websocket import WebsocketConsumer
import json
import random
from instant.models import Clients
from asgiref.sync import async_to_sync

class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.user = self.scope["user"]
        self.scope["session"]["seed"] = random.randint(1, 1000)
        Clients.objects.create(
            channel_name=self.channel_name,
            user=self.user)
        self.accept()
        async_to_sync(self.channel_layer.group_add)("chat", self.channel_name)


    def disconnect(self, close_code):
        Clients.objects.filter(channel_name=self.channel_name).delete()
        async_to_sync(self.channel_layer.group_discard)("chat", self.channel_name)
        pass

    def chat_message(self, text_data):
        return self.receive(json.dumps(text_data))

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        self.send(text_data=json.dumps({
            'message': message,
            'user': self.scope["user"].username,
        }))