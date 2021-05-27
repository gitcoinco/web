document.addEventListener('DOMContentLoaded', function() {
  const kinetics = new Kinetics({
    particles: {
      count: 16, sizes: { min: 5, max: 40 }, rotate: { speed: 2 },
      mode: { type: 'party', boundery: 'pong', speed: '8' }
    }
  });

  kinetics.interactionHook();
});
