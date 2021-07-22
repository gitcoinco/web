// checks if user accepted the cookie law
document.addEventListener('DOMContentLoaded', function() {
  const cookielawbutton = document.getElementById('cookielawbutton');

  if (cookielawbutton) {
    cookielawbutton.addEventListener('click', () => {
      createCookieLaw();
    });
    checkCookieLaw();
  }
});

// creates a cookie with name "cookielaw_accepted"
// what expires in 365 days
function createCookieLaw() {
  const now = new Date();
  var duedate = new Date(now);

  duedate.setDate(now.getDate() + 356);
  const expires = duedate.toGMTString();

  document.cookie = `cookielaw_accepted=1; expires=${expires}; path=/`;
  console.debug('COOKIELAW : Set');
  checkCookieLaw();
}

// checks cookie with name "cookielaw_accepted"
// if no cookie - showCookieLaw()
function checkCookieLaw() {
  const name = 'cookielaw_accepted';
  const match = document.cookie.match(new RegExp('(^| )' + name + '=([^;]+)'));

  if (!match) {
    showCookieLaw();
    console.debug('COOKIELAW : Cookie Not Found');
  } else {
    cookielaw.classList.add('hide');
    console.debug('COOKIELAW : Found');
  }
}

// show the cookie law banner
function showCookieLaw() {
  const cookielaw = document.getElementById('cookielaw');

  cookielaw.classList.remove('hide');
}
