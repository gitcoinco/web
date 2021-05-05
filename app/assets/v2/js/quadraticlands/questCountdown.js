// QUIZ TIMER
// define these constants
// const maxTime = 15;
// const expiryLink = "mission-proofofknowledge-quest1-wrong";
// then run this script by embed as script ...

time = maxTime;
const timeleft = document.getElementById('timeleft');
const progressbar = document.getElementById('progressbar');

questInterval = setInterval(function() {
  time--;
  timeleft.innerHTML = time + 's';
  timePercent = (100 * time) / maxTime;
  progressbar.style.width = timePercent + '%';

  if (time <= 10) {
    progressbar.classList.add('halftime');
  }

  if (time <= 4) {
    progressbar.classList.add('hurryup');
  }

  if (time <= 0) {
    clearInterval(questInterval);
    window.location = expiryLink; // goto wrong page
  }
}, 1000);
