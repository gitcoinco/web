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

  var remove_top_row = function() {
    $('#top_nav_notification').parents('.row').remove();
    localStorage['top_nav_notification_remove'] = true;
  };

  if (localStorage['top_nav_notification_remove']) {
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

    if (panel.style.maxHeight) {
      panel.style.maxHeight = null;
      panel.style.marginBottom = 0 + 'px';
    } else {
      panel.style.maxHeight = panel.scrollHeight + 'px';
      panel.style.marginBottom = 10 + 'px';
    }
  });
});


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
            <a rel="modal:close" href="javascript:void" aria-label="Close dialog" class="button button--primary">Ok</a>
          </div>
        </div>
      </div>
    </div>`);

  $(content).appendTo('body');
  $('#notify_policy_update').bootstrapModal('show');
}
