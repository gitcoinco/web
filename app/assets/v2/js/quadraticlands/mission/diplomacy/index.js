document.addEventListener('DOMContentLoaded', function() {

  console.debug("mission diplomacy loaded");

  // random floor polygones coloring / lights of town
  polygones = document.querySelectorAll('svg #hero polygon, svg #hero path');

  polygones.forEach(p => {
    p.setAttribute('data-kinetics-attraction', '');
    p.setAttribute('data-kinetics-attraction-chance', getRandomFloat(0.3, 1));
    p.setAttribute('data-kinetics-attraction-force', getRandomFloat(.7, 1.3));
    p.setAttribute('data-kinetics-attraction-grow', getRandomInt(1, 4));
    p.setAttribute('data-tone-click-random', '');
    p.style.cursor = 'pointer';
  });

  initToneJs();

  new Kinetics().interactionHook();

  last = 0;
  console.debug('ANIMATE DIPLOMACY');
  animate_diplomacy();
});


function animate_diplomacy(now) {

  if (!last || now - last >= 60) {

    // pick a random poly from hero-about.svg
    // to randomly color up with a little animation
    polygone = polygones[Math.floor(Math.random() * polygones.length)];
    polygone.animate({ fill: [ '#9760FF', '#FA72AF', '#7AFFF7', '#9760FF' ] },
      {
        duration: 500, delay: 0, iterations: 1
      });

    last = now;
  }

  requestAnimationFrame(animate_diplomacy);
}
