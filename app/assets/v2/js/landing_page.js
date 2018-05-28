
// Header and Nav
$(document).ready(function() {
  const $background = $('#gitcoin-background');
  const $navbar = $('.navbar');
  const $header = $('.header');
  const scrollWrapper = $('#landing_page_wrapper');
  const $gcRobot = $('#gc-robot');
  const $gcTree = $('#gc-tree');

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
      const pageY = mouseY - ($(window).height() / 2) - scrollWrapper.scrollTop() * 2;
      const newvalueX = width * pageX - 10;
      let newvalueY = height * pageY;

      $gcRobot.css('transform', `translateY(${($gcRobot.parent()[0].getBoundingClientRect().top - 100) / 2}px)`);
      $gcTree.css('transform', `translateY(${(-$gcTree.parent()[0].getBoundingClientRect().top) / 6 + 40}px)`);

      $background.css('transform', `translate(${newvalueX}px, ${newvalueY}px)`);
      throttledHandler = undefined;
    });
  };

  $navbar.mousemove(moveBackground);
  $header.mousemove(moveBackground);
  let robotContainerPos = $('.case-studies-container').offset().top;
  let treeContainerPos = $('.tree_container').offset().top;

  // Robot and Tree Parallax
  const moveWithScroll = (e) => {
    moveBackground(e);
  };

  scrollWrapper.scroll(moveWithScroll);
  moveBackground({});

  // How It Works section toggle
  $('#funder-toggle').click(function(e) {
    $('#funder-toggle').addClass('active');
    $('#contributor-toggle').removeClass('active');
  });
  $('#contributor-toggle').click(function(e) {
    $('#funder-toggle').removeClass('active');
    $('#contributor-toggle').addClass('active');
  });

  const prevScroll = localStorage.getItem('scrollTop');
  const lastAccessed = localStorage.getItem('lastAccessed');

  // Preserve scroll position if user was just here
  if (prevScroll && lastAccessed && new Date().getTime() - lastAccessed < 60 * 1000) {
    scrollWrapper.scrollTop(prevScroll);
    moveWithScroll({});
  }
  // before the current page goes away, save the menu position
  $(window).on('beforeunload', function() {
    localStorage.setItem('scrollTop', scrollWrapper.scrollTop());
    localStorage.setItem('lastAccessed', new Date().getTime());
  });
});
