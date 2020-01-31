
$(document).ready(function() {

  document.base_title = $('title').text();

  $('#activity_subheader').remove();

  // notifications of new activities
  var ping_activity_notifier = (function() {
    var plural = document.buffered_rows.length == 1 ? 'y' : 'ies';
    var html = '<div id=new_activity_notifier>' + document.buffered_rows.length + ' New Activit' + plural + ' - Click to View</div>';

    if ($('#new_activity_notifier').length) {
      $('#new_activity_notifier').html(html);
    } else {
      $(html).insertBefore($('#activities .row').first());
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
        max_pk = $('#activities .row').first().data('pk');
        if (!max_pk) {
          return;
        }
      }
      // get new activities
      var url = $('.infinite-more-link').attr('href').split('page')[0];

      url += '&after-pk=' + max_pk;
      $.get(url, function(html) {
        var new_row_number = $(html).find('.activity.row').first().data('pk');

        if (new_row_number && new_row_number > max_pk) {
          max_pk = new_row_number;
          $(html).find('.activity.row').each(function() {
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
    if ($('#activities .row').length) {
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

    // update UI
    $(this).parents('.row.box').remove();

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
  $(document).on('click', '.tip_activity', function(e) {
    if (!document.contxt.github_handle) {
      _alert('Please login first.', 'error');
      return;
    }
    if (!web3) {
      _alert('Please enable and unlock your web3 wallet.', 'error');
      return;
    }

    var $amount = $(this).find('.amount');

    const email = '';
    const github_url = '';
    const from_name = document.contxt['github_handle'];
    const username = $(this).data('username');
    const amountInEth = parseFloat(prompt('How much ETH do you want to give?', '0.01').replace('ETH', ''));

    if (amountInEth < 0.001) {
      _alert('Amount must be 0.001 or more.', 'error');
      return;
    }
    const comments_priv = 'activity:' + $(this).data('pk');
    const comments_public = '';
    const accept_tos = (confirm("Do you accept Gitcoin's terms of service at gitcoin.co/terms ?"));
    const from_email = '';
    const tokenAddress = '0x0';
    const expires = 9999999999;
    var $parent = $(this);
    var success_callback = function(txid) {
      const url = 'https://' + etherscanDomain() + '/tx/' + txid;
      const msg = 'This payment has been sent 👌 <a target=_blank href="' + url + '">[Etherscan Link]</a>';

      var old_amount = $amount.text();
      var new_amount = Math.round(100 * parseFloat(old_amount) + parseFloat(amountInEth)) / 100;

      $amount.fadeOut().text(new_amount).fadeIn();
      setTimeout(function() {
        var $target = $parent.parents('.row.box').find('.comment_activity');

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

    var parent = $(this).parents('.row.box');

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
    var comment = prompt('What is your comment?', '');

    // validation
    if (!comment) {
      return;
    }

    $parent.parents('.row.box').find('.loading').removeClass('hidden');

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
      view_comments($parent, allow_close_comment_container);
    }).done(function() {
      // pass
    })
      .fail(function() {
        $parent.parents('.row.box').find('.error').removeClass('hidden');
      })
      .always(function() {
        $parent.parents('.row.box').find('.loading').addClass('hidden');
      });
  };

  var view_comments = function($parent, allow_close_comment_container) {

    // remote post
    var params = {
      'method': 'comment'
    };
    var url = '/api/v0.1/activity/' + $parent.data('pk');

    var $target = $parent.parents('.row.box').find('.comment_container');

    if ($target.hasClass('filled') && allow_close_comment_container) {
      $target.html('');
      $target.removeClass('filled');
      $parent.find('.action').removeClass('open');
      return;
    }
    $parent.find('.action').addClass('open');
    $parent.parents('.row.box').find('.loading').removeClass('hidden');
    $.get(url, params, function(response) {
      $parent.parents('.row.box').find('.loading').addClass('hidden');
      $target.addClass('filled');
      $target.html('');
      for (var i = 0; i < response['comments'].length; i++) {
        var comment = sanitizeAPIResults(response['comments'])[i];
        var timeAgo = timedifferenceCvrt(new Date(comment['created_on']));
        var html = '<li><a href=/profile/' + comment['profile_handle'] + '><img src=/dynamic/avatar/' + comment['profile_handle'] + '></a> <a href=/profile/' + comment['profile_handle'] + '>' + comment['profile_handle'] + '</a>, ' + timeAgo + ': ' + comment['comment'] + '</li>';

        $target.append(html);
      }
      $target.append('<a href=# class=post_comment>Post comment &gt;</a>');
    });
  };

  // post comment activity
  $(document).on('click', '.comment_activity', function(e) {
    e.preventDefault();
    var num = $(this).find('span.num').html();

    if (parseInt(num) == 0) {
      post_comment($(this), true);
    } else {
      view_comments($(this), true);
    }
  });

  // post comment activity
  $(document).on('click', '.post_comment', function(e) {
    e.preventDefault();
    var $target = $(this).parents('.row.box').find('.comment_activity');

    post_comment($target, false);
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

    $('.comment_activity').each(function() {
      var open = $(this).data('open');

      if (open) {
        $(this).data('open', false);
        $(this).click();
      }
    });

    $('.activity.wall_post .activity-status b, .activity.status_update .activity-status b').each(function() {
      let new_text = $(this).text();

      new_text = new_text.replace('&lt;', '_');
      new_text = new_text.replace('&gt;', '_');
      new_text = new_text.replace('>', '_');
      new_text = new_text.replace('<', '_');
      new_text = urlify(new_text);
      new_text = new_text.replace(/#(\S*)/g, '<a href="/?tab=search-$1">#$1</a>');
      new_text = new_text.replace(/@(\S*)/g, '<a href="/profile/$1">@$1</a>');
      $(this).html(new_text);
    });

    // inserts links into the text where there are URLS detected
    function urlify(text) {
      var urlRegex = /(https?:\/\/[^\s]+)/g;

      return text.replace(urlRegex, function(url) {
        return '<a target=blank rel=nofollow href="' + url + '">' + url + '</a>';
      });
    }

  }, 1000);


}(jQuery));
