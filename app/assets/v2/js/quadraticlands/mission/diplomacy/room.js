document.addEventListener('DOMContentLoaded', function() {

  document.scroll_roomlog = function(){
    $(".diplomacy-roomlog .entries").animate({ scrollTop: $('.diplomacy-roomlog  .entries').prop("scrollHeight")}, 1000);
  }
  document.refresh_page = function(url){
      $.get(url, function(response){
        $(document).find('.entries').replaceWith($(response).find('.entries'))
        document.scroll_roomlog();
        $('#chat_room').focus();
      })
  }
  document.scroll_roomlog();

  console.debug('DIPLOMACY ROOM');

  // random floor polygones coloring on diplomacy image
  polygones = document.querySelectorAll('svg #hero polygon, svg #hero path');
  polygones.forEach(p => {
    p.setAttribute('data-kinetics-attraction', '');
    p.setAttribute('data-kinetics-attraction-chance', getRandomFloat(0.3, 1));
    p.setAttribute('data-kinetics-attraction-force', getRandomFloat(.7, 1.3));
    p.setAttribute('data-kinetics-attraction-grow', getRandomInt(1, 4));
    p.setAttribute('data-tone-click-random', '');
    p.style.cursor = 'pointer';
  });

  initToneJs();

  window.kinetics = new Kinetics();
  window.kinetics.interactionHook(); 
  

  // ROOM CREATED NOTIFICATION + PARTICLE FANYNESS
  const notification_room_created = document.getElementById('notification_room_created');
  if (notification_room_created)
  {
    console.log("ROOM CREATED");
    flashMessage('Room successfull created', 7000);

    // special particle fx
    window.kinetics.set({
      particles: {
        sizes: { min: 200, max: 400 }, rotate: { speed: 5 },
        mode:{ type: "party", speed: 40, boundery:"endless"}
      }
    });

     // reset to normal after 7 seconds
    setTimeout(function() {
      window.kinetics.set({
        particles: {
          sizes: { min: 5, max: 20 }, rotate: { speed: 1.5 },
          mode:{ type: "space", speed: 2, boundery:"endless"}
        }
      });      
    }, 7000);
  }


  last = 0;

  console.debug('ANIMATE DIPLOMACY');
  animate_diplomacy();


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
        alert("Message submitted");
        document.refresh_page(url);
      },
      error: function(error){
        alert('got an error - pls contact support@gitcoin.co');
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
      alert("Vote submitted")
      document.refresh_page(url);
    $('html, body').animate({
        scrollTop: $("#chat_room_interface").offset().top
     }, 500);
    },
    error: function(error){
      alert('got an error - pls contact support@gitcoin.co');
    },
    dataType: 'json'
  });

}


// animations for hero
function animate_diplomacy(now) {

  if (!last || now - last >= 60) {

    // pick a random poly from hero-about.svg
    // to randomly color up with a little animation
    polygone = polygones[Math.floor(Math.random() * polygones.length)];
    polygone.animate({ fill: [ '#9760FF', '#FA72AF', '#7AFFF7', '#9760FF' ] },
      {
        duration: 500, delay: 0, iterations: 1
      });

    last = now;
  }

  requestAnimationFrame(animate_diplomacy);
}

