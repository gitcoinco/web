const $slides = $('#slides');

let currentSlide = 0;

this.load_kudos_card_images = function() {
  let images = [...document.querySelectorAll('.kd-card img')];

  const interactSettings = {
    root: document.querySelector('.loader-container'),
    rootMargin: '0px 200px 200px 200px',
    threshold: 0.01
  };

  function onIntersection(imageEntites) {
    imageEntites.forEach(image => {
      if (image.isIntersecting) {
        observer.unobserve(image.target);
        image.target.src = image.target.dataset.src;
        image.target.onload = () => image.target.classList.add('loaded');
      }
    });
  }

  let observer = new IntersectionObserver(onIntersection, interactSettings);

  images.forEach(image => observer.observe(image));
};

this.nextSlide = function() {
  currentSlide = (currentSlide + 1) % $slides.children().length;
  $slides.css('transform', `translateX(${-currentSlide * 100}vw)`);
  resetTimer();
}

this.prevSlide = function() {
  if (currentSlide == 0) {
    currentSlide = slides.length - 1;
  } else {
    currentSlide = (currentSlide - 1) % slides.length;
  }
  $slides.css('transform', `translateX(${-currentSlide * 100}vw)`);
  resetTimer();
}

const resetTimer = function() {
  clearInterval(interval);
  startTimer();
}

