// decounce actions to avoid measuring too often/losing focus
let debounceMeasure = false;
let debounceClose = false;

// allow for the dimensions to be set-up before measuring (moveX sets an offset to move gc-menu-[background/content] on the x axis)
const dimensions = {
  // set offset as % (0.*) or px value
  products: {
    moveX: -60
  },
  company: {
    moveX: -80
  }
};

// read the transition duration from navbar.scss
const transitionDuration = parseFloat(getComputedStyle(document.documentElement).getPropertyValue('--gc-menu-transition-duration'));

// reference constant els used in the menu
const navbarEl = document.querySelector('.gc-navbar-nav');
const navbarContainerEl = document.querySelector('.navbar');
const menuContainerEl = document.querySelector('.gc-menu-container');
const navItemEls = document.querySelectorAll('.gc-nav-item');
const navLinkEls = document.querySelectorAll('.gc-nav-link');
const menuEls = document.querySelectorAll('.gc-menu-wrap');
const spacerEls = document.querySelectorAll('.gc-mobile-spacer');
const contentEl = document.querySelector('.gc-menu-content');
const caretEl = document.querySelector('.gc-menu-caret');
const backgroundEl = document.querySelector('.gc-menu-background');
const mobileToggleEl = document.querySelector('.navbar-toggler-icon');
const submenuToggleEls = document.querySelectorAll('.gc-menu-submenu-toggle');
const submenuEls = document.querySelectorAll('.gc-menu-submenu');

// index a collection by data-* attr taken from "from" nodeList elements finding classname ending with attr
const indexElsByName = (from, className, dataAttr) => {

  return [...from].reduce((carr, el) => {
    const attr = el.dataset[dataAttr];
    const dest = document.querySelector(`.${className}-${attr}`);

    // record the dest by attr value
    carr[attr] = dest;

    return carr;
  }, {});
};

// collect the els by name
const menuElsByName = indexElsByName(navLinkEls, 'gc-menu-wrap', 'menu');
const spacerElsByName = indexElsByName(navLinkEls, 'gc-mobile-spacer', 'menu');
const submenuElsByName = indexElsByName(submenuToggleEls, 'gc-menu-submenu', 'submenu');


// get a single dimension from a navLink el
const getDimension = (navLink, menuEL, isDesktop, menu) => {
  // display the container before measuring
  menuContainerEl.classList.add('show');

  // remove transform (rotate()) during measure so that the height/width isn't skewed
  menuContainerEl.style.transform = 'unset';
  menuContainerEl.style.transition = 'unset';

  // record as dimension obj
  const dimension = {};

  // pull info from doc to find the bounding to position the menu content/background/caret
  const navbarRect = navbarEl.getBoundingClientRect();
  const navLinkRect = navLink.getBoundingClientRect();
  const contentRect = menuEL.getBoundingClientRect();
  const containerRect = navbarContainerEl.getBoundingClientRect();

  // hide it again
  menuContainerEl.classList.remove('show');

  // remove unset from transform
  menuContainerEl.style.removeProperty('transform');
  menuContainerEl.style.removeProperty('transition');

  // allow the menuX pos to be offset by % or px value
  const offsetX = (isDesktop && dimensions[menu] && dimensions[menu].moveX ? (
      Math.abs(dimensions[menu].moveX) > 1 ? dimensions[menu].moveX : window.innerWidth * dimensions[menu].moveX
    ) : 0);

  // use measurements to dictate dimentsions and x/y positions
  dimension.arrowX = navLinkRect.left + (navLinkRect.width / 2) - navbarRect.left;
  dimension.menuX = dimension.arrowX - 66 + offsetX;
  dimension.menuY = navLinkRect.bottom - containerRect.y;
  dimension.width = contentRect.width;
  dimension.height = contentRect.height;

  // return the dimensions
  return dimension;
};


// set the dimensions for each navLinks menu
const setDimensions = () => {
  navLinkEls.forEach((navLink) => {
    // get the menu name from the navLink
    const menu = navLink.dataset.menu;
    // get the named menuEl
    const menuEL = menuElsByName[menu];

    // combine/fill the dimensions with new measurments
    dimensions[menu] = {...(dimensions[menu] ? dimensions[menu] : {}), ...getDimension(navLink, menuEL, true, menu)};
  });
};


// remove isVisible transitions to reduce jank
const resetVisibility = () => {
  // removing isVisible will reset transition to just opacity
  backgroundEl.classList.remove('isVisible');
  contentEl.classList.remove('isVisible');
  caretEl.classList.remove('isVisible');
  // close the dropdown to animate out
  menuContainerEl.classList.remove('open');
  // remove .show after the transitions finish
  setTimeout(() => {
    menuContainerEl.classList.remove('show');
  }, transitionDuration)
};


// clean up recorded dimensions and display state of the menu
const cleanUp = () => {
  // remove transform transitions
  resetVisibility();

  // remove prev .active state
  menuEls.forEach(el => {
    el.style.cssText = 'transition:unset;';
    el.classList.remove('show');
    el.classList.remove('active');
    el.style.cssText = '';
  });
  spacerEls.forEach(el => el.classList.remove('active'));
  navItemEls.forEach(el => el.classList.remove('active'));

  // remove current positions so that nothings offpage
  menuContainerEl.style.cssText = 'transition:unset;';
  backgroundEl.style.cssText = 'transition:unset;';
  contentEl.style.cssText = 'transition:unset;';
  caretEl.style.cssText = 'transition:unset;';
};


// toggle display of menu dropdown (triggered on hover - content is moved and background is scaled)
const showMenu = (navLink) => {
  // get menu name from navLink
  const menu = navLink.dataset.menu;

  // focus the element (to show :focus state on hover)
  navLink.focus();

  // mark menu open
  menuContainerEl.classList.add('show');

  // wait for .show paint (toggles display)
  window.requestAnimationFrame(() => {

    // add open to set opacity and to transition the rotateX
    menuContainerEl.classList.add('open');
    // remove prev active state
    menuEls.forEach(el => el.classList.remove('active'));
    // mark this menu as active
    menuElsByName[menu].classList.add('active');

    // clear disable transition
    menuContainerEl.style.cssText = '';
    backgroundEl.style.cssText = '';
    contentEl.style.cssText = '';
    caretEl.style.cssText = '';

    // hide bs dropdowns
    $('.nav-link.dropdown-toggle').dropdown('hide');

    // resize and position background (use scale to avoid janky transitions)
    backgroundEl.style.transform = `
      translateX(${ dimensions[menu].menuX }px)
      scaleX(${ dimensions[menu].width / (window.innerWidth * 0.60) })
      scaleY(${ dimensions[menu].height / (window.innerHeight * 0.50) })`;

    // resize and position content (we need to use width/height here but jank is hidden by the background)
    contentEl.style.width = dimensions[menu].width + 'px';
    contentEl.style.height = dimensions[menu].height + 'px';
    contentEl.style.transform = `
      translateX(${ dimensions[menu].menuX }px)`;

    // position caret
    caretEl.style.transform = `
      translateX(${ dimensions[menu].arrowX }px)
      rotate(45deg)`;

    // add isVisible to enable transform animations between menus
    setTimeout(() => {
      contentEl.classList.add('isVisible');
      backgroundEl.classList.add('isVisible');
      caretEl.classList.add('isVisible');
    }, transitionDuration);
  });
};


// toggle display of the menu for mobile
const showMenuMobile = (navLink) => {
  // get menu name from navLink
  const menu = navLink.dataset.menu;
  // get menuEl + menuSpacer so we can move menuEl into menuSpacer space
  const menuEl = menuElsByName[menu];
  const menuSpacer = spacerElsByName[menu];
  // check if its already been opened (is .active)
  const isActive = menuSpacer.classList.contains('active');

  // remove prev .active state
  cleanUp();

  // hide bs dropdowns
  $('.nav-link.dropdown-toggle').dropdown('hide');

  // only open if not already open
  if (!isActive) {
    // display the el
    menuEl.classList.add('show');
    // wait for .show to paint
    window.requestAnimationFrame(() => {
      // mark this menu as active
      menuEl.classList.add('active');
      menuSpacer.classList.add('active');
      navLink.parentElement.classList.add('active');

      // get the dimensions for just this menu (doing this each call so that we can be sure we have the right menuY value after open animation)
      const dimension = getDimension(navLink, menuEl);

      // set spacers height
      menuSpacer.style.height = `${ dimension.height }px`;
      // cleanUp before adding new css
      menuEl.style.cssText = '';
      // resize and position content
      menuEl.style.top = `${ dimension.menuY + navbarContainerEl.scrollTop }px`;
      menuEl.style.height = `${ dimension.height }px`;
    });
  }
};


// set initial positions for each nav item
setDimensions();


// cleanUp on resize
window.addEventListener('resize', () => {
  // debounce the measure
  clearTimeout(debounceMeasure);
  // reinit the cleanup
  debounceMeasure = setTimeout(() => {
    // cleanUp
    cleanUp();
    // only alter dimensions on resive for desktop version
    if (window.innerWidth > 768) {
      // set the new positions
      setDimensions();
    }
  }, 30);
});


// set mouseenter events on each navLink
navLinkEls.forEach((navLink) => {
  navLink.addEventListener('mouseenter', () => {
    // show the selection
    if (window.innerWidth > 768)
      showMenu(navLink);
  });
  navLink.addEventListener('click', (event) => {
    // prevent href from scrolling to top
    event.preventDefault();
    // only do for mobile
    if (window.innerWidth <= 767)
      showMenuMobile(navLink);
  });
});


// cleanup and attach event to close gc-menu on bs-dropdown open
mobileToggleEl.addEventListener('click', () => {
  // remove any open/active state
  cleanUp();
  // bind click event to hide items when bootstrap menu is opened (bind on toggle so that we're definately ready)
  $('.nav-link.dropdown-toggle[data-toggle="dropdown"]').each((_, el) => {
    $(el).off('click.gc-menu').on('click.gc-menu', () => window.innerWidth <= 767 && cleanUp());
  });
});


// set mouseleave event on whole navbar el
navbarEl.addEventListener('mouseleave', () => {
  if (window.innerWidth > 768) {
    debounceClose = setTimeout(() => {
      // remove isVisible transitions to reduce jank
      resetVisibility();
    }, 1000);
  }
});


// if mouse re-enters the navbar clear the timeout
navbarEl.addEventListener('mouseenter', () => {
  if (window.innerWidth > 768) {
    // quit the close routine
    clearTimeout(debounceClose);
  }
});

// show submenu content on hover of gc-menu-submenu-toggle
submenuToggleEls.forEach((submenuToggle) => {
  submenuToggle.addEventListener('mouseenter', () => {
    // show the selection
    if (window.innerWidth > 768) {
      // fix/remove hover state on toggle
      submenuToggleEls.forEach(el => el.classList.remove('gc-menu-toggle-focus'));
      submenuToggle.classList.add('gc-menu-toggle-focus');
      // show/hide submenu
      submenuEls.forEach(el => el.classList.remove('active'));
      submenuElsByName[submenuToggle.dataset.submenu].classList.add('active');
    }
  });
});
