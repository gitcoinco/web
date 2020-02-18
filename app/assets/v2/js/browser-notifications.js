const notificationsToggle= $('#browserNotifications');
const notificationsState = Notification.permission;


const checkBrowserNotifications = (state) => {
  if (state == 'denied') {
    notificationsToggle.prop('checked', false);
    notificationsToggle.attr('disabled', true);
    $('#browserNotificationsFeedback').html('<small>You can enable notifications manually on your browser interface.</small>');
  } else if (state == 'granted') {
    notificationsToggle.prop('checked', true);
    notificationsToggle.attr('disabled', true);
    $('#browserNotificationsFeedback').html('<small>You can disable notifications on your browser interface.</small>');
  } else {
    notificationsToggle.prop('checked', false);
  }
}

checkBrowserNotifications(notificationsState)

notificationsToggle.on('change', function(){
  Notification.requestPermission().then(permissionCallback);
})


const permissionCallback = (response) =>  {
  if (response == 'granted') {
    spawnNotification('Notifications enabled', 'Now you will receive notifiactions from Gitcoin');
  }
  checkBrowserNotifications(response);
}


function spawnNotification(
  theTitle,
  theBody,
  url,
  theIcon='/static/v2/images/helmet_front.png',
  timeOut=5000) {
  var options = {
      body: theBody,
      icon: theIcon,
      requireInteraction: true,
  }
  var notification = new Notification(theTitle, options, { tag: 'message1' });

  if (timeOut) {
    setTimeout(notification.close.bind(notification), timeOut);
  }
  notification.onclick = (e) => {
    e.preventDefault();
    window.focus();
    if (url) {
      location.href = url;
    }
    notification.close();
  }
}
