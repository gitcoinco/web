const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

document.addEventListener('DOMContentLoaded', function() {
  if (mission) {
    // update user state
    var setMissionStatus = fetchData('/quadraticlands/set_mission_status', 'POST', { 'mission': mission }, { 'X-CSRFToken': csrftoken });

    $.when(setMissionStatus).then((response, status, statusCode) => {
      console.debug('Missions status set successfully', status);
    }).catch(error => {
      console.error('There was an issue setting missions status', error.message);
    });
  } else {
    console.error('No mission is set');
  }
});
