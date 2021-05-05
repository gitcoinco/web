document.addEventListener('DOMContentLoaded', function() {
  window.kinetics = new Kinetics({
    particles: {
      count: 16, sizes: { min: 100, max: 200 }, rotate: { speed: 0.2 },
      mode: { type: 'linear', boundery: 'endless', speed: '1' }
    }
  });
  window.kinetics.interactionHook();
});
