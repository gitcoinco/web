document.addEventListener('DOMContentLoaded', () => {

  const tabs = document.querySelectorAll('.hackathon-tabs a');
  const hacks = document.querySelectorAll('.hackathon-list');

  const loadTab = (target) => {
    let hiddenRows = false;

    const hack = document.querySelector('.hackathon-list.' + target);
    const rows = document.querySelectorAll('.hackathon-list.' + target + ' > .row');
    const more = document.querySelector('.hackathon-list.' + target + ' > .view-more');

    tabs.forEach((t) => t.classList.remove('active'));
    document.querySelector('.nav-link[data-href="' + target + '"]').classList.add('active');

    hacks.forEach((hack) => hack.classList.add('hidden'));
    hack.classList.remove('hidden');

    rows.forEach((row, indx) => {
      if (indx > 1 && more.classList.contains('d-none')) {
        hiddenRows = true;
        row.classList.add('d-none');
      }
    });

    if (hiddenRows && more) {
      const newMore = more.cloneNode(true);

      more.parentNode.replaceChild(newMore, more);
      newMore.classList.add('d-block');
      newMore.classList.remove('d-none');
      newMore.addEventListener('click', () => {
        newMore.classList.add('d-none');
        newMore.classList.remove('d-block');
        rows.forEach((hack) => hack.classList.remove('d-none'));
      });
    }
  };

  tabs.forEach((tab) => {
    tab.addEventListener('click', (e) => {
      e.preventDefault();
      loadTab(e.target.dataset.href);
    });
  });

  loadTab(document.default_tab);
});
