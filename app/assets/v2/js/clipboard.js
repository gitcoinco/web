/*
 *  Copy the string from the input / textarea into the system clipboard
 *  @example
 *  <textarea id="shareText">This text will be copied</textarea>
 *  <button data-copyclipboard="#shareText">Copy Text</button>
 */
const copyClipboard = () => {
  $('[data-copyclipboard]').each(function(index, elem) {
    $(this).on('click', function() {
      let input = $(this).data('copyclipboard');

      $(input).select();
      document.execCommand('copy');
      document.getSelection().removeAllRanges();
      let msgDone = $('<b style="position: absolute;margin: 0.2rem -3.2rem;">Copied!</b>');

      $(input).after(msgDone);
      msgDone.animate({
        opacity: 1
      }, 5000, function() {
        $(this).remove();
      });
    });
  });
};
