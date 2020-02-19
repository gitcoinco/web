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


const tribeLeader = () => {
  $('[data-tribeleader]').each(function(index, elem) {

    $(elem).on('click', function() {
      $(elem).attr('disabled', true);

      const memberId = $(elem).data('tribeleader');
      const url = '/tribe/leader/';

      const sendLeader = fetchData (url, 'POST', {'member': memberId}, {'X-CSRFToken': $("input[name='csrfmiddlewaretoken']").val()});

      $.when(sendLeader).then(function(response) {
        console.log(response);
        if (response['success'] && response['is_leader']) {
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
        if (response['success'] && response['is_admin']) {
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
