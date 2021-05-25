document.addEventListener('DOMContentLoaded', function() {
  window.kinetics = new Kinetics({
    particles: {
      count: 8, sizes: { min: 100, max: 200 }, rotate: { speed: 0.2 }, toColor: '#6F3FF5',
      mode: { type: 'linear', boundery: 'endless', speed: '1' }
    }
  });
  window.kinetics.interactionHook();
});
