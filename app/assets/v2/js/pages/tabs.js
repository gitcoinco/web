
function setupTabs(name) {
  var indicator = document.querySelector(name + '.tab-indicator');
  var container = indicator.parentElement.parentElement;
  var sections = container.querySelector(name + '.tab-sections');
  var buttons = indicator.previousElementSibling;
  var firstButton = null;
  var last = null;

  function onClick(evt) {
    var width = evt.target.offsetWidth;
    var offset = evt.target.offsetLeft;
    var section = sections.querySelector('#' + evt.target.id);

    indicator.style.width = width + 'px';
    indicator.style.transform = 'translateX(' + offset + 'px)';

    if (last) {
      last.className = last.className.replace(' active', '');
    }

    evt.target.className += ' active';
    offset = -section.offsetLeft;
    sections.style.transform = 'translateX(' + offset + 'px)';
    last = evt.target;
  }

  while (buttons !== null) {
    buttons.addEventListener('click', onClick, false);

    firstButton = buttons;
    buttons = buttons.previousElementSibling;
    if (buttons === null) {
      // initial setup
      onClick({ target: firstButton });
    }
  }
}
