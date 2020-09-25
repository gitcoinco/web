(function($) {

    var roomName = document.game_config['room_name'];

    var chatSocket = new WebSocket(
        'ws://' + window.location.host +
        '/ws/chat/' + roomName + '/');

    chatSocket.onmessage = function(e) {
        console.log(e);
        var data = JSON.parse(e.data);
        var message = data['message'];
        var user = data['user'];
        var insert_me = user + ":" + message;
        document.querySelector('#chat-log').value += (insert_me + '\n');
    };

    chatSocket.onclose = function(e) {
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
        chatSocket.send(JSON.stringify({
            'message': message
        }));

        messageInputDom.value = '';
    };

    // jitsi
    const domain = 'meet.jit.si';
    const options = {
        roomName: roomName,
        width: 700,
        height: 400,
        displayName: document.contxt['github_handle'],
        avatarUrl: '/dynamic/avatar/' + document.contxt['github_handle'],
        parentNode: document.querySelector('#meet')
    };
    const api = new JitsiMeetExternalAPI(domain, options);
    api.executeCommand('toggleAudio'); // default off
    api.executeCommand('toggleVideo'); // default off


})(jQuery);
