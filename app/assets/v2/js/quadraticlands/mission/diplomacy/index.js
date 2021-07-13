document.addEventListener('DOMContentLoaded', function() {

  // create hyperlinks to rooms
  rooms = document.querySelectorAll('[data-roomlink]');
  rooms.forEach((room) => {
    room.addEventListener('click', () => {
      window.location.href = room.dataset.roomlink;
    });
  });

  // show submit button on user input of create room input field
  const create_room = document.getElementById('create_room');
  const create_room_button = document.getElementById('create_room_button');

  create_room.addEventListener('input', () => {
    if (create_room.value == '') {
      create_room_button.classList.add('disabled');
    } else {
      create_room_button.classList.remove('disabled');
    }
  });
});
