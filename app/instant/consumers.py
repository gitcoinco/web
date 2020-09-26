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

    def chat_message(self, text_data_json):
        # setup
        text_data_json = json.loads(text_data_json['text'])
        pk = text_data_json['pk']
        _type = text_data_json['type']
        _from = text_data_json['from']
        
        ## find game
        from governance.models import Game
        game = Game.objects.get(pk=pk)

        ## auth
        authd = _from == self.scope["user"].username

        ## handle messages
        msg = None
        if _type == 'message':
            message = text_data_json['message']
            if authd:
                msg = game.message(self.scope["user"].username, message)
            else:
                msg = game.feed.filter(sender__handle=_from).order_by('-created_on').first()
        if _type == 'play_move':
            i = int(text_data_json['i'])
            j = int(text_data_json['j'])
            new_vote = float(text_data_json['new_vote'])
            msg = game.play_move(self.scope["user"].username, i, j, new_vote)
            game.save()
            self.send(text_data=json.dumps({
                'type': 'play_move',
                'where': [i, j],
                'new_vote': new_vote,
            }))
        if _type == 'add_player':
            msg = game.add_player(self.scope["user"].username)

        if msg:
            self.send(text_data=json.dumps({
                'type': 'msg',
                'message': msg.message,
            }))

    def receive(self, text_data):
        async_to_sync(self.channel_layer.group_send)(
            "chat",
            {
                'type': 'chat.message',
                "text": text_data,
            },
        )
