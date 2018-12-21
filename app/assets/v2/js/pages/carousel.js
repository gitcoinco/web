const $slides = $('#slides');

let currentSlide = 0;
var load_kudos_card_images = function() {
  for (var i = 0; i < $('.kd-card:visible img').length; i++) {
    // dont load all at once
    var ele = $('.kd-card:visible img')[i];
    var url = $(ele).data('src');

    $(ele).attr('src', url);
  }
};

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

