
function setupTabs(name) {
  let sections = document.querySelector(name + '-sections.tab-sections');

  if (!sections) {
    return;
  }
  let buttons = document.querySelector(name).lastChild;
  let firstButton = null;
  let last = null;

  function onClick(evt) {
    const section = sections.querySelector('#section-' + evt.target.id);

    if (last) {
      last.className = last.className.replace(' active', '');
    }
    $(sections).find('.tab-section').removeClass('active');
    evt.target.className += ' active';
    section.className += ' active';
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
