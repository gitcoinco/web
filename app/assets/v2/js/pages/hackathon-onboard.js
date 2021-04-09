let quill;

$('#edit-btn').on('click', function() {
  const activateQuill = () => {
    if (quill) {
      return quill.isEnabled() ? destroyQuill() : rebuildQuill();
    }
    quill = new Quill('#description-hackathon', {
      modules: {
        toolbar: [
          [{ header: [ 1, 2, 3, 4, 5, 6, false ] }],
          [ 'bold', 'italic', 'underline', 'strike' ],
          [{ 'size': [ 'small', false, 'large', 'huge' ] }],
          [{ 'color': [] }, { 'background': [] }],
          [{ 'font': [] }],
          [{ 'align': [] }],
          [{ 'list': 'ordered'}, { 'list': 'bullet' }],
          [{ 'indent': '-1'}, { 'indent': '+1' }],
          [{ 'direction': 'rtl' }],
          [ 'blockquote', 'code-block', 'link', 'image', 'video' ],
          ['clean']
        ]
      },
      theme: 'snow',
      placeholder: 'Compose an epic description for your Tribe...'
    });
    $('#save-description-btn').removeClass('d-none');
    return quill;
  };

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

$('[data-savehackathon]').on('click', function() {
  const slug = $(this).data('savehackathon');
  const url = `/api/v0.1/hackathon/${slug}/save/`;
  const sendSave = fetchData (
    url,
    'POST',
    {'description': quill.root.innerHTML},
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
};

const rebuildQuill = () => {
  const editorContainer = $('.editor-container');

  editorContainer.removeClass('inactive');
  quill.enable(true);
  $('#save-description-btn').removeClass('d-none');
};
