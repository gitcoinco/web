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
    var flag = compareJson(response, notifications)
    if (flag === false) {
      console.log('updating')
      console.log(notifications, response)
      notifications = response;
      templateSuggestions(response)
    }
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
        <div>
          ${notify.message_html}
        </div>
        <time class="notifications__time" datetime="${notify.created_on}" title="${notify.created_on}">
          ${notify.created_on}
        </time>
      </li>`
    ).join(' ')}
  `;

  container.html(tmp);
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

requestNotifications()

var intervalNotifications = window.setInterval(requestNotifications, 5000);
