const $slides = $('#slides');

let currentSlide = 0;

function nextSlide() {
  currentSlide = (currentSlide + 1) % $slides.children().length;
  $slides.css('transform', `translateX(${-currentSlide * 100}vw)`);
  resetTimer();
}

function prevSlide() {
  if (currentSlide == 0) {
    currentSlide = slides.length - 1;
  } else {
    currentSlide = (currentSlide - 1) % slides.length;
  }
  $slides.css('transform', `translateX(${-currentSlide * 100}vw)`);
  resetTimer();
}

function resetTimer() {
  clearInterval(interval);
  startTimer();
}

