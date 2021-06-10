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

  // vouche button trigger function vouche()
  //
  const vouche_button = document.getElementById('vouche_button');

  vouche_button.addEventListener('click', () => {
    vouche();
  });

  // vouche bar validations
  inputs = document.querySelectorAll('.member input');
  inputs.forEach(i => {
    i.addEventListener('input', input => {
      if (i.value < 0) {
        i.value = 0;
      }
      updateVoucheBar();
    });
  });

});


function updateVoucheBar() {

  window.use = 0;

  inputs = document.querySelectorAll('.member input');
  inputs.forEach(i => {
    if (i.value > 0) {
      window.use += Number(i.value);
    }
  });

  diplomacy_wallet_use = document.getElementById('diplomacy_wallet_use');
  diplomacy_wallet_use.innerHTML = window.use;

}

function vouche() {

  console.debug('VOUCHE');

  // read all input fields what have data-member
  members = document.querySelectorAll('[data-member]');

  // define a result array
  const result = [];

  // push all vouche data of a member to the result
  members.forEach(member => {
    var entry = {
      userid: member.dataset.userid,
      username: member.dataset.username,
      value: member.value
    };

    result.push(entry);
  });

  // do something with the result ( sign, safe, whatever)
  console.log(result);

}