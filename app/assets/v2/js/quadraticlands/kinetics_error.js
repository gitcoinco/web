document.addEventListener('DOMContentLoaded', function() {
  const kinetics = new Kinetics({
    particles: { count: 4, size: {min: 400, max: 800}, rotate: {speed: 0.1},
      mode: {type: 'linear', boundery: 'endless', speed: '1' }}
  });

  kinetics.interactionHook();
});
