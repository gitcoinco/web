document.addEventListener('DOMContentLoaded', function() {
  const kinetics = new Kinetics({
    particles: {
      count: 8, sizes: { min: 100, max: 200 }, rotate: { speed: 0.2 },
      mode: { type: 'linear', boundery: 'endless', speed: '1' }
    }
  });

  kinetics.interactionHook();
});
