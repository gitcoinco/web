/* eslint-disable no-loop-func */
/* eslint-disable no-console */
/* eslint-disable nonblock-statement-body-position */
$(document).ready(function() {

  if (typeof ($('body').tooltip) != 'undefined') {
    $('body').tooltip({
      items: ':not([data-toggle])'
    });
  }

  var force_no_www = function() {
    if (document.location.href.indexOf('https://www.gitcoin.co') != -1) {
      var new_url = document.location.href.replace('www.gitcoin.co', 'gitcoin.co');

      document.location.href = new_url;
    }
  };

  force_no_www();

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

  record_campaign_to_cookie();

  if (!$('.header > .minihero').length && $('.header > .navbar').length) {
    $('.header').css('overflow', 'visible');
  }

  $('.nav-link.dropdown-toggle').on('click', function(e) {
    e.preventDefault();
    var parent = $(this).parents('.nav-item');

    var parentSiblings = parent.siblings('.nav-item');

    parent.find('.dropdown-menu').toggle().toggleClass('show');
    parentSiblings.find('.dropdown-menu').hide();
  });

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


  // preload hover image
  var url = $('#logo').data('hover');

  $.get(url, function() {
    // …
  });

  $('#logo').mouseover(function(e) {
    $(this).attr('old-src', $(this).attr('src'));
    var new_src = $(this).data('hover');

    $(this).attr('src', new_src);
    e.preventDefault();
  });

  $('#logo').mouseleave(function(e) {
    $(this).attr('src', $(this).attr('old-src'));
  });
  if (!$.fn.collapse) {
    $('.navbar-toggler').on('click', function() {
      var toggle = $(this).attr('aria-expanded');

      console.log(toggle);
      $('.navbar-collapse').toggleClass('show');
      if (toggle === 'false') {
        $(this).attr('aria-expanded', 'true');
      } else {
        $(this).attr('aria-expanded', 'false');
      }

    });
  }

  var top_nav_salt = 2;
  var remove_top_row = function() {
    $('#top_nav_notification').parents('.row').remove();
    localStorage['top_nav_notification_remove_' + top_nav_salt] = true;
  };

  if (localStorage['top_nav_notification_remove_' + top_nav_salt]) {
    remove_top_row();
  }
  $('#top_nav_notification').click(remove_top_row);

  // pulse animation on click
  $('.pulseClick').on('click', (event) => {
    let element = $(event.target);

    element.addClass('pulseButton');
    let callback = () => {
      element.removeClass('pulseButton');
    };

    setTimeout(callback, 300);
  });

  $('.faq_item .question').on('click', (event) => {
    $(event.target).parents('.faq_parent').find('.answer').toggleClass('hidden');
    $(event.target).parents('.faq_parent').find('.answer').toggleClass('show');
  });

  $('.accordion').on('click', (event) => {
    const element = $(event.target);

    element.toggleClass('active');
    let panel = element[0].nextElementSibling;

    if (panel) {
      if (panel.style.maxHeight) {
        panel.style.maxHeight = null;
        panel.style.marginBottom = 0 + 'px';
      } else {
        panel.style.maxHeight = panel.scrollHeight + 'px';
        panel.style.marginBottom = 10 + 'px';
      }
    }
  });
  attach_close_button();
});

const attach_close_button = function() {
  $('body').delegate('.alert .closebtn', 'click', function(e) {
    $(this).parents('.alert').remove();
    $('.alert').each(function(index) {
      if (index == 0) $(this).css('top', 0);
      else {
        let new_top = (index * 66) + 'px';

        $(this).css('top', new_top);
      }
    });
  });
};

const closeButton = function(msg) {
  var html = (msg['closeButton'] === false ? '' : '<span class="closebtn" >&times;</span>');

  return html;
};

const alertMessage = function(msg) {
  var html = `<strong>${typeof msg['title'] !== 'undefined' ? msg['title'] : ''}</strong>${msg['message']}`;

  return html;
};

const _alert = function(msg, _class) {
  if (typeof msg == 'string') {
    msg = {
      'message': msg
    };
  }
  var numAlertsAlready = $('.alert:visible').length;
  var top = numAlertsAlready * 44;

  var html = function() {
    return (
      `<div class="alert ${_class} g-font-muli" style="top: ${top}px">
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
};


if ($('#is-authenticated').val() === 'True' && !localStorage['notify_policy_update']) {
  localStorage['notify_policy_update'] = true;

  const content = $.parseHTML(
    `<div id="notify_policy_update" class="modal fade" tabindex="-1" role="dialog" aria-hidden="true">
      <div class="modal-dialog">
        <div class="modal-content px-4 py-3">
          <div class="col-12">
            <button type="button" class="close" data-dismiss="modal" aria-label="Close"><span aria-hidden="true">×</span></button>
          </div>
          <div class="col-12 pt-2 pb-2 text-center">
            <h2 class="font-title">${gettext('We Care About Your Privacy')}</h2>
          </div>
          <div class="col-12 pt-2 pb-2 font-body">
            <p>${gettext('As a Web 3.0 company, we think carefully about user data and privacy and how the internet is evolving. We hope Web 3.0 will bring more control of data to users. With this ethos in mind, we are always careful about how we use your information.')}</p>
            <p>${gettext('We recently reviewed our Privacy Policy to comply with requirements of General Data Protection Regulation (GDPR), improving our Terms of Use, Privacy Policy and Cookie Policy. These changes are in effect and your continued use of the Gitcoin will be subjected to our updated Terms of Use and Privacy Policy.')}</p>
          </div>
          <div class="col-12 font-caption">
            <a href="/legal/policy" target="_blank">${gettext('Read Our Updated Terms')}</a>
          </div>
          <div class="col-12 mt-4 mb-2 text-right font-caption">
            <button type="button" class="button button--primary" data-dismiss="modal">ok</button>
          </div>
        </div>
      </div>
    </div>`);

  $(content).appendTo('body');
  $('#notify_policy_update').bootstrapModal('show');
}

if (document.contxt.github_handle && !document.contxt.persona_is_funder && !document.contxt.persona_is_hunter) {

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
            <p>${gettext('Let us know so we could optimize the <br>best experience for you!')}</p>
          </div>
          <div class="col-12 my-4 d-flex justify-content-around">
            <button type="button" class="btn btn-gc-blue col-5" data-persona="persona_is_funder">I'm a Funder</button>
            <button type="button" class="btn btn-gc-blue col-5" data-persona="persona_is_hunter">I'm a Contributor</button>
          </div>
        </div>
      </div>
    </div>`);

  $(content).appendTo('body');
  $('#persona_modal').bootstrapModal('show');
}

$('body').on('click', '[data-persona]', function(e) {
  sendPersonal($(this).data('persona'));
});

const sendPersonal = (persona) => {
  let postPersona = fetchData('/api/v0.1/choose_persona/', 'POST',
    {persona, 'access_token': document.contxt.access_token}
  );

  $.when(postPersona).then((response, status, statusCode) => {
    if (statusCode.status != 200) {
      return _alert(response.msg, 'error');
    }

    $('#persona_modal').bootstrapModal('hide');
    const urls = [
      {
        url: document.location.href,
        redirect: '/onboard/funder'
      },
      {
        url: '/bounties/funder',
        redirect: '/onboard/funder'
      },
      {
        url: '/contributor',
        redirect: '/onboard/contributor'
      }
    ];

    const checkUrl = (arr, val) => {
      return arr.some(arrObj => {
        if (val.indexOf(arrObj.url) >= 0) {
          return true;
        }
        return false;
      });
    };

    if (response.persona === 'persona_is_funder') {
      if (checkUrl(urls, document.location.href)) {
        window.location = '/onboard/funder';
      } else {
        return _alert(gettext('Thanks, you can read the guide <a href="/how/funder">here.</a>'), 'info');
      }

    } else if (response.persona === 'persona_is_hunter') {
      if (checkUrl(urls, document.location.href)) {
        window.location = '/onboard/contributor';
      } else {
        return _alert(gettext('Thanks, you can read the guide <a href="/how/contributor">here.</a>'), 'info');
      }
    }


  });
};
