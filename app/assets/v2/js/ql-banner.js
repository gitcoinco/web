
// check if the banner has been closed
if (!localStorage.getItem('ql-banner')) {
  // grab the elements
  const banner = document.getElementById('ql-banner');
  // grab the elements
  const bannerCoin = document.getElementById('ql-banner-coin');
  const bannerClose = document.getElementById('ql-banner-close');

  // change opacity of the inner content on load
  const bannerInnerRow = document.querySelector('#ql-banner-inner .row');

  // show the banner
  banner.style.display = 'flex';

  // set up the kinetics (using custom implementation to contain the particles in a single el)
  const kinetics = new Kinetics({
    // to fill the full-size banner we need to take measurements from here
    container: document.querySelector('#ql-banner'),
    // but for z-indexing we need to append the canvas here
    prependTo: document.querySelector('#ql-banner-inner'),
    // we want the canvas to be absolutely positioned
    canvas: {
      handlePosition: false,
      style: {
        position: 'absolute',
        pointerEvents: 'none',
        zIndex: 1
      }
    },
    // ignore scroll methods
    unpausable: true,
    // configure the particles
    particles: {
      count: 32, size: {min: 100, max: 300}, rotate: {speed: 0.1},
      mode: {type: 'wind-from-right', boundery: 'endless', speed: '2' }
    }
  }, document.querySelector('#ql-banner'));

  // hook the particles
  kinetics.interactionHook();

  // spin the coin
  const spinCoin = () => {
    bannerCoin.classList.remove('spin-3d');
    // trigger reflow
    void bannerCoin.offsetWidth;
    bannerCoin.classList.add('spin-3d');
  };

  // close the banner
  const closeBanner = () => {
    // hide on click
    banner.style.display = 'none';
    // keep the banner hidden
    localStorage.setItem('ql-banner', true);
  };

  // wait a tick to display to avoid flashing the wrong position
  setTimeout(() => {
    // fade in on load
    bannerInnerRow.style.opacity = 1;
    bannerInnerRow.style.paddingTop = 0;
    // spin on load
    spinCoin();
  });

  // spin on click
  bannerCoin.addEventListener('click', spinCoin);

  // close on click
  bannerClose.addEventListener('click', closeBanner);
}
