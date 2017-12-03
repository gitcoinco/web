function findNextButton(currentButtonValue, radioButtons) {
  var maxIndex = radioButtons.length - 1
  var newButtonValue = (currentButtonValue + 1) % (maxIndex)
  return radioButtons[newButtonValue]
}

function findPreviousButton(currentButtonValue, radioButtons) {
  var maxIndex = radioButtons.length - 1
  var newButtonValue
  if (currentButtonValue == 0) {
    newButtonValue = maxIndex
  } else {
    newButtonValue = (currentButtonValue - 1)
  }
  return radioButtons[newButtonValue]
}

function nextSlide() {
  var radioButtons = $("input[name='carousel']")
  var currentButtonValue = $("input[name='carousel']:checked").val()

  var nextButton = findNextButton(currentButtonValue, radioButtons)

  nextButton.click();

  resetTimer();
}

function previousSlide() {
  var radioButtons = $("input[name='carousel']")
  var currentButtonValue = $("input[name='carousel']:checked").val()

  var prevButton = findPreviousButton(currentButtonValue, radioButtons)

  prevButton.click()

  resetTimer();
}

var interval;
var startTimer = function(){
 interval = setInterval(function(){
  nextSlide()
  },5000);
};

function resetTimer() {
  clearInterval(interval);
  startTimer();
}

$(document).keyup(function(e) {
  radioButtons = $("input[name='carousel']")
  currentButtonValue = $("input[name='carousel']:checked").val()
  if (e.key === "ArrowLeft") {
    previousSlide(currentButtonValue, radioButtons)
  } else if (e.key == "ArrowRight") {
    nextSlide(currentButtonValue, radioButtons)
  }
});

$(document).ready(function() {
  startTimer();
})