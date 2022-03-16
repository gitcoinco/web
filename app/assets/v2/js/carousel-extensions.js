$(document).ready(function() {
  const dataAttr = 'carousel-item-href';

  $(`.carousel .carousel-item[data-${dataAttr}]`).on('click', function(event) {
    if (event.target.tagName.toLowerCase() === 'a') {
      return;
    }

    event.preventDefault();
    const href = $(event.currentTarget).data(dataAttr);

    if (href !== undefined) {
      document.location.href = href;
    }
  });
});
