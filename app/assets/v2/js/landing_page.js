
// Header and Nav
$(document).ready(function() {
  const $background = $('#gitcoin-background');
  const $navbar = $('.navbar');
  const $header = $('.header');
  const scrollWrapper = $('#landing_page_wrapper');

  let startX = null;
  let startY = null;
  let mouseX = 0;
  let mouseY = 0;
  const followStateHeight = 500;
  let navFollowState = scrollWrapper.scrollTop() > followStateHeight;

  const movementStrength = 25;
  const height = movementStrength / $(window).height();
  const width = movementStrength / $(window).width();
  let throttledHandler;
  const moveBackground = e => {
    mouseX = e.pageX || mouseX;
    mouseY = e.pageY || mouseY;
    if (throttledHandler) {
      return;
    }
    throttledHandler = requestAnimationFrame(() => {
      if (!navFollowState && scrollWrapper.scrollTop() > followStateHeight) {
        $navbar.addClass('following');
        navFollowState = true;
      } else if (navFollowState && scrollWrapper.scrollTop() < followStateHeight) {
        $navbar.removeClass('following');
        navFollowState = false;
      }
      const pageX = mouseX - ($(window).width() / 2);
      const pageY = mouseY - ($(window).height() / 2) + scrollWrapper.scrollTop() * 2;
      const newvalueX = width * (pageX - startX) * -1 - 100;
      let newvalueY = height * (pageY - startY) * -1 - 140;

      if (!startX) {
        startX = newvalueX;
      }

      if (!startY) {
        startY = newvalueY;
      }

      $background.css('transform', `translate(${newvalueX - startX}px, ${newvalueY - startY}px)`);
      throttledHandler = undefined;
    });
  };

  $navbar.mousemove(moveBackground);
  $header.mousemove(moveBackground);
  let robotContainerPos = $('.case-studies-container').position().top;
  let treeContainerPos = $('.tree_container').position().top;
  const $gcRobot = $('#gc-robot');
  const $gcTree = $('#gc-tree');

  window.addEventListener('resize', function(e) {
    robotContainerPos = $('.case-studies-container').position().top;
    treeContainerPos = $('.tree_container').position().top;
  });

  scrollWrapper.scroll((e) => {
    moveBackground(e);
    $gcRobot.css('transform', `translateY(${(-scrollWrapper.scrollTop() + robotContainerPos - 100) / 2}px)`);
    $gcTree.css('transform', `translateY(${(scrollWrapper.scrollTop() - treeContainerPos) / 6}px)`);
  });
  moveBackground({});

  $('#funder-toggle').click(function(e) {
    $('#funder-toggle').addClass('active');
    $('#contributor-toggle').removeClass('active');
  });
  $('#contributor-toggle').click(function(e) {
    $('#funder-toggle').removeClass('active');
    $('#contributor-toggle').addClass('active');
  });
});
