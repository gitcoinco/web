/* eslint block-scoped-var: "warn" */
/* eslint no-redeclare: "warn" */

var build_detail_page = function(result) {
  result['posted_at'] = timeDifference(new Date(), new Date(result['posted_at']));
  var template = $.templates('#job_detail');

  html = template.render(result);

  $('#rendered_job_detail').html(html);
};

var pull_job_from_api = function() {
  var uri = '/api/v0.1/jobs/' + document.job_id + '/';

  $.get(uri, function(result) {
    result = sanitizeAPIResults(result);
    var nonefound = true;

    if (result) {
      nonefound = false;
      build_detail_page(result);
      document.result = result;
      $('#rendered_job_detail').css('display', 'block');
    }
    if (nonefound) {
      $('#rendered_job_detail').css('display', 'none');
      // is there a pending issue or not?
      $('.nonefound').css('display', 'block');
    }
  }).fail(function() {
    _alert({message: gettext('got an error. please try again, or contact support@gitcoin.co')}, 'error');
    $('#rendered_job_detail').css('display', 'none');
  }).always(function() {
    $('.loading').css('display', 'none');
  });
};

var main = function() {
  setTimeout(function() {
    pull_job_from_api();
  }, 100);
};


window.addEventListener('load', function() {
  main();
});
