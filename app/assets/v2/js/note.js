const movementStrength = 25;
let startX = null;
let startY = null;
let mouseX = 0;
let mouseY = 0;
let scrollContainer;
const moveBackground = RAFThrottle(e => {
  mouseY = e.pageY || mouseY;
  const pageY = mouseY - ($(window).height() / 2) -
    ((scrollContainer === window) ? window.scrollY : scrollContainer.scrollTop()) * 2;
  let newvalueY = movementStrength / $(window).height() * pageY;

  $('.gitcoin-background').css('background-position', ` center ${newvalueY}px`);
});

$(document).ready(function() {
  scrollContainer = scrollContainer || $(window); // Allows overriding page scroll container

  $('.header, .white-light-bg').each(function(index, element) {
    $(element).mousemove(e => {
      const pageX = e.pageX - ($(window).width() / 2);
      const pageY = e.pageY - ($(window).height() / 2);
      const newvalueX = movementStrength / $(window).width() * (pageX - startX) * -1 - 25;
      const newvalueY = movementStrength / $(window).height() * (pageY - startY) * -1 - 50;

      if (!startX) {
        startX = newvalueX;
      }

      if (!startY) {
        startY = newvalueY;
      }

      $(element).css('background-position', `${newvalueX - startX}px ${newvalueY - startY}px`);
    });
  });

  const $navbar = $('.navbar');
  const $header = $('.header');

  $navbar.mousemove(moveBackground);
  $header.mousemove(moveBackground);
  scrollContainer.scroll(moveBackground);
});

function RAFThrottle(f) {
  let throttledHandler;

  return function() {
    if (throttledHandler) {
      return;
    }

    throttledHandler = requestAnimationFrame(() => {
      f(...arguments);
      throttledHandler = undefined;
    });
  };
}
