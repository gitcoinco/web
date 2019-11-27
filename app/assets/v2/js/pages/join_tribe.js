const joinTribe = () => {
  $('[data-jointribe]').each(function(index, elem) {

    $(elem).on('click', function() {
      $(elem).attr('disabled', true);

      let tribe = $(elem).data('jointribe');
      let url = `/join/${tribe}/`;


      var sendJoin = fetchData (url, 'POST',{}, {'X-CSRFToken': $("input[name='csrfmiddlewaretoken']").val()});

      $.when(sendJoin).then(function(response) {
        $(elem).attr('disabled', false);
        console.log(response)
        if (response.is_member) {
          $(elem).text('Leave Tribe');
        } else {
          $(elem).text('Join Tribe');
        }

      }).fail(function(test){
        console.log(test)
        // $(elem).attr('disabled', true);
      })

    });
  })
}
joinTribe();


const tribeLeader = () => {
  $('[data-tribeleader]').each(function(index, elem) {

    $(elem).on('click', function() {
      $(elem).attr('disabled', true);

      let memberId = $(elem).data('tribeleader');
      let url = 'tribe/tribeleader/';
      const template = `<span class="text-center text-uppercase font-weight-bold p-1 text-highlight-yellow">Tribe Leader</span>`;


      var sendLeader = fetchData (url, 'POST',{'member':memberId}, {'X-CSRFToken': $("input[name='csrfmiddlewaretoken']").val()});

      $.when(sendLeader).then(function(response) {
        $(elem).after(template);
        $(elem).closest('.card').find('.badge-tribe_leader').removeClass('d-none')
        $(elem).remove()
      }).fail(function(error){
        $(elem).attr('disabled', false);
      })

    });
  })
}
tribeLeader();
