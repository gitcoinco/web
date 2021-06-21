document.addEventListener('DOMContentLoaded', function() {
  const kinetics = new Kinetics({
    particles: {
      count: 8, sizes: { min: 10, max: 20 }, rotate: { speed: 0.4 },
      mode: { type: 'rain', boundery: 'endless', speed: '10' }
    }
  });

  kinetics.interactionHook();
});
