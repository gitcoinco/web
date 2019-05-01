from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
import json

from dashboard.models import ProfileSerializer, Profile
from experts.models import ExpertSession


USER_CHANNEL_NAME = 'user_{}'

class ExpertSessionConsumer(WebsocketConsumer):
    group_name = None

    def connect(self):
        session = ExpertSession.objects.get(pk=self.scope['url_route']['kwargs']['session_id'])
        self.accept()
        profile = Profile.objects.get(user=self.scope['user'])

        async_to_sync(self.channel_layer.group_add)(
            session.channel_group_name,
            self.channel_name
        )
        async_to_sync(self.channel_layer.group_add)(
            USER_CHANNEL_NAME.format(profile.handle),
            self.channel_name
        )

    def _send_action(self, action_type, data):
        self.send(text_data=json.dumps({
            'type': action_type,
            'data': data
        }))

    def disconnect(self, close_code):
        pass

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        self.send(text_data=json.dumps({
            'message': message
        }))

    def send_group_action(self, event):
        # Called when sending a message via the channel layer
        self._send_action(event['action_type'], event['data'])
