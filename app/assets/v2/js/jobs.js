$('.js-select2').each(function() {
  $(this).select2({
    minimumResultsForSearch: Infinity
  });
});

const save_job_status = function() {
  if (!document.contxt.github_handle) {
    _alert('No profile', 'error');
  }
  const formData = new FormData();
  const job_search_status = $('#jobStatus').find(':selected').val();
  const show_job_status = $('#showJobStatus').prop('checked');
  const job_type = $('input[name=jobType]:checked').map(function() {
                      return $(this).val()
                    }).get();
  const remote = $('#jobRemote:checked').val();
  const job_salary = $('#jobSalary').val();
  const linkedin_url = $('#linkedinUrl').val();
  const job_cv = $('#jobCV')[0].files;

  function checkUndefined(name, value) {
    if (typeof value !== 'undefined') {
      formData.append(name, value)
      console.log(name, value)
    }
  }

  const dataSend = {
    'job_cv':job_cv[0],
    'job_search_status': job_search_status,
    'show_job_status': show_job_status,
    'job_type': job_type,
    'remote': remote,
    'linkedin_url': linkedin_url,
    'job_salary': job_salary,
  }

  $.each(dataSend, (index, input) => {
    // console.log(index, input)
    checkUndefined(index, input)
  })

  formData.append('locations', JSON.stringify(jobLocations));

  const profile = {
    url: '/api/v0.1/profile/' + document.contxt.github_handle + '/jobopportunity',
    method: 'POST',
    headers: {'X-CSRFToken': csrftoken},
    data: formData,
    processData: false,
    dataType: 'json',
    contentType: false
  };

  $.ajax(profile).done(function(response) {
    _alert(response.message, 'info');
  }).fail(function(error) {
    _alert(error, 'error');
  });
};

// let jobLocations = [];
let autocomplete;

function initPlacecomplete() {
  let input = document.getElementById('jobLocation');

  var options = {
    types: ['(regions)']
  };

  autocomplete = new google.maps.places.Autocomplete(input, options);
  autocomplete.addListener('place_changed', function() {
    let place = autocomplete.getPlace();

    jobLocations.push(place);
    setLocations(jobLocations);
  });
}

const setLocations = (jobLocations) => {
  let locationsHtml = [];

  $.each(jobLocations, function(k, value) {
    locationsHtml.push(`<a class=filter-tag data-index=${k}><i class="fas fa-times"></i>${value.formatted_address}</a>`);
  });
  $('.locations-tags').html(locationsHtml);
  $('#jobLocation').val('');
};

const removeLocations = (index) => {
  jobLocations.splice(index, 1);
};

$('.locations-tags').on('click', '.filter-tag', function(e) {
  removeLocations($(this).data('index'));
  $(this).remove();
});

$('#jobSalary').on('change', function() {
  let currentValue = $(this).val();

  $(this).val(Number(currentValue.replace(',', '')).toLocaleString());
});


const checkFileSize = (elem, max_img_size) => {
  let input = document.getElementById(elem);

  if (input.files && input.files.length == 1) {
    if (input.files[0].size > max_img_size) {
      alert(`The file must be less than ${(max_img_size / 1024 / 1024).toFixed(2)}MB`);
      input.value = '';
      return false;
    }
  }
  return true;
};

$('#jobCV').on('change', () =>{
  checkFileSize('jobCV', 3144000);
});
