/* eslint no-useless-concat: 0 */ // --> OFF

$(document).ready(function() {

  var linkify = function(new_text) {
    new_text = new_text.replace(/(?:^|\s)#([a-zA-Z\d-]+)/g, ' <a href="/?tab=search-$1">#$1</a>');
    new_text = new_text.replace(/\B@([a-zA-Z0-9_-]*)/g, ' <a href="/profile/$1">@$1</a>');
    return new_text;
  };
  // inserts links into the text where there are URLS detected

  function urlify(text) {
    var urlRegex = /https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,4}\b([-a-zA-Z0-9@:%_\+.~#?&//=]*)/g;

    return text.replace(urlRegex, function(url) {
      return '<a target=blank rel=nofollow href="' + url + '">' + url + '</a>';
    });
  }

  var get_jitsi_api_object = function(roomName) {
    var jitsi_domain = 'meet.jit.si';
    var jitsi_options = {
      roomName: roomName,
      parentNode: document.querySelector('#' + roomName),
      welcomePageEnabled: true
    };
    var jitsi_api = new JitsiMeetExternalAPI(jitsi_domain, jitsi_options);

    return jitsi_api;
  };

  // join video call
  $(document).on('click', '.click_here_to_join_video', function(e) {
    e.preventDefault();
    if (typeof document.jitsi_api != 'undefined') {
      _alert('You can only be in one video call at a time.', 'error', 1000);
      return;
    }
    const animals = [ 'Hamster', 'Marmot', 'Robot', 'Ferret', 'Squirrel' ];
    const animal = animals[Math.floor(Math.random() * animals.length)];
    const safeHandle = document.contxt.github_handle ? document.contxt.github_handle : animal;

    $(this).addClass('live');
    $(this).text('');
    const roomName = $(this).data('roomname');
    const api = get_jitsi_api_object(roomName);
    const avatarURL = 'https://gitcoin.co/dynamic/avatar/' + safeHandle;

    document.jitsi_api = api;
    api.executeCommand('displayName', safeHandle + parseInt(100 * Math.random()));
    api.executeCommand('avatarUrl', avatarURL);
    api.executeCommand('toggleAudio'); // default off
    api.executeCommand('toggleVideo'); // default off
    const participants_count = api.getNumberOfParticipants() + 1;
    const $target = $(this).parents('.activity_detail_content');
    const html = `
    <p class='float-right p-0 m-0 video_options_container'>
    <a href=# class='full_screen'>Full Screen <i class="fas fa-expand-arrows-alt"></i></a> | 
    <a href=# class='popout_screen'>Pop Out <i class="fas fa-sign-out-alt"></i></a> | 
    <a href=# class='new_tab'>Open in New Tab <i class="fas fa-external-link-square-alt"></i></i></a> | 
    <a href=# class=' leave_video_call'>Leave Video Call <i class="far fa-times-circle"></i></a>
    </p>`;

    $target.prepend(html);
  });

  // refresh job for live call
  setInterval(function() {
    $('.click_here_to_join_video.live').each(function() {
      const pc = document.jitsi_api.getNumberOfParticipants();
      const roomName = $(this).data('roomname');
      const $parent = $(this).parents('.activity_detail');

      $parent.find('.participants_count').text(pc);
      if ($parent.find('.indie_chat_indicator').hasClass('offline')) {
        $parent.find('.indie_chat_indicator').removeClass('offline');
      }
      if (!document.contxt.github_handle) {
        return;
      }
      const url = '/api/v0.1/video/presence';
      const params = {
        'participants': pc,
        'roomname': roomName,
        'csrfmiddlewaretoken': $('input[name=csrfmiddlewaretoken]').val()
      };

      $.post(url, params, function(response) {
        $.noop;
      });
    });
  }, 5000);

  $(document).on('click', '.new_tab', function(e) {
    e.preventDefault();
    var roomname = $(this).parents('.row').find('.click_here_to_join_video').data('roomname');
    var url = 'https://meet.jit.si/' + roomname;

    window.open(url, '_blank');
  });

  // leave video call
  $(document).on('click', '.leave_video_call', function(e) {
    e.preventDefault();
    document.jitsi_api.dispose();
    var $taret = $(this).parents('.row').find('.click_here_to_join_video');
    var url = $taret.data('src');
    var html = "<img src='" + url + "'>";

    document.jitsi_api = undefined;
    $taret.removeClass('live').html(html);
    $('.video_options_container').remove();
  });

  // full screen
  $(document).on('click', '.full_screen', function(e) {
    e.preventDefault();
    var $target = $(this).parents('.row').find('iframe[name=jitsiConferenceFrame0]');

    toggleFullscreen();
  });

  // popout screen
  $(document).on('click', '.popout_screen', function(e) {
    e.preventDefault();
    var $target = $(this).parents('.row').find('iframe[name=jitsiConferenceFrame0]');

    $target.toggleClass('popout');
    if ($(this).text().indexOf('Pop Out') != -1) {
      $(this).html('Pop In <i class="fas fa-level-up-alt"></i>');
    } else {
      $(this).html('Pop Out <i class="fas fa-sign-out-alt">');
    }
  });

  function toggleFullscreen() {
    let iframe = document.querySelector('#jitsiConferenceFrame0');

    if (!document.fullscreenElement) {
      iframe.requestFullscreen().catch(err => {
        alert(`Error attempting to enable full-screen mode: ${err.message} (${err.name})`);
      });
    } else {
      document.exitFullscreen();
    }
  }

  $(document).on('click', '.infinite-more-link', function(e) {
    if ($(this).hasClass('hidden')) {
      e.preventDefault();
      return;
    }
    $(this).addClass('hidden');
    var url = $(this).attr('href');

    $('.infinite-container').find('.loading').removeClass('hidden');
    $.get(url, function(response) {
      $('.infinite-container').find('.infinite-more-link').remove();
      $('.infinite-container').find('.loading').remove();
      $('.infinite-container').append($(response).find('.infinite-container').html());
      $('.infinite-container').find('.loading').addClass('hidden');
    });
    e.preventDefault();
  });
  $('.infinite-more-link').click();


  document.base_title = $('title').text();

  // remove loading indicator
  var remove_loading_indicator = function() {
    if ($('.activity_stream .box').length) {
      $('#activity_subheader').remove();
    } else {
      setTimeout(remove_loading_indicator, 50);
    }
  };

  remove_loading_indicator();
  $('#activity_subheader span').remove();

  // notifications of new activities
  var ping_activity_notifier = (function() {
    var plural = document.buffered_rows.length == 1 ? 'y' : 'ies';
    var html = '<div id=new_activity_notifier>' + document.buffered_rows.length + ' New Activit' + plural + ' - Click to View</div>';

    if ($('#new_activity_notifier').length) {
      $('#new_activity_notifier').html(html);
    } else {
      $(html).insertBefore($('#activities .box').first());
    }
    var prefix = '(' + document.buffered_rows.length + ') ';

    $('title').text(prefix + document.base_title);

  });

  // refresh activity page
  document.buffered_rows = [];
  var refresh_interval = 7000;
  var max_pk = null;
  var run_longpoller = function(recursively) {
    if (document.hidden) {
      return setTimeout(function() {
        if (recursively) {
          run_longpoller(true);
        }
      }, refresh_interval);
    }
    if ($('.infinite-more-link').length) {
      if (!max_pk) {
        max_pk = $('#activities .box').first().data('pk');
        if (!max_pk) {
          return;
        }
      }
      // get new activities
      var url = $('.infinite-more-link').attr('href').split('page')[0];

      url += '&after-pk=' + max_pk;
      $.get(url, function(html) {
        var new_row_number = $(html).find('.activity.box').first().data('pk');

        if (new_row_number && new_row_number > max_pk) {
          max_pk = new_row_number;
          $(html).find('.activity.box').each(function() {
            document.buffered_rows.push($(this)[0].outerHTML);
          });
          ping_activity_notifier();
        }
        // recursively run the longpoller
        setTimeout(function() {
          if (recursively) {
            run_longpoller(true);
          }
        }, refresh_interval);
      });
    }
  };
  // hack to make this available to status.js

  document.run_long_poller = run_longpoller;

  // schedule long poller when first activity feed item shows up
  // by recursively waiting for the activity items to show up
  var schedule_long_poller = function() {
    if ($('#activities .box').length) {
      run_longpoller(true);
    } else {
      setTimeout(function() {
        schedule_long_poller();
      }, 1000);
    }
  };

  setTimeout(function() {
    if (document.long_poller_live) {
      schedule_long_poller();
    }
  }, 1000);

  $(document).on('click', '.activity_stream .content', function(e) {
    window.open($(this).find('a.d-block').first().attr('href'));
    e.preventDefault();
  });

  // expand attachments
  $(document).on('click', '#activities .row .attachment', function(e) {
    e.preventDefault();
    $(this).toggleClass('expanded');
  });

  // refresh new actviity feed items
  $(document).on('click', '#new_activity_notifier', function(e) {
    e.preventDefault();
    for (var i = document.buffered_rows.length; i > 0; i -= 1) {
      var html = document.buffered_rows[i - 1];

      $('.infinite-container').prepend($(html));
    }
    $(this).remove();
    document.buffered_rows = [];
    $('title').text(document.base_title);
  });

  // show percentages and votes
  var update_and_reveal = function($this, total) {

    // calc total
    var answers = $this.parents('.poll_choices').find('span');

    for (var i = 0; i < answers.length; i++) {
      total += parseInt(($(answers[i]).text()));
    }

    // update all htmls
    for (var j = 0; j < answers.length; j++) {
      var $answer = $(answers[j]);
      var answer = parseInt(($answer.text()));
      var new_answer = answer;

      if (isNaN(new_answer)) {
        new_answer = 0;
      }
      var pct = Math.round((new_answer / total) * 100);

      if (isNaN(pct)) {
        pct = 0;
      }
      var html = '- ' + new_answer + ' ( ' + pct + '% )';

      $answer.html(html);
    }
    return total;
  };

  $('.poll_choices.answered').each(function() {
    update_and_reveal($(this).find('div'), 0);
  });

  // vote on a poll
  $(document).on('click', '.poll_choices div', function(e) {
    e.preventDefault();

    // no answering twice
    if ($(this).parents('.poll_choices').hasClass('answered')) {
      return;
    }

    // setup
    $(this).addClass('answer');
    $(this).parents('.poll_choices').addClass('answered');

    // update this error count
    var $answer = $(this).find('span');
    var answer = parseInt(($answer.text()));
    var new_answer = answer + 1;

    $answer.html(new_answer);

    update_and_reveal($(this), 0);

    // remote post
    var $parent = $(this).parents('.activity.box');
    var vote = $(this).data('vote');
    var params = {
      'method': 'vote',
      'vote': vote,
      'csrfmiddlewaretoken': $('input[name=csrfmiddlewaretoken]').val()
    };
    var url = '/api/v0.1/activity/' + $parent.data('pk');

    $.post(url, params, function(response) {
      console.log(response);
    });

  });

  // delete activity
  $(document).on('click', '.delete_activity', function(e) {
    e.preventDefault();
    if (!document.contxt.github_handle) {
      _alert('Please login first.', 'error');
      return;
    }

    if (!confirm('Are you sure you want to delete this?')) {
      return;
    }

    // update UI
    $(this).parents('.activity.box').remove();

    // remote post
    var params = {
      'method': 'delete',
      'csrfmiddlewaretoken': $('input[name=csrfmiddlewaretoken]').val()
    };
    var url = '/api/v0.1/activity/' + $(this).data('pk');

    $.post(url, params, function(response) {
      // no message to be sent
    });

  });
  // like activity
  var send_tip_to_object = function($parent, e, tag) {
    e.preventDefault();
    if (!document.contxt.github_handle) {
      _alert('Please login first.', 'error');
      return;
    }
    if (!web3) {
      _alert('Please enable and unlock your web3 wallet.', 'error');
      return;
    }

    var $amount = $parent.find('.amount');
    var has_hidden_comments = $parent.parents('.activity.box').find('.row.comment_row.hidden').length;

    const email = '';
    const github_url = '';
    const from_name = document.contxt['github_handle'];
    const username = $parent.data('username');
    var amount_input = prompt('How much ETH do you want to send to ' + username + '?', '0.001');

    if (!amount_input) {
      return;
    }
    const amountInEth = parseFloat(amount_input.replace('ETH', ''));

    if (amountInEth < 0.001) {
      _alert('Amount must be 0.001 or more.', 'error');
      return;
    }
    const comments_priv = tag + ':' + $parent.data('pk');
    const comments_public = '';
    const accept_tos = true; // accepted upon signup
    const from_email = '';
    const tokenAddress = '0x0';
    const expires = 9999999999;
    var success_callback = function(txid) {
      const url = 'https://' + etherscanDomain() + '/tx/' + txid;
      const msg = 'This payment has been sent 👌 <a target=_blank href="' + url + '">[Etherscan Link]</a>';

      var old_amount = $amount.text();
      var new_amount = Math.round(1000 * (parseFloat(old_amount) + parseFloat(amountInEth))) / 1000;

      $amount.fadeOut().text(new_amount).fadeIn();
      setTimeout(function() {
        var $target = $parent.parents('.activity.box').find('.comment_activity');

        var override_hide_comments = !has_hidden_comments;

        view_comments($target, false, undefined, true);
      }, 1000);

      _alert(msg, 'info', 1000);
      // todo: update amount
    };

    var failure_callback = function() {
      $.noop(); // do nothing
    };

    return sendTip(
      email,
      github_url,
      from_name,
      username,
      amountInEth,
      comments_public,
      comments_priv,
      from_email,
      accept_tos,
      tokenAddress,
      expires,
      success_callback,
      failure_callback,
      false
    );

  };

  $(document).on('click', '.tip_on_comment', function(e) {
    send_tip_to_object($(this), e, 'comment');
  });
  $(document).on('click', '.tip_activity', function(e) {
    send_tip_to_object($(this), e, 'activity');
  });


  // like activity
  $(document).on('click', '.like_activity, .flag_activity', function(e) {
    e.preventDefault();
    if (!document.contxt.github_handle) {
      _alert('Please login first.', 'error');
      return;
    }

    var is_unliked = $(this).data('state') == $(this).data('negative');
    var num = $(this).find('span.num').html();

    if (is_unliked) { // like
      $(this).find('span.action').addClass('open');
      $(this).data('state', $(this).data('affirmative'));
      $(this).addClass('animate-sparkle');

      num = parseInt(num) + 1;
      $(this).find('span.num').html(num);
    } else { // unlike
      $(this).find('span.action').removeClass('open');
      $(this).data('state', $(this).data('negative'));
      $(this).removeClass('animate-sparkle');
      num = parseInt(num) - 1;
      $(this).find('span.num').html(num);
    }

    // remote post
    var params = {
      'method': $(this).data('action'),
      'direction': $(this).data('state'),
      'csrfmiddlewaretoken': $('input[name=csrfmiddlewaretoken]').val()
    };
    var url = '/api/v0.1/activity/' + $(this).data('pk');

    var parent = $(this).parents('.activity.box');

    parent.find('.loading').removeClass('hidden');
    $.post(url, params, function(response) {
      // no message to be sent
      parent.find('.loading').addClass('hidden');
    }).fail(function() {
      parent.find('.error').removeClass('hidden');
    });


  });

  var post_comment = function($parent, allow_close_comment_container) {
    if (!document.contxt.github_handle) {
      _alert('Please login first.', 'error');
      return;
    }

    // user input
    var comment = $parent.parents('.box').find('.comment_container textarea').val().trim();

    // validation
    if (!comment) {
      return;
    }

    $parent.parents('.box').find('.comment_container textarea').prop('disabled', true);
    $('.post_comment').prop('disabled', true);

    $parent.parents('.activity.box').find('.loading').removeClass('hidden');
    var has_hidden_comments = $parent.parents('.activity.box').find('.row.comment_row.hidden').length;
    // increment number
    var num = $parent.find('span.num').html();

    num = parseInt(num) + 1;
    $parent.find('span.num').html(num);

    // remote post
    var params = {
      'method': 'comment',
      'comment': comment,
      'csrfmiddlewaretoken': $('input[name=csrfmiddlewaretoken]').val()
    };
    var url = '/api/v0.1/activity/' + $parent.data('pk');

    $.post(url, params, function(response) {
      var success_callback = function($parent) {
        $parent.parents('.box').find('.comment_container textarea').val('');
        $parent.find('textarea').focus();

      };
      var override_hide_comments = !has_hidden_comments;

      view_comments($parent, allow_close_comment_container, success_callback, override_hide_comments);
    }).done(function() {
      // pass
    })
      .fail(function() {
        $parent.parents('.activity.box').find('.error').removeClass('hidden');
      })
      .always(function() {
        $parent.parents('.activity.box').find('.loading').addClass('hidden');
        $parent.parents('.box').find('.comment_container textarea').prop('disabled', false);
        $('.post_comment').prop('disabled', false);
      });
  };

  // converts an object to a dict
  function convert_to_dict(obj) {
    return Object.keys(obj).map(key => ({
      name: key,
      value: obj[key],
      type: 'foo'
    }));
  }

  var view_comments = function($parent, allow_close_comment_container, success_callback, override_hide_comments) {
    hide_after_n_comments = 3;
    if (getParam('tab') && getParam('tab').indexOf('activity:') != -1) {
      hide_after_n_comments = 100;
    }
    const limit_hide_option = 10;
    // remote post
    var params = {
      'method': 'comment'
    };
    var url = '/api/v0.1/activity/' + $parent.data('pk');

    var $target = $parent.parents('.activity.box').find('.comment_container');
    var $existing_textarea = $target.find('textarea.enter-activity-comment');
    var existing_text = $existing_textarea.length ? $existing_textarea.val() : '';

    if (!$target.length) {
      $target = $parent.parents('.box').find('.comment_container');
    }

    if ($target.hasClass('filled') && allow_close_comment_container) {
      $target.html('');
      $target.removeClass('filled');
      $parent.find('.action').removeClass('open');
      return;
    }
    $parent.find('.action').addClass('open');
    $parent.parents('.activity.box').find('.loading').removeClass('hidden');
    $.get(url, params, function(response) {
      $parent.parents('.activity.box').find('.loading').addClass('hidden');
      $target.addClass('filled');
      $target.html('');
      let num_comments = response['comments'].length;

      for (let i = 0; i < num_comments; i++) {
        let comment = sanitizeAPIResults(response['comments'])[i];
        let the_comment = comment['comment'];

        the_comment = urlify(the_comment);
        the_comment = linkify(the_comment);
        the_comment = the_comment.replace(/\r\n|\r|\n/g, '<br />');
        const timeAgo = timedifferenceCvrt(new Date(comment['created_on']));
        const show_tip = true;
        const is_comment_owner = document.contxt.github_handle == comment['profile_handle'];
        var sorted_match_curve_html = '';

        if (comment['sorted_match_curve']) {

          var match_curve = Array.from(convert_to_dict(comment['sorted_match_curve']).values());

          for (let j = 0; j < match_curve.length; j++) {
            let ele = match_curve[j];

            sorted_match_curve_html += '<li>';
            sorted_match_curve_html += `Your contribution of ${ele.name} could yield $${Math.round(ele.value * 1000) / 1000} in matching.`;
            sorted_match_curve_html += '</li>';
          }
        }
        var show_more_box = '';
        var is_hidden = (num_comments - i) >= hide_after_n_comments && override_hide_comments != true;
        var is_first_hidden = i == 0 && num_comments >= hide_after_n_comments && override_hide_comments != true;
        const show_all_option = num_comments > limit_hide_option;

        if (is_first_hidden) {
          show_more_box = `
          <div class="row mx-auto ${ show_all_option ? 'show_all' : 'show_more'} d-block text-center">
            <a href="#" class="text-black-60 font-smaller-5">
            ${ show_all_option ? 'See all comments' : `Show More (<span class="comment-count">${num_comments - hide_after_n_comments}</span>)`}
            </a>
          </div>
          `;
        }
        let html = `
        ${show_more_box}
        <div class="row comment_row mx-auto ${is_hidden ? 'hidden' : ''}" data-id=${comment['id']}>
          <div class="col-1 activity-avatar my-auto">
            <a href="/profile/${comment['profile_handle']}" data-toggle="tooltip" title="@${comment['profile_handle']}">
              <img src="/dynamic/avatar/${comment['profile_handle']}">
            </a>
          </div>
          <div class="col-11 activity_comments_main pl-4 px-sm-3">
            <div class="mb-0">
              <span>
              <span class="chat_presence_indicator mini ${comment['last_chat_status']}" data-openchat="${comment['profile_handle']}">
                <span class="indicator" data-toggle="tooltip" title="Gitcoin Chat: ${comment['last_chat_status_title']}">
                  •
                </span>
              </span>          
                <b>${comment['name']}</b>
                <span class="grey"><a class=grey href="/profile/${comment['profile_handle']}">
                @${comment['profile_handle']}
                </a></span>
                ${comment['match_this_round'] ? `
                <span class="tip_on_comment" data-pk="${comment['id']}" data-username="${comment['profile_handle']}" style="border-radius: 3px; border: 1px solid white; color: white; background-color: black; cursor:pointer; padding: 2px; font-size: 10px;" data-placement="bottom" data-toggle="tooltip" data-html="true"  title="@${comment['profile_handle']} is estimated to be earning <strong>$${comment['match_this_round']}</strong> in this week's CLR Round.
                <BR><BR>

              Want to help @${comment['profile_handle']} move up the rankings?  Assuming you haven't contributed to @${comment['profile_handle']} yet this round, a contribution of 0.001 ETH (about $0.30) could mean +<strong>$${Math.round(1000 * comment['default_match_round']) / 1000}</strong> in matching.
              <br>
              <br>
              Other contribution levels will mean other matching amounts:
              <ul>
              ${sorted_match_curve_html}
              </ul>

              <br>Want to learn more?  Go to gitcoin.co/townsquare and checkout the CLR Matching Round Leaderboard.
              ">
                  <i class="fab fa-ethereum mr-0" aria-hidden="true"></i>
                  $${comment['match_this_round']} | +$${Math.round(100 * comment['default_match_round']) / 100}
                </span>

                  ` : ' '}
              </span>
              <span class='float-right'>
                <span class="d-none d-sm-inline grey font-smaller-5 text-right">
                  ${timeAgo}
                </span>
                <span class="font-smaller-5 mt-1" style="display: block; text-align: right;">
                  ${is_comment_owner ?
    `<i data-pk=${comment['id']} class="delete_comment fas fa-trash font-smaller-7 position-relative text-black-70 mr-1 cursor-pointer" style="top:-1px; "></i>| `
    : ''}
                  ${show_tip ? `
                  <span class="action like px-0 ${comment['is_liked'] ? 'open' : ''}" data-toggle="tooltip" title="Liked by ${comment['likes']}">
                    <i class="far fa-heart grey"></i> <span class=like_count>${comment['like_count']}</span>
                  </span> |
                  <a href="#" class="tip_on_comment text-dark" data-pk="${comment['id']}" data-username="${comment['profile_handle']}"> <i class="fab fa-ethereum grey"></i> <span class="amount grey">${Math.round(1000 * comment['tip_count_eth']) / 1000}</span>
                  </a>
                  ` : ''}
                <span>
              </span>
            </div>
            <div class="activity_comments_main_comment pt-1 pb-1">
              ${the_comment}
            </div>
          </div>

        </div>
        `;

        $target.append(html);
      }

      const post_comment_html = `
        <div class="row py-2 mx-auto">
          <div class="col-sm-1 mt-1 activity-avatar d-none d-sm-inline">
            <img src="/dynamic/avatar/${document.contxt.github_handle}">
          </div>
          <div class="col-12 col-sm-11 text-right">
            <textarea class="form-control bg-lightblue font-caption enter-activity-comment" placeholder="Enter comment" cols="80" rows="3">${existing_text}</textarea>
            <a href=# class="btn btn-gc-blue btn-sm mt-= font-smaller-7 font-weight-bold post_comment">COMMENT</a>
          </div>
        </div>
      `;

      $target.append(post_comment_html);
      if (success_callback && typeof success_callback != 'undefined') {
        success_callback($target);
      }
    });
  };


  // post comment activity
  $(document).on('click', '.comment_container .action.like', function(e) {
    e.preventDefault();
    var id = $(this).parents('.comment_row').data('id');

    var params = {
      'method': 'toggle_like_comment',
      'comment': id,
      'csrfmiddlewaretoken': $('input[name=csrfmiddlewaretoken]').val()
    };
    var url = '/api/v0.1/activity/' + $(this).parents('.activity').data('pk');

    $.post(url, params, function(response) {
      console.log('toggle like');
    });
    var like_count = parseInt($(this).find('span.like_count').text());

    if ($(this).hasClass('open')) {
      $(this).removeClass('open');
      $(this).removeClass('animate-sparkle');
      like_count = like_count - 1;
    } else {
      $(this).addClass('open');
      $(this).addClass('animate-sparkle');
      like_count = like_count + 1;
    }
    let $ele = $(this).find('span.like_count');

    $ele.fadeOut(function() {
      $ele.text(like_count);
      $ele.fadeIn();
    });
  });

  var get_hidden_comments = function($this) {
    return $this.parents('.activity_comments').find('.comment_row.hidden');
  };

  // post comment activity
  $(document).on('click', '.show_more', function(e) {
    e.preventDefault();
    const num_to_unhide_at_once = 3;

    for (var i = 0; i < num_to_unhide_at_once; i++) {
      get_hidden_comments($(this)).last().removeClass('hidden');
    }
    if (get_hidden_comments($(this)).length == 0) {
      $(this).remove();
    } else {
      $(this).find('.comment-count').text(get_hidden_comments($(this)).length);
    }
  });

  $(document).on('click', '.show_all', function(e) {
    e.preventDefault();
    const hiddenComments = get_hidden_comments($(this));

    for (let i = 0; i < hiddenComments.length; i++) {
      hiddenComments[i].classList.remove('hidden');
    }

    $(this).remove();
  });

  // post comment activity
  $(document).on('click', '.comment_activity', function(e) {
    e.preventDefault();
    var success_callback = function($parent) {
      $parent.find('textarea').focus();
    };

    view_comments($(this), true, success_callback, false);
  });

  // post comment activity
  $(document).on('click', '.post_comment', function(e) {
    e.preventDefault();
    const $target = $(this).parents('.activity.box').find('.comment_activity');

    post_comment($target, false);
  });

  $(document).on('click', '.delete_comment', function(e) {
    e.preventDefault();
    const comment_id = $(this).data('pk');

    const params = {
      'method': 'DELETE',
      'csrfmiddlewaretoken': $('input[name=csrfmiddlewaretoken]').val()
    };

    const url = '/api/v0.1/comment/' + comment_id;

    if (confirm('Do you want to delete this comment?')) {
      $.post(url, params, function(response) {
        if (response.status <= 204) {
          _alert('comment successfully deleted.', 'success', 1000);
          $(`.comment_row[data-id='${comment_id}']`).addClass('hidden');
          console.log(response);
        } else {
          _alert(`Unable to delete commment: ${response.message}`, 'error');
          console.log(`error deleting commment: ${response.message}`);
        }
      }).fail(function(error) {
        _alert('Unable to delete comment', 'error');
        console.log(`error deleting commment: ${error.message}`);
      });
    }
  });


  $(document).on('keypress', '.enter-activity-comment', function(e) {
    if (e.which == 13 && !e.shiftKey) {
      const $target = $(this).parents('.activity.box').find('.comment_activity');

      post_comment($target, false);
    }
  });

  // post comment activity
  $(document).on('click', '.copy_activity', function(e) {
    e.preventDefault();
    var url = $(this).data('url');

    copyToClipboard(url);
    _alert('Link copied to clipboard.', 'success', 1000);
    $(this).addClass('open');
    var $target = $(this);

    setTimeout(function() {
      $target.removeClass('open');
    }, 300);
  });


  // auto open new comment threads
  setInterval(function() {

    $('[data-toggle="popover"]').popover();
    $('[data-toggle="tooltip"]').bootstrapTooltip();
    openChat();

    $('.comment_activity').each(function() {
      var open = $(this).data('open');

      if (open) {
        $(this).data('open', false);
        view_comments($(this), true, undefined, false);
      }
    });

    // $('.activity_detail_content span').each(function() {
    //   if (!$(this).hasClass('clean')) {
    //     let new_text = $(this).text();

    //     new_text = new_text.replace(/\</g, '_');
    //     new_text = new_text.replace(/\>/g, '_');
    //     new_text = new_text.replace(/&gt/g, '_');
    //     new_text = new_text.replace(/&lt/g, '_');
    //     new_text = new_text.replace(/\</g, '_');
    //     new_text = new_text.replace(/\>/g, '_');
    //     new_text = new_text.replace(/\n/g, '<BR>');
    //     new_text = urlify(new_text);
    //     new_text = linkify(new_text);
    //     $(this).html(new_text);
    //     $(this).addClass('clean');
    //   }
    // });
  }, 1000);


}(jQuery));

function throttle(fn, wait) {
  var time = Date.now();

  return function() {
    if ((time + wait - Date.now()) < 0) {
      fn();
      time = Date.now();
    }
  };
}
  

window.addEventListener('scroll', throttle(function() {
  var offset = 800;

  if ((window.innerHeight + window.scrollY + offset) >= document.body.offsetHeight) {
    $('.infinite-more-link').click();
  }
}, 500));

