// preloading all images on a small interval
var interval = 500;

$(document).ready(function() {
  $.fn.isInViewport = function() {
    var elementTop = $(this).offset().top;
    var elementBottom = elementTop + $(this).outerHeight();
    var viewportTop = $(window).scrollTop();
    var viewportBottom = viewportTop + $(window).height();

    return elementBottom > viewportTop && elementTop < viewportBottom;
  };

  $(window).on('hashchange', function(evt) {
    $('#toc a').each(function() {
      $(this).removeClass('active');

      if ($(this).attr('href') === window.location.hash) {
        $(this).addClass('active');
      }
    });
  });

  $(window).scroll(function() {
    var scrollPos = $(document).scrollTop();

    if (parseInt(scrollPos) % 100 < 10) {
      $('#toc a').removeClass('active');
      $('#toc a').each(function() {
        var href = $(this).attr('href');
        var target_selector = href;

        if ($(target_selector).isInViewport()) {
          if ($('#toc a.active').length < 1) {
            $(this).addClass('active');
          }
        }
      });
    }
  });

  function markVote(toolId, direction, scoreDelta) {
    var upVoteButton = $('#' + toolId + '_vote .vote-up');
    var downVoteButton = $('#' + toolId + '_vote .vote-down');
    var activeVoteClass = 'active';

    upVoteButton.removeClass(activeVoteClass);
    downVoteButton.removeClass(activeVoteClass);

    if (direction == 1 && scoreDelta > 0)
      upVoteButton.addClass(activeVoteClass);

    if (direction == -1 && scoreDelta < 0)
      downVoteButton.addClass(activeVoteClass);
  }

  function voteCallback(response, toolId, direction) {
    var scoreEl = $('#' + toolId + '_vote .score');
    var scoreDelta = response.score_delta;

    markVote(toolId, direction, scoreDelta);
    scoreEl.text(parseInt(scoreEl.text()) + scoreDelta);
  }

  function failVoteCallback(response) {
    _alert({ message: response.responseJSON.error }, 'error');
  }

  $('.vote-up').on('click', function() {
    var el = $(this);
    var toolId = el.data('tool-id');

    $.post('/actions/tool/' + toolId + '/voteUp', {}, function(response) {
      voteCallback(response, toolId, 1);
    }).fail(failVoteCallback);
  });
  $('.vote-down').on('click', function() {
    var el = $(this);
    var toolId = el.data('tool-id');

    $.post('/actions/tool/' + toolId + '/voteDown', {}, function(response) {
      voteCallback(response, toolId, -1);
    }).fail(failVoteCallback);
  });

});
