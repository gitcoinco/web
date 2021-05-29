(function($) {

    var roomName = document.game_config['pk'];

    document.chatSocket = new WebSocket(
        'ws://' + window.location.host +
        '/ws/chat/' + roomName + '/');

    document.chatSocket.onmessage = function(e) {
        var data = JSON.parse(e.data);
        if(data['type'] == 'msg'){
            var message = data['message'];
            var insert_me = message;
            document.querySelector('#chat-log').value += (insert_me + '\n');
        }
        if(data['type'] == 'play_move'){
            var where = data['where'];
            var i = where[0];
            var j = where[1];
            var new_vote = data['new_vote'];
            $(`input[data-i=${i}][data-j=${j}]`).val(new_vote);
        }
    };

    document.chatSocket.onclose = function(e) {
        console.log(e)
        console.error('Chat socket closed unexpectedly');
    };

    document.querySelector('#chat-message-input').focus();
    document.querySelector('#chat-message-input').onkeyup = function(e) {
        if (e.keyCode === 13) {  // enter, return
            document.querySelector('#chat-message-submit').click();
        }
    };

    document.querySelector('#chat-message-submit').onclick = function(e) {
        var messageInputDom = document.querySelector('#chat-message-input');
        var message = messageInputDom.value;
        document.chatSocket.send(JSON.stringify({
            'message': message,
            'type': 'message',
            'pk': document.game_config['pk'],
            'from': document.contxt['github_handle'],
        }));

        messageInputDom.value = '';
    };



})(jQuery);
