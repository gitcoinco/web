$(document).ready(function() {
  $(".carousel .carousel-item").on("click", function(event) {
    if (event.target.tagName.toLowerCase() === 'a') {
      return;
    }

    event.preventDefault();

    const href = $(event.currentTarget).data('carousel-item-href');

    if (href !== undefined) {
      document.location.href = href;
    }
  });
})
