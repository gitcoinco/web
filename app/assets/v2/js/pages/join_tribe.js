const joinTribe = () => {
  $('[data-jointribe]').each(function(index, elem) {

    $(elem).on('click', function() {
      $(elem).attr('disabled', true);

      const tribe = $(elem).data('jointribe');
      const url = `/tribe/${tribe}/join/`;
      const sendJoin = fetchData (url, 'POST', {}, {'X-CSRFToken': $("input[name='csrfmiddlewaretoken']").val()});

      $.when(sendJoin).then(function(response) {
        $(elem).attr('disabled', false);
        response.is_member ? $(elem).text('Leave Tribe') : $(elem).text('Join Tribe');

      }).fail(function(error) {
        $(elem).attr('disabled', false);
      });

    });
  });
};

joinTribe();


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
