/* eslint no-useless-concat: 0 */ // --> OFF

$(document).ready(function() {

  var linkify = function(new_text) {
    new_text = new_text.replace(/ #(\S*)/g, ' <a href="/?tab=search-$1">#$1</a>');
    new_text = new_text.replace(/ @(\S*)/g, ' <a href="/profile/$1">@$1</a>');
    return new_text;
  };
  // inserts links into the text where there are URLS detected

  function urlify(text) {
    var urlRegex = /(https?:\/\/[^\s]+)/g;

    return text.replace(urlRegex, function(url) {
      return '<a target=blank rel=nofollow href="' + url + '">' + url + '</a>';
    });
  }


  document.base_title = $('title').text();

  $('#activity_subheader').remove();

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

    const email = '';
    const github_url = '';
    const from_name = document.contxt['github_handle'];
    const username = $parent.data('username');
    var amount_input = prompt('How much ETH do you want to send to ' + username + '?', '0.01');

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
      var new_amount = Math.round(100 * (parseFloat(old_amount) + parseFloat(amountInEth))) / 100;

      $amount.fadeOut().text(new_amount).fadeIn();
      setTimeout(function() {
        var $target = $parent.parents('.activity.box').find('.comment_activity');

        view_comments($target, false);
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

      num = parseInt(num) + 1;
      $(this).find('span.num').html(num);
    } else { // unlike
      $(this).find('span.action').removeClass('open');
      $(this).data('state', $(this).data('negative'));

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
    var comment = $parent.parents('.box').find('.comment_container textarea').val();

    // validation
    if (!comment) {
      return;
    }

    $parent.parents('.activity.box').find('.loading').removeClass('hidden');

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
        $parent.find('textarea').focus();
      };

      view_comments($parent, allow_close_comment_container, success_callback);
    }).done(function() {
      // pass
    })
      .fail(function() {
        $parent.parents('.activity.box').find('.error').removeClass('hidden');
      })
      .always(function() {
        $parent.parents('.activity.box').find('.loading').addClass('hidden');
      });
  };

  var view_comments = function($parent, allow_close_comment_container, success_callback) {

    // remote post
    var params = {
      'method': 'comment'
    };
    var url = '/api/v0.1/activity/' + $parent.data('pk');

    var $target = $parent.parents('.activity.box').find('.comment_container');

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
      for (var i = 0; i < response['comments'].length; i++) {
        let comment = sanitizeAPIResults(response['comments'])[i];
        let the_comment = comment['comment'];

        the_comment = urlify(the_comment);
        the_comment = linkify(the_comment);
        the_comment = the_comment.replace(/\r\n|\r|\n/g,"<br />")
        var timeAgo = timedifferenceCvrt(new Date(comment['created_on']));
        var show_tip = true;
        let html = `
        <div class="row comment_row p-2" data-id=${comment['id']}>
          <div class="col-1 activity-avatar mt-1">
            <a href="/profile/${comment['profile_handle']}" data-toggle="tooltip" title="@${comment['profile_handle']}">
              <img src="/dynamic/avatar/${comment['profile_handle']}">
            </a>
          </div>
          <div class="col-11 activity_comments_main pl-4 px-sm-3">
            <div class="mb-1">
              <span>
                <b>${comment['name']}</b>
                <span class="grey"><a class=grey href="/profile/${comment['profile_handle']}">
                @${comment['profile_handle']}
                </a></span>
                ${comment['match_this_round'] ? `
                <span class="tip_on_comment" data-pk="${comment['id']}" data-username="${comment['profile_handle']}" style="border-radius: 3px; border: 1px solid white; color: white; background-color: black; cursor:pointer; padding: 2px; font-size: 10px;" data-placement="bottom" data-toggle="tooltip" data-html="true"  title="@${comment['profile_handle']} is estimated to be earning ${comment['match_this_round']} in this week's CLR Round.  <BR><BR><strong>Send a tip to @${comment['profile_handle']}</strong> to increase their take of the matching pool.   <br><br>Want to learn more?  Go to gitcoin.co/townsquare and checkout the CLR Matching Round Leaderboard.">
                  <i class="fab fa-ethereum mr-0" aria-hidden="true"></i>
                  $${comment['match_this_round']}
                </span>

                  ` : ' '}
              </span>
              <span class="d-none d-sm-inline grey font-smaller-5 float-right">
                ${timeAgo}
              </span>
            </div>
            <div class="activity_comments_main_comment">
              ${the_comment}
            </div>
              <span class="font-smaller-5 float-right">
              ${show_tip ? `
              <span class="action like ${comment['is_liked'] ? 'open' : ''}" data-toggle="tooltip" title="Liked by ${comment['likes']}">
                <i class="far fa-heart grey"></i> <span class=like_count>${comment['like_count']}</span>
              </span> |
              <a href="#" class="tip_on_comment text-dark" data-pk="${comment['id']}" data-username="${comment['profile_handle']}"> <i class="fab fa-ethereum grey"></i> <span class="amount grey">${Math.round(100 * comment['tip_count_eth']) / 100}</span>
              </a>
              ` : ''}
              <span>
          </div>

        </div>
        `;

        $target.append(html);
      }

      const post_comment_html = `
        <div class="row p-2">
          <div class="col-sm-1 activity-avatar d-none d-sm-inline">
            <img src="/dynamic/avatar/${document.contxt.github_handle}">
          </div>
          <div class="col-12 col-sm-11 text-right">
            <textarea class="form-control bg-lightblue font-caption enter-activity-comment" placeholder="Enter comment" cols="80" rows="5"></textarea>
            <a href=# class="btn btn-gc-blue btn-sm mt-2 font-smaller-7 font-weight-bold post_comment">COMMENT</a>
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
      like_count = like_count - 1;
    } else {
      $(this).addClass('open');
      like_count = like_count + 1;
    }
    let $ele = $(this).find('span.like_count');

    $ele.fadeOut(function() {
      $ele.text(like_count);
      $ele.fadeIn();
    });
  });


  // post comment activity
  $(document).on('click', '.comment_activity', function(e) {
    e.preventDefault();
    var success_callback = function($parent) {
      $parent.find('textarea').focus();
    };

    view_comments($(this), true, success_callback);
  });

  // post comment activity
  $(document).on('click', '.post_comment', function(e) {
    e.preventDefault();
    const $target = $(this).parents('.activity.box').find('.comment_activity');

    post_comment($target, false);
  });

  // https://stackoverflow.com/a/6015906/6784817
  function pasteIntoInput(el, text) {
      el.focus();
      if (typeof el.selectionStart == "number"
              && typeof el.selectionEnd == "number") {
          var val = el.value;
          var selStart = el.selectionStart;
          el.value = val.slice(0, selStart) + text + val.slice(el.selectionEnd);
          el.selectionEnd = el.selectionStart = selStart + text.length;
      } else if (typeof document.selection != "undefined") {
          var textRange = document.selection.createRange();
          textRange.text = text;
          textRange.collapse(false);
          textRange.select();
      }
  }

  function handleEnter(e) {
    if (e.which == 13) {
      if(e.keyCode == 13 && e.shiftKey){
        pasteIntoInput(this, "\n");
      } else {
        const $target = $(this).parents('.activity.box').find('.comment_activity');

        post_comment($target, false);
      }
      e.preventDefault();
    }
  }

  $(document).on('keypress', '.enter-activity-comment', handleEnter);

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

    $('.comment_activity').each(function() {
      var open = $(this).data('open');

      if (open) {
        $(this).data('open', false);
        view_comments($(this), true);
      }
    });

    $('.activity_detail_content span').each(function() {
      if (!$(this).hasClass('clean')) {
        let new_text = $(this).text();

        new_text = new_text.replace(/\</g, '_');
        new_text = new_text.replace(/\>/g, '_');
        new_text = new_text.replace(/&gt/g, '_');
        new_text = new_text.replace(/&lt/g, '_');
        new_text = new_text.replace(/\</g, '_');
        new_text = new_text.replace(/\>/g, '_');
        new_text = new_text.replace(/\n/g, '<BR>');
        new_text = urlify(new_text);
        new_text = linkify(new_text);
        $(this).html(new_text);
        $(this).addClass('clean');
      }
    });
  }, 1000);


}(jQuery));
