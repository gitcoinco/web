const joinTribe = () => {
  $('[data-jointribe]').each(function(index, elem) {

    $(elem).on('click', function(e) {

      if (!document.contxt.github_handle) {
        e.preventDefault();
        _alert('Please login first.', 'error');
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

const joinTribeDirect = (elem) => {

  if (!document.contxt.github_handle) {
    _alert('Please login first.', 'error');
    return;
  }

  $(elem).attr('disabled', true);
  const tribe = $(elem).data('jointribe');
  const url = `/tribe/${tribe}/join/`;
  const sendJoin = fetchData (url, 'POST', {}, {'X-CSRFToken': $("input[name='csrfmiddlewaretoken']").val()});

  $.when(sendJoin).then(function(response) {
    $(elem).attr('disabled', false);
    $(elem).attr('member', response.is_member);
    $(elem).attr('hidden', true);
  }).fail(function(error) {
    $(elem).attr('disabled', false);
  });
};


const followRequest = (handle, elem, cb, cbError) => {
  if (!document.contxt.github_handle) {
    _alert('Please login first.', 'error');
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


const tribeLeader = () => {
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

const hideTribe = () => {
  $('[data-hidetribe]').each(function(index, element) {
    $(element).on('click', function() {
      const tribeId = $(element).data('hidetribe');

      const url = `/tribe/${tribeId}/remove/`;
      const removeTribe = fetchData (url, 'POST', {}, {'X-CSRFToken': $("input[name='csrfmiddlewaretoken']").val()});

      $.when(removeTribe).then(function(response) {
        console.log(response)
        $(element).parent('#suggestedTribe').remove();
        // fetch new tribes
        fetchSuggestedTribes()
      }).fail(function(error){
        // throw some errors to the user
        _alert('An error occured. Please try again.', 'error');
      })
    })
  })
}

hideTribe()

const fetchSuggestedTribes = () => {
  const url = '/api/v0.1/suggested_tribes';
  const suggestedTribes = fetchData (url, 'GET', {});
  $.when(suggestedTribes).then(function(response) {
    console.log(response)
  }).fail(function(error){
    // throw some errors to the user
    _alert('Failed to load suggested tribes. Please try again', 'error');
  })
}

fetchSuggestedTribes()