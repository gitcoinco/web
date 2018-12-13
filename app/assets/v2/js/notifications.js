// var notifications = [];
var newNotifications = [];
var isHidden = false;
var page = 1;
const container = $('.notifications__list');

const onChange = (objToWatch, onChangeFunction) => {
  const handler = {
    get(target, property, receiver) {
      onChangeFunction(property); // Calling our function
      return Reflect.get(target, property, receiver);
    },
    set(target, property, value, receiver) {
      onChangeFunction('this', property);
      return Reflect.set(target, property, value);
    }
  };
return new Proxy(objToWatch, handler);
};

const logger = (value) => console.log();

const notifications = onChange(newNotifications, logger)


function requestNotifications() {
  console.log('REQUEST', page)
  var getNotifications = fetchData (`/api/v0.1/notifications/?page=${page}`, 'GET');

  $.when(getNotifications).then(function(response) {
    // var loadTmp = response.data.length && response.data[0].id !== notifications[0].id;
    // var loadTmp = response.data.length !== notifications.length
    // console.log(response.data[0].id)
    // if (response.data.length !== notifications.length) {
    // if (loadTmp) {

      // page = response.has_next ? page+1 : page = 1
      if (response.has_next) {
        page = ++page
        console.log('PAGE', page)
      } else {
        page = 1
      }
      console.log(page)

      newNotifications = newData(response.data, notifications);
      newNotifications.forEach(element => {
        notifications.push(element);
      });

      toggleRead(newNotifications)

      setDot(true, notifications);
      templateSuggestions(newNotifications, page);
    // }

  });
}

function templateSuggestions(notifications, page) {
  var tmp = `
    ${notifications.map((notify, index) => `
      <li class="notifications__item">
        <span class="notifications__item-readed">
          <b class="notification__dot-small ${notify.is_read ? '' : 'notification__dot-small_active' }"></b>
        </span>
        <a href="${notify.CTA_URL}" class="notifications_content" data-notification="${notify.id}">
          <img class="notifications__avatar" src="/dynamic/avatar/${notify.username}" width="28" height="28">
          <p class="line-clamp">
          	${notify.message_html}
          </p>
        </a>
        <time class="notifications__time" datetime="${notify.created_on}" title="${notify.created_on}">
          ${moment.utc(notify.created_on).fromNow()}
        </time>
      </li>`
    ).join(' ')}`;

    console.log('template' , page)
  if (page === 1) {
    container.append(tmp);
  } else {
    container.prepend(tmp);
  }
}

function checkTabHidden() {
  if (typeof document.hidden !== 'undefined') {
    isHidden = document.hidden;

  } else {
    isHidden = false;
  }
  return isHidden;
}

function newData(newObj, oldObj) {

  return newObj.filter(function(obj) {
    return !oldObj.some(function(obj2) {
      return obj.id == obj2.id;
    });
  });
}

moment.updateLocale('en', {
  relativeTime: {
    future: 'in %s',
    past: '%s ',
    s: 'now',
    ss: '%ds',
    m: '1m',
    mm: '%d m',
    h: '1h',
    hh: '%dh',
    d: '1 day',
    dd: '%d days',
    M: '1 month',
    MM: '%d months',
    y: '1 year',
    yy: '%d years'
  }
});

function setDot(hasNewData, dataNotify) {
  let dataNotifyCount = dataNotify.length
  $('#total-notifications').text(dataNotifyCount);
  if (dataNotifyCount == 0) {
    $('notifications__no-results').removeClass('d-none');
  } else {
    $('notifications__no-results').addClass('d-none');
  }

  let hasUnread = dataNotify.find(o => o.is_read === false);

  if (hasUnread != undefined ) {
    $('#notification-dot').addClass('notification__dot_active');
  } else {
    $('#notification-dot').removeClass('notification__dot_active');
  }
}

function toggleRead(notificationToRead, unread) {
  // console.log(notificationToRead)
  let notificationRead = sessionStorage.getItem('notificationRead')
  notificationRead && notificationRead.length ? notificationRead = notificationRead.split(',').map(String) : notificationRead;
  // console.log(notificationRead)

  if (notificationRead) {
    // console.log('ping')
    sessionStorage.removeItem('notificationRead');
    // console.log('api request readed', notificationRead);
    if (unread) {
      const unread = Object()
      unread["unread"] = notificationRead
      let data = JSON.stringify(unread);
      var putRead = fetchData (`api/v0.1/notifications/unread/`, 'PUT', data);

    } else {
      const read = Object()
      read["read"] = notificationRead
      let data = JSON.stringify(read);
      var putRead = fetchData (`api/v0.1/notifications/read/`, 'PUT', data);
    }

    $.when(putRead).then(function(response) {
      console.log(response)
    })

    // notificationRead = parseInt(notificationRead)

    // const index = notificationToRead.findIndex(item => {
    //   return item.id === notificationRead
    // })
    // notificationToRead[index].is_read = true;


    notificationRead.forEach(function(itema) {
      let notify = Number(itema)
      const index = notificationToRead.findIndex(function(item, index) {
          return item.id == notify
      });
      console.log(index)
      if (unread) {
        // notificationToRead[index].is_read = false;


      } else {
        // console.log('index',index)
        if (notificationToRead.length) {
          console.log(notificationToRead)
          notificationToRead[index].is_read = true;
        }
      }

    })


    // notificationRead.forEach(function(item) {
    //   let notify = parseInt(item)
    //   const index = notificationRead.findIndex(item => {
    //     return item.id === notify
    //   })
    //   console.log( 'thist is the index', index)
    //   if (unread) {
    //     notificationToRead[index].is_read = false;
    //   } else {
    //     notificationToRead[index].is_read = true;
    //   }

    // })



    // getAllIndexes(notificationToRead)
    // function getAllIndexes(arr, val) {
    //   var indexes = [], i;
    //   for(i = 0; i < arr.length; i++)
    //       if (arr[i].id === val)
    //       arr[i].is_read = true;
    //           // indexes.push(i);
    //   return indexes;
    // }
  }
}


requestNotifications();

// var intervalNotifications = window.setInterval(requestNotifications, 10000);

$(document).ready(function() {
  const notificationsBox = $('.notifications__box')

  notificationsBox.on('click', '[data-notification]', function(e){
    window.sessionStorage.setItem('notificationRead', e.currentTarget.dataset.notification);
  })

  notificationsBox.on('click', '#read-all', function(e){
    e.preventDefault();

    var toRead = Array.from(notifications, item => item.id)

    $('.notification__dot-small').removeClass('notification__dot-small_active')
    // notifications.map((notify, index) => {
    //   notify.is_read = true;

    // })

    // console.log(toRead)
    window.sessionStorage.setItem('notificationRead', toRead);
    requestNotifications();
  })

  $('.notification__icon').on('click', function(e){
    if($('.notifications__box').hasClass('show')){
      page = 1
      requestNotifications();
    }
  })

})

$('.notifications__list').scroll( function() {
  console.log(page)
  const scrollContainer = $(this)[0]
  if (scrollContainer.scrollTop + scrollContainer.clientHeight >= scrollContainer.scrollHeight) {
    requestNotifications();
  }
});






