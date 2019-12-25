const checkUnrated = () => {
  let today = new Date();
  let lastPromp = new Date(localStorage.getItem('rateCapture')) || 0;
  let numDays = 7;

  if (!daysBetween(lastPromp, today, numDays)) {
    return;
  }

  let requestUnrated = fetchData ('/api/v0.1/unrated_bounties/', 'GET');

  $.when(requestUnrated).then((response, status, statusCode) => {
    if (statusCode.status != 200) {
      return _alert(response.msg, 'error');
    }

    if (response.unrated > 0) {
      ratingCaptureModal();
      localStorage.setItem('rateCapture', new Date());
    }

  });
};

const daysBetween = (d1, d2, numDays) => {
  let diff = Math.abs(d1.getTime() - d2.getTime());

  diff = diff / (1000 * 60 * 60 * 24);

  if (diff >= numDays) {
    return true;
  }
  return false;

};

const ratingCaptureModal = () => {
  let modalUrl = '/modal/rating_capture';

  $.ajax({
    url: modalUrl,
    type: 'GET',
    cache: false
  }).done(function(result) {
    $('body').append(result);
    $('#modalRating').bootstrapModal('show');

  });

  $(document, '#modalRating').on('hidden.bs.modal', function(e) {
    $('#modalRating').remove();
    $('#modalRating').bootstrapModal('dispose');
  });
};

checkUnrated();
