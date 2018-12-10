var notifications = [];
var newNotifications = [];
var isHidden = false;
var page = 1;
const container = $('.notifications__list');

function requestNotifications() {
  console.log(page)
  var getNotifications = fetchData (`/api/v0.1/notifications/?page=${page}`, 'GET');

  $.when(getNotifications).then(function(response) {
    // var loadTmp = response.data.length && response.data[0].id !== notifications[0].id;
    var loadTmp = response.data.length !== notifications.length
    // console.log(response.data[0].id)
    // if (response.data.length !== notifications.length) {
    if (loadTmp) {
      newNotifications = newData(response.data, notifications);

      page = response.has_next ? page+1 : page = 1
      console.log(page)

      newNotifications.forEach(element => {
        notifications.push(element);
      });

      markAsRead(newNotifications)

      setDot(true, notifications);
      templateSuggestions(newNotifications);
    }

  });
}

function templateSuggestions(notifications) {
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
      </li>`).join(' ')}`;

  // if (newItems) {
    container.prepend(tmp);
  // } else {
    // container.append(tmp);
  // }
  $('.notifications__item');
}

function checkHidden() {
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

function setDot(hasNewData, newNotifications) {
  $('#total-notifications').text(newNotifications.length);

  if (hasNewData) {
    $('#notification-dot').addClass('notification__dot_active');
  } else {
    $('#notification-dot').removeClass('notification__dot_active');
  }
}

function markAsRead(notificationToRead) {
  console.log(notificationToRead)
  var notificationRead = parseInt(sessionStorage.getItem('notificationRead'))

  if (notificationRead) {
    console.log('ping')
    sessionStorage.removeItem('notificationRead');
    console.log('api request readed', notificationRead);
    let data = JSON.stringify({'read':[notificationRead]});
    var putRead = fetchData (`api/v0.1/notifications/read/`, 'PUT', data);
    $.when(putRead).then(function(response) {
      console.log(response)
    })

    // notificationRead = parseInt(notificationRead)

    const index = notificationToRead.findIndex(item => {
      return item.id === notificationRead
    })
    notificationToRead[index].is_read = true;
  }
}

requestNotifications();

var intervalNotifications = window.setInterval(requestNotifications, 10000);

$(document).ready(function() {

  $('.notifications__box').on('click', '[data-notification]', function(e){
    window.sessionStorage.setItem('notificationRead', e.currentTarget.dataset.notification);
  })

})

$('.notifications__list').scroll( function() {
  console.log($(this)[0])
  const scrollContainer = $(this)[0]
  if (scrollContainer.scrollTop + scrollContainer.clientHeight >= scrollContainer.scrollHeight) {
    requestNotifications(page);
  }
});



var array = [];
var observedArray = new Proxy(notifications, {
    set: function (target, propertyKey, value, receiver) {
        console.log(propertyKey+'='+value);
        console.log(target,propertyKey, value )
        target[propertyKey] = value;
        return true
    }
});

