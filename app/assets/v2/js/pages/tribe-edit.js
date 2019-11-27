let quill;

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
    return quill;
  };

  if (!document.getElementById('quill-js')) {
    const style = document.createElement('link');

    style.href = '//cdn.quilljs.com/1.3.6/quill.snow.css';
    style.type = 'text/css';
    style.rel = 'stylesheet';
    document.getElementsByTagName('head')[0].appendChild(style);
  }
  loadDynamicScript(activateQuill, 'https://cdn.quilljs.com/1.3.6/quill.js', 'quill-js');

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
};

const rebuildQuill = () => {
  const editorContainer = $('.editor-container');

  editorContainer.removeClass('inactive');
  quill.enable(true);
  $('#save-description-btn').removeClass('d-none');
};
