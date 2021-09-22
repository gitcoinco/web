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
    $('#edit-btn').addClass('btn-danger');
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
    _alert('Error saving description', 'danger');
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
  $('#edit-btn').removeClass('btn-danger');
};

const rebuildQuill = () => {
  const editorContainer = $('.editor-container');

  editorContainer.removeClass('inactive');
  quill.enable(true);
  $('#save-description-btn').removeClass('d-none');
  $('#edit-btn').addClass('btn-danger');
  $('#edit-btn i').removeClass('fa-edit');
  $('#edit-btn i').addClass('fa-times');
  $('#edit-btn span').text('Cancel');
};

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