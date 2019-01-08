scrollContainer = $('#landing_page_wrapper');

// Header and Nav
$(document).ready(function() {
  $('#gc-tree #tree-svg .lines').addClass('pause-animation');
  $('#gc-tree #tree-svg .cls-4').addClass('pause-animation');

  const $navbar = $('.navbar');
  const $gcRobot = $('#gc-robot');

  const followStateHeight = 500;
  const treeAnimationPosition = 1500;
  let navFollowState = scrollContainer.scrollTop() > followStateHeight;

  scrollContainer.scroll(RAFThrottle((e) => {
    moveBackground(e);
    // Robot and Tree Parallax
    if (!navFollowState && scrollContainer.scrollTop() > followStateHeight) {
      $navbar.addClass('following');
      navFollowState = true;
    } else if (navFollowState && scrollContainer.scrollTop() < followStateHeight) {
      $navbar.removeClass('following');
      navFollowState = false;
    }

    if (scrollContainer.scrollTop() > treeAnimationPosition) {
      $('#gc-tree #tree-svg .lines').removeClass('pause-animation');
      $('#gc-tree #tree-svg .cls-4').removeClass('pause-animation');
    }

    $gcRobot.css('transform', `translateY(${$gcRobot.parent()[0].getBoundingClientRect().top - 100}px)`);
  }));
  moveBackground({});

  // How It Works section toggle
  const $toggleIndicator = $('#howworks-toggle-indicator');
  const $funderToggle = $('#funder-toggle');
  const $contributorToggle = $('#contributor-toggle');
  const $sections = $('.howworks-sections');

  function switchToFunder(e) {
    $funderToggle.addClass('active');
    $contributorToggle.removeClass('active');
    $toggleIndicator.css('transform', 'scaleX(1)');
    $toggleIndicator.css('left', '0');
    $sections.removeClass('contributor-section');
  }
  function switchToContributor(e) {
    $funderToggle.removeClass('active');
    $contributorToggle.addClass('active');
    $toggleIndicator.css('transform', `scaleX(${$contributorToggle.innerWidth() / $funderToggle.innerWidth()})`);
    $toggleIndicator.css('left', `${$funderToggle.innerWidth() + 20}px`);
    $sections.addClass('contributor-section');
  }
  $funderToggle.on('click', function(e) {
    switchToFunder(e);
  });
  $contributorToggle.on('click', function(e) {
    switchToContributor(e);
  });
  switchToFunder();

  const prevScroll = localStorage.getItem('scrollTop');
  const lastAccessed = localStorage.getItem('lastAccessed');

  // Preserve scroll position if user was just here
  if (prevScroll && lastAccessed && new Date().getTime() - lastAccessed < 60 * 1000) {
    scrollContainer.scrollTop(prevScroll);
  }
  // before the current page goes away, save the menu position
  $(window).on('beforeunload', function() {
    localStorage.setItem('scrollTop', scrollContainer.scrollTop());
    localStorage.setItem('lastAccessed', new Date().getTime());
  });
});
