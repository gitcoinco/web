/* eslint-disable no-prototype-builtins */

this.joinTribe = () => {
  $('[data-jointribe]').each(function(index, elem) {

    $(elem).on('click', function(e) {

      if (!document.contxt.github_handle) {
        e.preventDefault();
        _alert('Please login first.', 'danger');
        return;
      }

      $(elem).attr('disabled', true);
      e.preventDefault();
      const tribe = $(elem).data('jointribe');
      const url = `/tribe/${tribe}/join/`;
      const sendJoin = fetchData (url, 'POST', {}, {'X-CSRFToken': $("input[name='csrfmiddlewaretoken']").val()});

      $.when(sendJoin).then(function(response) {
        $(elem).attr('disabled', false);
        $(elem).attr('member', response.is_member);
        $(elem).toggleClass('btn-success').toggleClass('btn-primary');
        response.is_member ? $(elem).html('Unfollow <i class="fas fa-minus"></i>') : $(elem).html('Follow <i class="fas fa-plus"></i>');
        let old_count = parseInt($('#follower_count span').text());
        var new_count = response.is_member ? old_count + 1 : old_count - 1;

        $('#follower_count span').fadeOut();
        setTimeout(function() {
          $('#follower_count span').text(new_count).fadeIn();
        }, 500);
      }).fail(function(error) {
        $(elem).attr('disabled', false);
      });

    });
  });
};

joinTribe();

this.joinTribeDirect = (elem) => {

  if (!document.contxt.github_handle) {
    _alert('Please login first.', 'danger');
    return;
  }

  $(elem).attr('disabled', true);
  const tribe = $(elem).data('jointribe');
  const url = `/tribe/${tribe}/join/`;
  const sendJoin = fetchData (url, 'POST', {}, {'X-CSRFToken': $("input[name='csrfmiddlewaretoken']").val()});

  $.when(sendJoin).then(function(response) {
    $(elem).attr('disabled', false);
    $('[data-jointribe]').each((idx, ele) => {

      if (window.hasOwnProperty('tribesApp')) {
        window.tribesApp.is_on_tribe = true;
      }
      $(ele).attr('hidden', true);
    });
  }).fail(function(error) {
    $(elem).attr('disabled', false);
  });
};


this.followRequest = (handle, elem, cb, cbError) => {
  if (!document.contxt.github_handle) {
    _alert('Please login first.', 'danger');
    return;
  }

  const url = `/tribe/${handle}/join/`;
  const sendJoin = fetchData (url, 'POST', {}, {'X-CSRFToken': $("input[name='csrfmiddlewaretoken']").val()});

  $.when(sendJoin).then(function(response) {
    return cb(handle, elem, response);
  }).fail(function(error) {
    return cbError(error);
  });
};


this.tribeLeader = () => {
  $('[data-tribeleader]').each(function(index, elem) {

    $(elem).on('click', function() {
      $(elem).attr('disabled', true);

      const memberId = $(elem).data('tribeleader');
      const url = '/tribe/leader/';
      const template = '<span class="text-center text-uppercase font-weight-bold p-1 text-highlight-yellow">Tribe Leader</span>';

      const sendLeader = fetchData (url, 'POST', {'member': memberId}, {'X-CSRFToken': $("input[name='csrfmiddlewaretoken']").val()});

      $.when(sendLeader).then(function(response) {
        $(elem).after(template);
        $(elem).closest('.card').find('.badge-tribe_leader').removeClass('d-none');
        $(elem).remove();
      }).fail(function(error) {
        $(elem).attr('disabled', false);
      });

    });
  });
};

tribeLeader();

this.build_suggested_tribe = (tribe) => {
  return `
    <li class="nav-item d-flex justify-content-between align-items-center my-1">
      <a style="max-width: 70%;" href="/profile/${ tribe.title }" class="d-flex nav-link nav-line pr-0 mr-0">
        <img src="${tribe.avatar_url}" class="rounded-circle avatar mr-2" />
        <span class="font-caption">
          <span class="nav-title pt-0 mb-0">${tribe.title}</span>
          <span class="font-smaller-7">(${ tribe.follower_count } followers)</span>
        </span>
      </a>
      <div>
        <a class="follow_tribe btn btn-sm btn-primary font-weight-bold font-smaller-7 px-3" href="#" data-jointribe="${ tribe.title }">
          Follow
        </a>
        <button data-ignore-tribe="${ tribe.title }"  class="font-smaller-6 px-0 remove-tribe btn btn-link"><i class="fa fa-times"></i></button>
      </div>
    </li>`;
};

$(document).on('click', '.remove-tribe', function(e) {
  const element = e.target;

  if (!document.contxt.github_handle) {
    e.preventDefault();
    _alert('Please login first.', 'danger');
    return;
  }
  $(element).attr('disabled', true);

  e.preventDefault();
  let tribe;

  if ($(element).data('ignore-tribe')) {
    tribe = $(element).data('ignore-tribe');
  } else {
    tribe = $(element.parentElement).data('ignore-tribe');
  }


  const new_suggested_tribes = fetchData(`api/v0.1/ignore_suggested_tribes/${tribe}`, 'PUT');

  $.when(new_suggested_tribes).then((response) => {
    $('#suggested-tribes ul').fadeOut(300, function() {
      $(this).empty();

      response.tribes.map((tribe) => {
        const new_suggested_tribe = build_suggested_tribe(tribe);

        $('#suggested-tribes ul').append(new_suggested_tribe);
      });

    });

  });

});


this.newManageTribe = () => {
  $('[data-tribe]').each(function(index, elem) {
    $(elem).on('mouseenter focus', function(e) {
      if ($(elem).hasClass('btn-primary')) {
        $(elem).removeClass('btn-primary');
        $(elem).addClass('btn-success').text('Unfollow');
      }
    });

    $(elem).on('mouseleave focusout', function(e) {
      if ($(elem).hasClass('btn-primary')) {
        $(elem).removeClass('btn-primary');
        $(elem).addClass('btn-success').text('Following');
      }
    });

    $(elem).on('click', function(e) {
      if (!document.contxt.github_handle) {
        e.preventDefault();
        _alert('Please login first.', 'danger');
        return;
      }

      $(elem).attr('disabled', true);
      e.preventDefault();
      const tribe = $(elem).data('tribe');

      followRequest(tribe, elem, function(handle, elem, response) {
        $(elem).attr('disabled', false);
        $(elem).attr('member', response.is_member);
        if (response.is_member) {
          $(elem).addClass('btn-success').removeClass(['btn-primary']).text('Following');
        } else {
          $(elem).removeClass(['btn-success']).addClass('btn-primary').text('Follow');
        }
      }, function(error) {
        $(elem).attr('disabled', false);
      });
    });
  });
};

newManageTribe();
