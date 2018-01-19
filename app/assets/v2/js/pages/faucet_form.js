 $('document').ready(function () {
    $('#comment').bind('input propertychange', function() {
      this.value = this.value.replace(/ +(?= )/g,'');
      if(this.value.length > 500) {
        this.value = this.value.substring(0, 500);
      }
      if(this.value.length){
        $("#charcount").html(501 - this.value.length);
      }
    });
    $('#githubProfile').on('change', function() {
      var cleanedUser = this.value.replace('@','').toLowerCase();
      request_url = '/api/v0.1/faucet/githubProfile/' + cleanedUser;
      document.getElementById("submitFaucet").setAttribute("disabled","disabled");
      $.get(request_url, function(result){
        result = sanitizeAPIResults(result);
        if(result.user === false) {
          $('#githubProfile').addClass('is-invalid');
          $('#githubProfileHelpBlock').html('We could not find that user in Github').show();
        } else if(result.name === cleanedUser) {
          $('#githubProfile').addClass('is-invalid-error');
          $('#githubProfileHelpBlock').html('We have a pending or processed faucet contribution for that Github user').show();
        }
        $("#submitFaucet").removeAttr("disabled");
      });
    });
    $('#githubProfile').on('focus', function() {
      $('#githubProfileHelpBlock').hide();
      $('#githubProfile').removeClass('is-invalid');
    });
    $('#emailAddress').on('focus', function() {
      $('#emailAddressHelpBlock').hide();
      $('#emailAddress').removeClass('is-invalid');
    });
    $('#emailAddress').on('change', function() {
      var exp = /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
      if(!exp.test(this.value)) {
        $('#emailAddress').addClass('is-invalid');
        $('#emailAddressHelpBlock').html('We could not validate that input as an email address').show();
      }
    });
    $('#submitFaucet').on('click', function(e) {
      e.preventDefault()
      if(e.target.hasAttribute('disabled') ||
       $('#githubProfile').is(['is-invalid']) ||
       $('#emailAddress').is(['is-invalid']) ||
       $('#githubProfile').val()==='' ||
       $('#emailAddress').val()==='') {
        return;
      }
      var faucetRequestData={
          'githubProfile': $('#githubProfile').val().replace('@',''),
          'ethAddress': $('#ethAddress').val(),
          'emailAddress': $('#emailAddress').val(),
          'comment': $('#comment').val(),
          'csrfmiddlewaretoken': $('input[name="csrfmiddlewaretoken"]').val()
      }
      $.post('/api/v0.1/faucet/save', faucetRequestData)
      .done(function(d) {
        $('#main_form').hide();
        $('#success_container').show();
      })
      .fail(function(e) {
        $('#main_form').hide();
        $('#fail_message').html(e.responseJSON.message);
        $('#fail_container').show();
      });
    })
 });
