var notifications = [];
var newNotifications = [];
var isHidden = false;
const container = $('.notifications__list');

function requestNotifications() {
  var getNotifications = fetchData ('/api/v0.1/notifications/', 'GET');

  $.when(getNotifications).then(function(response) {
    var loadTmp = true;

    if (response.length !== notifications.length) {
      newNotifications = newData(response, notifications);

      newNotifications.forEach(element => {
        notifications.push(element);
      });
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

  container.prepend(tmp);
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

requestNotifications();

var intervalNotifications = window.setInterval(requestNotifications, 5000);
