var notifications = []
const isHidden = false
const container = $('.notifications__list')

function requestNotifications() {
  var getNotifications = fetchData ('/notification/','GET')

  $.when( getNotifications ).then(function(response) {

    // if (notifications.length) {
    //   newNotifications = filterNewData(response);
    // } else {
      // }
    // newNotifications = response;
    // console.log(newNotifications)
    // var flag = compareJson(response, notifications)
    // if (flag === false) {



      console.log('updating')

      response.forEach(element => {
        notifications.push(element)
      });
      // notifications.push(response);
      // notifications = notifications.filter( function( elem, i, array ) {
      //   console.log( elem, i, array )
      //         return array.indexOf( elem ) === i;
      //       } );

      // notifications = getDistinctArray(notifications)

      notifications = notifications.filter((notification, index, self) =>
        index === self.findIndex((t) => (
          t.id === notification.id
        ))
      )
      console.log(notifications)
      setDot(true, notifications)
      templateSuggestions(notifications)
    // }
    // return response
  })
}

function templateSuggestions(notifications) {
  var tmp = `
    ${notifications.map((notify, index) => `
      <li class="notifications__item">
        <span class="notifications__item-readed">
          <b class="notification__dot-small"></b>
        </span>
        <a href="${notify.CTA_URL}" class="notifications_content">
          <img class="notifications__avatar" src="/dynamic/avatar/${notify.username}" width="24">
          <p>
          	${notify.message_html}
          </p>
        </a>
        <time class="notifications__time" datetime="${notify.created_on}" title="${notify.created_on}">
          ${moment.utc(notify.created_on).fromNow()}
        </time>
      </li>`
    ).join(' ')}
  `;

  container.prepend(tmp);
}

function checkHidden() {
  if (typeof document.hidden !== "undefined") {
    return isHidden = document.hidden
  } else {
    return isHidden = false
  }
}

function filterNewData(data) {

  return notifications.filter(
    function(item) {

      return data.indexOf(item) < 0;
    }
  );
}



function getDistinctArray(arr) {
  var dups = {};
  return arr.filter(function(el) {
      var hash = el.valueOf();
      var isDup = dups[hash];
      dups[hash] = true;
      return !isDup;
  });
}

function compareJson(obj1, obj2) {
  var flag = true
  if (Object.keys(obj1).length==Object.keys(obj2).length){
      for(key in obj1) {
          if(obj1[key] == obj2[key]) {
              continue;
          }
          else {
              return flag=false;
              break;
          }
      }
  }
  else {
    return flag=false;
  }
}




moment.updateLocale('en', {
  relativeTime : {
      future: "in %s",
      past: "%s ",
      s  : 'now',
      ss : '%ds',
      m: "1m",
      mm: "%d m",
      h: "1h",
      hh: "%dh",
      d: "1 day",
      dd: "%d days",
      M: "1 month",
      MM: "%d months",
      y: "1 year",
      yy: "%d years"
  }
});

function setDot(newData, notifications) {
  $('#total-notifications').text(notifications.length)
  if (newData) {
    $('#notification-dot').addClass('notification__dot-active')
  } else {
    $('#notification-dot').removeClass('notification__dot-active')
  }
}

requestNotifications()

var intervalNotifications = window.setInterval(requestNotifications, 5000);
