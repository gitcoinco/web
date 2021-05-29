/* eslint-disable no-loop-func */
/* eslint-disable no-console */
/* eslint-disable nonblock-statement-body-position */
$(document).ready(function() {

  $.fn.isInViewport = function() {
    var elementTop = $(this).offset().top;
    var elementBottom = elementTop + $(this).outerHeight();
    var viewportTop = $(window).scrollTop();
    var viewportBottom = viewportTop + $(window).height();

    return elementBottom > viewportTop && elementTop < viewportBottom;
  };

  if (typeof ($('body').tooltip) != 'undefined') {
    $('body').tooltip({
      items: ':not([data-toggle])'
    });
  }

  // TODO: MOVE TO GRANTS shared
  if (typeof CartData != 'undefined') {
    applyCartMenuStyles();
  }

  $('body').on('click', '.copy_me', function() {
    $(this).focus();
    $(this).select();
    document.execCommand('copy');
    $(this).after('<div class=after_copy>Copied to clipboard</div>');
    setTimeout(function() {
      $('.after_copy').remove();
    }, 500);
  });

  function getParam(parameterName) {
    var result = null;
    var tmp = [];

    location.search
      .substr(1)
      .split('&')
      .forEach(function(item) {
        tmp = item.split('=');
        if (tmp[0] === parameterName)
          result = decodeURIComponent(tmp[1]);
      });
    return result;
  }

  // makes the reflink sticky
  if (getParam('cb')) {
    var cb = getParam('cb');
    // only if user is not logged in tho

    if (cb.indexOf('ref') != -1 && !document.contxt.github_handle) {
      localStorage.setItem('cb', cb);
    }
  }

  // if there exists a sticky reflink but the user navigated away from the link in the course of logging in...
  if (localStorage.getItem('cb') && document.contxt.github_handle && !getParam('cb')) {
    var this_url = new URL(document.location.href);

    this_url.searchParams.append('cb', localStorage.getItem('cb'));
    this_url.search = this_url.search.replace('%3A', ':');
    localStorage.setItem('cb', '');
    document.location.href = this_url;
  }

  var force_no_www = function() {
    if (document.location.href.indexOf('https://www.gitcoin.co') != -1) {
      var new_url = document.location.href.replace('www.gitcoin.co', 'gitcoin.co');

      document.location.href = new_url;
    }
  };

  force_no_www();

  // Fix multiple modals at same time.
  $(document).on('show.bs.modal', '.modal', function(event) {
    let zIndex = 1040 + (10 * $('.modal:visible').length);

    $(this).css('z-index', zIndex);
    setTimeout(function() {
      $('.modal-backdrop').not('.modal-stack').css('z-index', zIndex - 1).addClass('modal-stack');
    }, 0);
  });


  var record_campaign_to_cookie = function() {
    var paramsStr = decodeURIComponent(window.location.search.substring(1));

    paramsStr.split('&')
      .map((paramStr) => {
        var [ key, value ] = paramStr.split('=');

        return {key, value};
      })
      .filter((param) => [ 'utm_medium', 'utm_source', 'utm_campaign' ].indexOf(param.key) !== -1)
      .forEach((campaign) => {
        Cookies.set(campaign.key, campaign.value);
      });
  };

  if (document.visitorId) {
    Cookies.set('visitorId', document.visitorId);
  }
  record_campaign_to_cookie();


  if (!$('.header > .minihero').length && $('.header > .navbar').length) {
    $('.header').css('overflow', 'visible');
  }

  // get started modal
  $("a[href='/get']").on('click', function(e) {
    e.preventDefault();
    var url = $(this).attr('href');

    setTimeout(function() {
      $.get(url, function(newHTML) {
        $(newHTML).appendTo('body').modal();
      });
    }, 300);
  });

  // bust the cache every time the user interacts with github
  $("[href^='/_github']").on('click', function(e) {
    var timestamp = Date.now() / 1000 | 0;

    Cookies.set('last_github_auth_mutation', timestamp);
  });

  if (!$.fn.collapse) {
    $('.navbar-toggler').on('click', function() {
      var toggle = $(this).attr('aria-expanded');

      $('.navbar-collapse').toggleClass('show');
      if (toggle === 'false') {
        $(this).attr('aria-expanded', 'true');
      } else {
        $(this).attr('aria-expanded', 'false');
      }

    });
  }

  // control display of #top_nav_notification
  var $top_nav_notif = $('#top_nav_notification');
  var top_nav_salt = document.nav_salt;
  var remove_top_row = function() {
    $top_nav_notif.parents('.row').remove();
    localStorage['top_nav_notification_remove_' + top_nav_salt] = true;
  };

  // display (if it holds a message and hasn't been closed) or remove #top_nav_notification
  if (top_nav_salt == 0 || localStorage['top_nav_notification_remove_' + top_nav_salt]) {
    remove_top_row();
  } else {
    $top_nav_notif.parents('.row').removeClass('d-none');
  }
  $top_nav_notif.click(remove_top_row);

  // pulse animation on click
  $('.pulseClick').on('click', (event) => {
    let element = $(event.target);

    element.addClass('pulseButton');
    let callback = () => {
      element.removeClass('pulseButton');
    };

    setTimeout(callback, 300);
  });

  // updates expiry timers with countdowns
  const setDataFormat = function(data) {
    let str = 'in ';

    if (data.months() > 0)
      str += data.months() + 'mon ';
    if (data.days() > 0)
      str += data.days() + 'd ';
    if (data.hours() > 0)
      str += data.hours() + 'h ';
    if (data.minutes() > 0)
      str += data.minutes() + 'm ';
    if (data.seconds() > 0)
      str += data.seconds() + 's ';

    return str;
  };

  const updateTimers = function() {
    let enterTime = moment();

    $('[data-time]').filter(':visible').each(function() {
      moment.locale('en');
      var time = $(this).data('time');
      var timeFuture = $(this).data('time-future');
      var timeDiff = moment(time).diff(enterTime, 'sec');

      if (timeFuture && (timeDiff < 0)) {
        $(this).html('now');
        $(this).parents('.offer_container').addClass('animate').removeClass('empty');
        $(this).removeAttr('data-time');

        // let btn = `<a class="btn btn-block btn-primary btn-sm mt-2" href="${timeUrl}">View Action</a>`;
        // return $(this).parent().next().html(btn);
        return $(this).parent().append('<div>Refresh to view offer!</div>');
      }

      const diffDuration = moment.duration(moment(time).diff(moment()));

      $(this).html(setDataFormat(diffDuration));
    });
  };

  setInterval(updateTimers, 1000);

  $('.faq_item .question').on('click', (event) => {
    $(event.target).parents('.faq_parent').find('.answer').toggleClass('hidden');
    $(event.target).parents('.faq_parent').find('.answer').toggleClass('show');
  });

  attach_close_button();
});


this.attach_close_button = function() {
  $('body').delegate('.alert .closebtn', 'click', function(e) {
    $(this).parents('.alert').remove();
    $('.alert').not('.alert-static').each(function(index) {
      if (index == 0) $(this).css('top', 0);
      else {
        let new_top = (index * 70) + 'px';

        $(this).css('top', new_top);
      }
    });
  });
};

this.closeButton = function(msg) {
  var html = (msg['closeButton'] === false ? '' : '<span class="closebtn" >&times;</span>');

  return html;
};

this.alertMessage = function(msg) {
  var html = `<strong>${typeof msg['title'] !== 'undefined' ? msg['title'] : ''}</strong>${msg['message']}`;

  return html;
};

this._alert = function(msg, _class, remove_after_ms) {
  if (typeof msg == 'string') {
    msg = {
      'message': msg
    };
  }
  var numAlertsAlready = $('body > .alert:visible').length;
  var top = numAlertsAlready * 70;
  var id = 'msg_' + parseInt(Math.random() * 10 ** 10);

  var html = function() {
    return (
      `<div id="${id}" class="alert alert-fixed bs-alert alert-${_class} d-flex justify-content-between align-items-center shadow-sm py-3 font-weight-semibold font-body" style="top: ${top}px">
        <div class="message">
          <div class="content">
            ${alertMessage(msg)}
          </div>
        </div>
        ${closeButton(msg)}
      </div>`
    );
  };

  $('body').append(html);

  $(document).keydown(function(e) {
    if (e.keyCode == 27) {
      $(`#${id}`).remove();
    }
  });

  if (typeof remove_after_ms != 'undefined') {
    setTimeout(function() {
      $('#' + id).remove();
    }, remove_after_ms);
  }

};

this.show_persona_modal = function(e) {
  const content = $.parseHTML(
    `<div id="persona_modal" class="modal fade" tabindex="-1" role="dialog" aria-hidden="true">
      <div class="modal-dialog">
        <div class="modal-content px-4 py-3">
          <div class="col-12">
            <button type="button" class="close" data-dismiss="modal" aria-label="Close">
              <span aria-hidden="true">&times;</span>
            </button>
          </div>
          <div class="col-12 pt-2 pb-2 text-center">
            <img src="${static_url}v2/images/modals/persona-choose.svg" width="160" height="137">
            <h2 class="font-title mt-4">${gettext('Are you a Funder or a Contributor?')}</h2>
          </div>
          <div class="col-12 pt-2 text-center">
            <p class="mb-0">${gettext('Let us know so we could optimize the <br>best experience for you!')}</p>
          </div>
          <div class="col-12 my-4 text-center">
            <button type="button" class="btn btn-primary px-5 mb-2 mx-2" data-persona="persona_is_funder">I'm a Funder</button>
            <button type="button" class="btn btn-primary px-5 mx-2" data-persona="persona_is_hunter">I'm a Contributor</button>
          </div>
        </div>
      </div>
    </div>`);

  $(content).appendTo('body');
  $('#persona_modal').bootstrapModal('show');
};

this.popOnboard = function(step) {
  if (step) {
    appOnboard.step = step;
  }
  appOnboard.$refs['onboard-modal'].openModal();
};

$('body').on('click', '[data-persona]', function(e) {
  sendPersonal($(this).data('persona'));
});

this.sendPersonal = (persona) => {
  let postPersona = fetchData('/api/v0.1/choose_persona/', 'POST',
    {persona, 'access_token': document.contxt.access_token}
  );

  $.when(postPersona).then((response, status, statusCode) => {
    if (statusCode.status != 200) {
      return _alert(response.msg, 'danger');
    }
    $('#persona_modal').bootstrapModal('hide');

    const urls = [
      {
        url: '/hackathon/onboard'
      },
      {
        url: '/profile'
      }
    ];

    const checkUrlRedirect = (arr, val) => {
      return arr.all(arrObj => {
        if (val.indexOf(arrObj.url) == -1) {
          return true;
        }
        return false;
      });
    };

    if (response.persona === 'persona_is_funder') {
      if (checkUrlRedirect(urls, document.location.href)) {
        window.location = '/onboard/funder';
      } else {
        return _alert(gettext('Thanks, you can read the guide <a href="/how/funder">here.</a>'), 'info');
      }

    } else if (response.persona === 'persona_is_hunter') {
      if (checkUrlRedirect(urls, document.location.href)) {
        window.location = '/onboard/contributor';
      } else {
        return _alert(gettext('Thanks, you can read the guide <a href="/how/contributor">here.</a>'), 'info');
      }
    }

  });
};


this.gitcoinUpdates = () => {
  const urlUpdates = `https://api.github.com/repos/gitcoinco/web/issues/5057?access_token=${document.contxt.access_token}`;

  const getUpdates = fetchData (urlUpdates, 'GET');

  $.when(getUpdates).then(response => {

    const content = $.parseHTML(
      `<div id="gitcoin_updates" class="modal fade" tabindex="-1" role="dialog" aria-hidden="true">
        <div class="modal-dialog modal-lg">
          <div class="modal-content px-4 py-3">
            <div class="col-12">
              <button type="button" class="close" data-dismiss="modal" aria-label="Close">
                <span aria-hidden="true">&times;</span>
              </button>
            </div>
            <div class="col-12 pt-2 pb-2 text-center">
              <img src="${static_url}v2/images/modals/persona-choose.svg" width="160" height="137">
              <h2 class="mt-4">${response.title}</h2>
            </div>
            <div class="col-12 pt-2 dynamic-content">
              ${response.body}
            </div>
            <div class="col-12 my-4 d-flex justify-content-around">
              <button type="button" class="btn btn-primary" data-dismiss="modal" aria-label="Close">Close</button>
            </div>
          </div>
        </div>
      </div>`);

    $(content).appendTo('body');
    $('#gitcoin_updates').bootstrapModal('show');
  });

  $(document, '#gitcoin_updates').on('hidden.bs.modal', function(e) {
    $('#gitcoin_updates').remove();
    $('#gitcoin_updates').bootstrapModal('dispose');
  });

};

this.applyCartMenuStyles = function() {
  let dot = $('#cart-notification-dot');

  if (CartData.hasItems()) {
    dot.addClass('notification__dot_active');
    dot.text(CartData.length());
  } else {
    dot.removeClass('notification__dot_active');
    if (document.location.href.indexOf('/grants') == -1) {
      $('#cart-nav').addClass('hidden');
    }
  }
};

// Turn form data pulled form page into a JS object
this.objectifySerialized = function(data) {
  let objectData = {};

  for (let i = 0; i < data.length; i++) {
    const item = data[i];

    objectData[item.name] = item.value;
  }

  return objectData;
};
