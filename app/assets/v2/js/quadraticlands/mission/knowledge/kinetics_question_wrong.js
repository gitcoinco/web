document.addEventListener('DOMContentLoaded', function() {
  const kinetics = new Kinetics({
    particles: {
      count: 16, sizes: { min: 5, max: 10 }, rotate: { speed: 5 },
      mode: { type: 'rain', boundery: 'endless', speed: '10' }
    }
  });

  kinetics.interactionHook();
});
