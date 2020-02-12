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

      const sendLeader = fetchData (url, 'POST', {'member': memberId}, {'X-CSRFToken': $("input[name='csrfmiddlewaretoken']").val()});

      $.when(sendLeader).then(function(response) {
        console.log(response);
        if(response['success'] && response['is_leader']) {
          $(elem).closest('.card').find('.badge-tribe_leader').removeClass('d-none');
          $(elem).closest('.card').find('.leader-promote').addClass('d-none');
          $(elem).closest('.card').find('.leader-demote').removeClass('d-none');
        } else if (response['success'] && !response['is_leader']) {
          $(elem).closest('.card').find('.badge-tribe_leader').addClass('d-none');
          $(elem).closest('.card').find('.leader-demote').addClass('d-none');
          $(elem).closest('.card').find('.leader-promote').removeClass('d-none');
        }
        $(elem).attr('disabled', false);
      }).fail(function(error) {
        $(elem).attr('disabled', false);
      });

    });
  });
};

tribeLeader();

const tribeAdmin = () => {
  $('[data-tribeadmin]').each(function(index, elem) {

    $(elem).on('click', function() {
      $(elem).attr('disabled', true);

      const memberId = $(elem).data('tribeadmin');
      const url = '/tribe/admin/';

      const sendAdmin = fetchData (url, 'POST', {'member': memberId}, {'X-CSRFToken': $("input[name='csrfmiddlewaretoken']").val()});

      $.when(sendAdmin).then(function(response) {
        console.log(response);
        if(response['success'] && response['is_admin']) {
          $(elem).closest('.card').find('.badge-tribe_admin').removeClass('d-none');
          $(elem).closest('.card').find('.admin-promote').addClass('d-none');
          $(elem).closest('.card').find('.admin-demote').removeClass('d-none');
        } else if (response['success'] && !response['is_admin']) {
          $(elem).closest('.card').find('.badge-tribe_admin').addClass('d-none');
          $(elem).closest('.card').find('.admin-demote').addClass('d-none');
          $(elem).closest('.card').find('.admin-promote').removeClass('d-none');
        }
        $(elem).attr('disabled', false);
      }).fail(function(error) {
        $(elem).attr('disabled', false);
      });

    });
  });
};

tribeAdmin();
