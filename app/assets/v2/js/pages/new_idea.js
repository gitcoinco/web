$('document').ready(() => {

  initCharCounter('#summary', '#summary_chars');
  initCharCounter('#more_info', '#more_info_chars');

  $('#create_idea').click(() => {
    if (!$('#new_idea_form').valid())
      return false;

    var fullName = $('#full_name').val();
    var email = $('#email').val();
    var githubUsername = $('#github_username').val();
    var summary = $('#summary').val();
    var moreInfo = $('#more_info').val();
    var lookingForCapital = $('#capital_looking').is(':checked');
    var lookingForBuilders = $('#builders_looking').is(':checked');
    var lookingForDesigners = $('#designers_looking').is(':checked');
    var lookingForCustomers = $('#customers_looking').is(':checked');
    var capitalExists = $('#capital_exists').is(':checked');
    var buildersExists = $('#builders_exists').is(':checked');
    var designersExists = $('#designers_exists').is(':checked');
    var customerExists = $('#customers_exists').is(':checked');

    $.post('create', JSON.stringify({
      'full_name': fullName,
      'email': email,
      'github_username': githubUsername,
      'summary': summary,
      'more_info': moreInfo,
      'looking_for_capital': lookingForCapital,
      'looking_for_builders': lookingForBuilders,
      'looking_for_designers': lookingForDesigners,
      'looking_for_customers': lookingForCustomers,
      'capital_exists': capitalExists,
      'builders_exists': buildersExists,
      'designers_exists': designersExists,
      'customer_exists': customerExists
    }), (result) => {
      document.location.href = 'idea/' + result.ideaId + '/show';
    }, 'json');
  });

  // prevent submission, keep form validation...
  $('#new_idea_form').submit(function() {
    console.log('submit');
    return false;
  });

});

function initCharCounter(inputId, counterElementId) {
  $(inputId).keyup(function() {
    $(counterElementId).text($(this).val().length);
  });
}