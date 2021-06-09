document.addEventListener('DOMContentLoaded', function() {

  console.debug('DIPLOMACY ROOM');

  // copy room link to clipboard
  const room_link = document.getElementById('room_link');
  const room_link_button = document.getElementById('room_link_button');

  room_link_button.addEventListener('click', () => {
    room_link.select();
    document.execCommand('copy');
    flashMessage('copied to clipboard', 10000);
  });


  // delete room UI
  // show delete button + warning on enter the room name what is fetched
  // by data-attribute data-roomname
  const delete_room = document.getElementById('delete_room');
  const delete_room_button = document.getElementById('delete_room_button');
  const delete_room_interface = document.getElementById('delete_room_interface');
  const roomname = delete_room.dataset.roomname;

  delete_room.addEventListener('input', () => {
    if (delete_room.value == roomname) {
      delete_room_button.classList.remove('disabled');
      delete_room_interface.classList.add('warning');
    } else {
      delete_room_button.classList.add('disabled');
      delete_room_interface.classList.remove('warning');
    }
  });


  // leave room UI
  // show leave button + warning on enter the room name what is fetched
  // by data-attribute data-phrase
  const leave_room = document.getElementById('leave_room');
  const leave_room_button = document.getElementById('leave_room_button');
  const leave_room_interface = document.getElementById('leave_room_interface');
  const phrase = leave_room.dataset.phrase;

  leave_room.addEventListener('input', () => {
    if (leave_room.value == phrase) {
      leave_room_button.classList.remove('disabled');
      leave_room_interface.classList.add('warning');
    } else {
      leave_room_button.classList.add('disabled');
      leave_room_interface.classList.remove('warning');
    }
  });

  
});

