const _toast = (msg, type) => {
  const VISIBLE_TIME = 3000;

  if (!msg)
    return;

  var html = `<div id="g-toast" class="font-caption text-center g-toasts show ${type}">${msg}</div>`;

  $('body').append(html);

  setTimeout(() => {
    const toast = $('.g-toasts').get(0);

    toast.className.replace('show', '');
    toast.remove();
  }, VISIBLE_TIME);
};