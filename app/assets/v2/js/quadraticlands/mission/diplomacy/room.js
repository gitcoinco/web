document.addEventListener('DOMContentLoaded', function() {

  console.debug('DIPLOMACY ROOM');

  // show and hide arrownav when #trollbox is / is not in visible area
  const arrownav = document.getElementById('arrownav');
  var observer = new IntersectionObserver(function(entries) {
    if(entries[0].isIntersecting === true)
      arrownav.classList.remove("hide");
    else
      arrownav.classList.add("hide");
  }, { threshold: [0] });
  observer.observe(document.querySelector("#trollbox"));


  // 
  //
  document.refresh_page = function(url){
    var keys = [/*'.diplomacy-room-members', '.diplomacyvouchebar', */'.entries']
    $.get(url, function(response){
      for(var i=0; i<keys.length; i++){
        let key = keys[i];
        console.log(key, $(response).length, $(response).find(key).html());
        debugger;
        $(key).replaceWith($(response).find(key));
      }
    })
  }


  // ROOM CREATED NOTIFICATION + PARTICLE FANYNESS
  const notification_room_created = document.getElementById('notification_room_created');
  if (notification_room_created)
  {
    console.log("ROOM CREATED");
    flashMessage('Room successfull created', 7000);
  }
  

  //member card toggle card front back - but not on click in the input field on front card
  const membercards = document.querySelectorAll('.member-card');
  membercards.forEach(card => {
    card.addEventListener('click', (event) => {
      if (event.target.tagName != "INPUT") {
        card.classList.toggle("flip");
      }
    });    
  });


  //fetch balance of users wallet + display it
  const diplomacy_wallet_address = document.getElementById('wallet_address');
  const diplomacy_wallet_balance = document.getElementById('wallet_token_balance');
  document.addEventListener('dataWalletReady', diplomacyWallet);


  //fetch diplomacy_wallet_available from dom (comes from database)
  const used = document.getElementById('diplomacy_wallet_used');
  window.used = used.dataset.used;
  console.debug("USED", window.used)


  // copy room link to clipboard
  const room_link = document.getElementById('room_link');
  const room_link_button = document.getElementById('room_link_button');
  if(room_link){
    room_link_button.addEventListener('click', () => {
      room_link.select();
      document.execCommand('copy');
      flashMessage('copied to clipboard', 10000);
    });
  }


  // no self deleegation
  $('.front input').click(function(){
    if($(this).data('username') == document.contxt['github_handle']){
      flashMessage('Cannot vouch for  self', 1000);
    }
  })


  // delete room UI
  // show delete button + warning on enter the room name what is fetched
  // by data-attribute data-roomname
  const delete_room = document.getElementById('delete_room');
  const delete_room_button = document.getElementById('delete_room_button');
  const delete_room_interface = document.getElementById('delete_room_interface');
  if(delete_room){  
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
  }


  // leave room UI
  // show leave button + warning on enter the room name what is fetched
  // by data-attribute data-phrase
  const leave_room = document.getElementById('leave_room');
  if(leave_room){
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

  }


  // vouche button trigger function vouche()
  //
  const vouche_button = document.getElementById('vouche_button');
  vouche_button.addEventListener('click', () => {
    vouche();
  });

  $("body").on('submit', '.diplomacy-chat-form', function(e){
    e.preventDefault();
    let params = {
      csrfmiddlewaretoken: $('[name=csrfmiddlewaretoken]').val(),
      chat: $("#chat_room").val(),
    }
    $('#chat_room').val('');
    var url = $("#diplomacy-chat-form").attr('action');
    $.ajax({
      type: "POST",
      url: url,
      data: params,
      success: function(response){
        flashMessage("Message submitted", 2000);
        document.refresh_page(url);
      },
      error: function(error){
        flashMessage('got an error - pls contact support@gitcoin.co', 5000);
      },
    });  
  });


  // vouche bar validations
  inputs = document.querySelectorAll('.member-card .front input');
  console.debug(inputs)
  inputs.forEach(i => {
    i.addEventListener('input', input => {
      if (i.value < 0) {
        i.value = 0;
      }

      updateVoucheBar();

      console.debug("USED", window.used)
      console.debug("USE", window.use)
      console.debug("AWAILABLE", (window.walletbalance - window.used) )

      if (window.use > (window.walletbalance - window.used) )
      {
        console.debug("you can not use so much gtc");
        i.value = 0;
        updateVoucheBar();
      }

    });
  });

});


function updateVoucheBar(){

  window.use = 0;
  inputs = document.querySelectorAll('.member-card .front input');

  inputs.forEach(i => {
    if (i.value > 0) {
      window.use += Number(i.value);
    }
  });

  diplomacy_wallet_use = document.getElementById('diplomacy_wallet_use');
  diplomacy_wallet_use.innerHTML = window.use;

  diplomacy_wallet_available = document.getElementById('diplomacy_wallet_available');
  diplomacy_wallet_available.innerHTML = window.walletbalance - window.used;
  console.debug("updateVouceBar");

}


// fetch the gtc balance
async function diplomacyWallet(){
  console.debug("diplomacy wallet");
  try {

    let balance = await getTokenBalances(gtc_address());

    diplomacy_wallet_balance.innerHTML = balance.balance.toFixed(2);
    diplomacy_wallet_address.innerHTML = truncate(selectedAccount);
    window.walletbalance = balance.balance.toFixed(2);
    console.debug("walletbalance", window.walletbalance)

    // to calc available balance
    updateVoucheBar();

  } catch (e) {
    console.error(e);
  }
}


// reads all the members input fields and generate a nice
// array of objects to do a "sign" + a "safe to db"
// not sure how to do this part.

async function vouche() {

  console.debug('VOUCHE');

  // read all input fields what have data-member
  members = document.querySelectorAll('[data-member]');

  // define a result array
  const result = [];

  // push all vouche data of each member to the result
  members.forEach(member => {
    var entry = {
      userid: member.dataset.userid,
      username: member.dataset.username,
      value: member.value ? member.value : 0
    };

    result.push(entry);
  });

  // @kev : do something with the result ( sign, safe, whatever)
  // this is how far i could come. now your turn :)
  const accounts = await web3.eth.getAccounts();
  const account = accounts[0];
  const package = {
    'votes': result,
    'balance': balance,
    'account': account,
  }
  let signature = await web3.eth.personal.sign(JSON.stringify(package) , account);
  const diplomacy_wallet_balance = document.getElementById('wallet_token_balance');
  const params = {
    package: JSON.stringify(package),
    signature: signature,
    csrfmiddlewaretoken: $('[name=csrfmiddlewaretoken]').val(),
  }
  const url = document.location.href;
  $.ajax({
    type: "POST",
    url: url,
    data: params,
    success: function(response){
      flashMessage("Vote submitted", 2000)
      document.location.href= url;
    },
    error: function(error){
      flashMessage('got an error - pls contact support@gitcoin.co', 5000);
    },
    dataType: 'json'
  });

}


