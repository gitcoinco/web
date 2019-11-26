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
