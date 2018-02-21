$(document).ready(function() {
  let startX = null;
  let startY = null;
  const movementStrength = 25;
  const height = movementStrength / $(window).height();
  const width = movementStrength / $(window).width();

  $('.header, .white-light-bg').each(function(index, element) {
    $(element).mousemove(e => {
      const pageX = e.pageX - ($(window).width() / 2);
      const pageY = e.pageY - ($(window).height() / 2);
      const newvalueX = width * (pageX - startX) * -1 - 25;
      const newvalueY = height * (pageY - startY) * -1 - 50;

      if (!startX) {
        startX = newvalueX;
      }

      if (!startY) {
        startY = newvalueY;
      }

      $(element).css('background-position', `${newvalueX - startX}px ${newvalueY - startY}px`);
    });
  });
});
