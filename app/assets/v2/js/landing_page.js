scrollContainer = $('#landing_page_wrapper');

// Header and Nav
$(document).ready(function() {
  $('#gc-tree #tree-svg .lines').addClass('pause-animation');
  $('#gc-tree #tree-svg .cls-4').addClass('pause-animation');

  const $navbar = $('.navbar');
  const $gcRobot = $('#gc-robot');

  const followStateHeight = 500;
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
    $gcRobot.css('transform', `translateY(${$gcRobot.parent()[0].getBoundingClientRect().top - 100}px)`);
    $('#gc-tree #tree-svg .lines').removeClass('pause-animation');
    $('#gc-tree #tree-svg .cls-4').removeClass('pause-animation');

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
  $funderToggle.click(switchToFunder);
  $contributorToggle.click(switchToContributor);
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

  $('#gc-tree').click(function() {
    $('#gc-tree .cls-4').each(function() {
      if (Math.random() < 0.2) {
        var new_colors = [ '#25e899', '#ffce08', '#eff4ee', '#f9006c', '#8e2abe', '#3e00ff', '#15003e' ];
        var new_color = new_colors[Math.floor(Math.random() * new_colors.length)];

        $(this).css('fill', new_color);
        var sizes = [ 7, 8, 9, 10, 11, 12 ];
        var size = sizes[Math.floor(Math.random() * sizes.length)];

        $(this).css('r', size);
        $(this).css('animation', 'none');
        // var ele = $(this);
        // setTimeout(function(){
        //  ele.css('animation', 'resize 0.3s ease-in 0s forwards');
        // },1000);
      }
    });
  });

});
