const slides = document.querySelectorAll('#slides .slide');
let currentSlide = 0;
slides[0].className = 'slide showing';

let slideInterval = setInterval(nextSlide, 6000);

function nextSlide() {
  slides[currentSlide].className = 'slide';
  currentSlide = (currentSlide+1) % slides.length;
  slides[currentSlide].className = 'slide showing';
}

function prevSlide() {
  slides[currentSlide].className = 'slide';
  if(currentSlide == 0)
    currentSlide = slides.length - 1;
  else
  currentSlide = (currentSlide - 1) % slides.length;
  slides[currentSlide].className = 'slide showing';
}
