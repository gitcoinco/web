document.addEventListener('DOMContentLoaded', function() {

  // particles
  new Kinetics().interactionHook();

  // floor polygones in town.svg
  polygones = document.querySelectorAll('#town #floor polygon');

  // .light classes in town.svg
  lights = document.querySelectorAll('#town .light');

  last = 0;
  animate_town();
});


function animate_town(now) {

  if (!last || now - last >= 100) {

    polygone = polygones[Math.floor(Math.random() * polygones.length)];
    polygone.animate({ fill: [ '#9760FF', '#FA72AF', '#7AFFF7', '#9760FF' ] }, { duration: 400, delay: 0, iterations: 1 });

    light = lights[Math.floor(Math.random() * lights.length)];
    light.animate({ fill: [ '#9760FF', '#FA72AF', '#7AFFF7', '#9760FF' ] },
      {
        duration: Math.random() * (5000 - 500) + 500, delay: 0, iterations: 1
      });

    last = now;
  }

  requestAnimationFrame(animate_town);
}
