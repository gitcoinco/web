let quill;
let quill_priority;

$('#edit-btn').on('click', function() {

  const activateQuill = () => {
    if (quill) {
      return quill.isEnabled() ? destroyQuill() : rebuildQuill();
    }
    quill = new Quill('#description-tribes', {
      modules: {
        toolbar: [
          [{ header: [ 1, 2, false ] }],
          [ 'bold', 'italic', 'underline' ],
          [{ 'align': [] }],
          [ 'link', 'image', 'code-block' ],
          ['clean']
        ]
      },
      theme: 'snow',
      placeholder: 'Compose an epic description for your Tribe...'
    });
    $('#save-description-btn').removeClass('d-none');
    $('#edit-btn i').removeClass('fa-edit');
    $('#edit-btn i').addClass('fa-times');
    $('#edit-btn span').text('Cancel');
    $('#edit-btn').addClass('btn-gc-pink');
    return quill;
  };

  if (!document.getElementById('quill-js')) {
    const style = document.createElement('link');

    style.href = '//cdn.jsdelivr.net/npm/quill@1.3.6/dist/quill.snow.css';
    style.type = 'text/css';
    style.rel = 'stylesheet';
    document.getElementsByTagName('head')[0].appendChild(style);
  }
  loadDynamicScript(activateQuill, 'https://cdn.jsdelivr.net/npm/quill@1.3.6/dist/quill.min.js', 'quill-js');

});

const loadDynamicScript = (callback, url, id) => {
  const existingScript = document.getElementById(id);

  if (!existingScript) {
    const script = document.createElement('script');

    script.src = url;
    script.id = id;
    document.body.appendChild(script);

    script.onload = () => {
      if (callback)
        callback();
    };
  }

  if (existingScript && callback)
    callback();
};

$('[data-savetribe]').on('click', function() {
  const tribe = $(this).data('savetribe');
  const url = `/tribe/${tribe}/save/`;
  const sendSave = fetchData (
    url,
    'POST',
    {'tribe_description': quill.root.innerHTML},
    {'X-CSRFToken': $("input[name='csrfmiddlewaretoken']").val()}
  );

  $.when(sendSave).then(function(response) {
    destroyQuill();
    _alert('Description saved');
  }).fail(function(error) {
    _alert('Error saving description', 'error');
  });
});

const destroyQuill = () => {
  const editorContainer = $('.editor-container');

  editorContainer.addClass('inactive');
  quill.enable(false);
  $('#save-description-btn').addClass('d-none');
  $('#edit-btn i').addClass('fa-edit');
  $('#edit-btn span').text('Edit');
  $('#edit-btn i').removeClass('fa-times');
  $('#edit-btn').removeClass('btn-gc-pink');
};

const rebuildQuill = () => {
  const editorContainer = $('.editor-container');

  editorContainer.removeClass('inactive');
  quill.enable(true);
  $('#save-description-btn').removeClass('d-none');
  $('#edit-btn').addClass('btn-gc-pink');
  $('#edit-btn i').removeClass('fa-edit');
  $('#edit-btn i').addClass('fa-times');
  $('#edit-btn span').text('Cancel');
};

if ($('#edit-tribe_priority').length) {

  $('[data-updatepriority]').on('click', function() {
    const tribe = $(this).data('updatepriority');
    const url = `/tribe/${tribe}/save/`;
    const text = quill_priority.root.innerHTML;

    const sendSave = fetchData(
      url,
      'POST',
      {
        'tribe_priority': text,
        'publish_to_ts': $('#post-to-ts').is(':checked'),
        'priority_html_text': quill_priority.getText('')
      },
      {'X-CSRFToken': $("input[name='csrfmiddlewaretoken']").val()}
    );

    $.when(sendSave).then(function(response) {
      _alert('Tribe Priority has been updated');
      $('#priority-text').html(text);
      $('#priority-text-container').removeClass('hidden');
      $('#placeholder-text').addClass('hidden');
      quill_priority.setText('');
    }).fail(function(error) {
      _alert('Error saving priorites. Try again later', 'error');
      console.error('error: unable to save priority', error);
    });
  });

  const activateQuill = () => {
    quill_priority = new Quill('#edit-tribe_priority', {
      modules: {
        toolbar: [
          [ 'bold', 'italic', 'underline' ],
          [{ 'align': [] }],
          [ 'link', 'code-block' ],
          ['clean']
        ]
      },
      theme: 'snow',
      placeholder: 'List out your tribe priorities to let contributors to know what they can request to work on'
    });

    return quill_priority;
  };

  const style = document.createElement('link');

  style.href = '//cdn.jsdelivr.net/npm/quill@1.3.6/dist/quill.snow.css';
  style.type = 'text/css';
  style.rel = 'stylesheet';
  document.getElementsByTagName('head')[0].appendChild(style);

  loadDynamicScript(activateQuill, 'https://cdn.jsdelivr.net/npm/quill@1.3.6/dist/quill.min.js', 'quill-js');
}

tokens(document.web3network).forEach(function(ele) {
  let option = document.createElement('option');

  option.text = ele.name;
  option.value = ele.addr;

  $('#token').append($('<option>', {
    value: ele.addr,
    text: ele.name
  }));
});
$('select[name=denomination]').select2();

$('[data-createbountyrequest]').on('click', function() {

  const githubUrl = $('#githubUrl').val();
  const tokenName = tokenAddressToDetails($('#token').val())['name'];
  const comment = $('#comment').val();
  const tribe = $(this).data('createbountyrequest');
  const url = '/api/v1/bounty_request/create';
  const amount = $('#amount').val();

  fetchIssueDetailsFromGithub(githubUrl).then(result => {
    const title = result.title;

    const createBountyRequest = fetchData(
      url,
      'POST',
      {
        'github_url': githubUrl,
        'tribe': tribe,
        'comment': comment,
        'token_name': tokenName,
        'amount': amount,
        'title': title
      },
      {'X-CSRFToken': $("input[name='csrfmiddlewaretoken']").val()}
    );

    $.when(createBountyRequest).then(function(response) {

      if (response.status == 204) {
        _alert('Bounty Request has been created');
        location.reload();
      } else {
        _alert(`Error creating bounty request as ${response.message}`, 'error');
        console.error(response.message);
      }

    }).fail(function(error) {
      _alert(`Error creating bounty request as ${error}`, 'error');
      console.error('error: unable to creating bounty request', error);
    });
  }).catch(error => {
    _alert(`Error creating bounty request as ${error}`, 'error');
    console.error('error: unable to creating bounty request', error);
  });
});

$('[data-cancelbountyrequest]').on('click', function() {
  const bounty_request_id = $(this).data('cancelbountyrequest');
  const url = '/api/v1/bounty_request/update';

  const createBountyRequest = fetchData(
    url,
    'POST',
    {
      'bounty_request_id': bounty_request_id,
      'request_status': 'c'
    },
    {'X-CSRFToken': $("input[name='csrfmiddlewaretoken']").val()}
  );

  $.when(createBountyRequest).then(function(response) {

    if (response.status == 200) {
      _alert('Bounty Request has been rejected');
      $(`#${bounty_request_id}`).hide();
    } else {
      _alert(`Error rejecting bounty request as ${response.message}`, 'error');
      console.error(response.message);
    }

  }).fail(function(error) {
    _alert(`Error rejecting bounty request. ${error}`, 'error');
    console.error('error: unable to reject bounty request', error);
  });
});
