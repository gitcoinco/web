window.onload = function () {

  var alphabet = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h',
        'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's',
        't', 'u', 'v', 'w', 'x', 'y', 'z'];
  var pressedKeys = [];
  var categories;         // Array of topics
  var chosenCategory;     // Selected category
  var getHint ;          // Word getHint
  var word ;              // Selected word
  var guess ;             // guess
  var guesses = [ ];      // Stored guesses
  var lives ;             // Lives
  var counter ;           // Count correct guesses
  var space;              // Number of spaces in word '-'

  // Get elements
  var showLives = document.getElementById("mylives");
  var showTimer = this.document.getElementById("time");
  var showcategory = document.getElementById("scategory");
  var getHint = document.getElementById("hint");
  var showClue = document.getElementById("clue");

 // kb utility
  function countInArray(array, what) {
    var count = 0;
    for (var i = 0; i < array.length; i++) {
        if (array[i] === what) {
            count++;
        }
    }
    return count;
  }


  // kb listener function
  function kblisten(event){
    pressedKeys.push(event.key)
    if (countInArray(pressedKeys, event.key) > 1) {
      // pass
    } else {
      var elms = document.querySelectorAll("[id='letter']");
    var selectedLetter = alphabet.indexOf(event.key);
    elms[selectedLetter].setAttribute("class", "active");
    
    var guess = event.key;
    for (var i = 0; i < word.length; i++) {
      if (word[i] === guess) {
        guesses[i].innerHTML = guess;
        counter += 1;
      } 
    }
    var j = (word.indexOf(guess));
    if (j === -1) {
      lives -= 1;
      comments();
      animate();
    } else {
      comments();
    }
    }
  }
  window.addEventListener('keydown', kblisten, true);

  // create alphabet ul
  var buttons = function () {
    myButtons = document.getElementById('buttons');
    letters = document.createElement('ul');

    for (var i = 0; i < alphabet.length; i++) {
      letters.id = 'alphabet';
      list = document.createElement('li');
      list.id = 'letter';
      list.innerHTML = alphabet[i];
      check();
      myButtons.appendChild(letters);
      letters.appendChild(list);
    }
  }
    
  
  // Select category
  // Categories should be in the same order as guessable words
  // On production, you may want to only implement one word, category and hint and get rid of the randomness
  var selectCat = function () {
    if (chosenCategory === categories[0]) {
      categoryName.innerHTML = "The randomly chosen category is <strong>"+document.category+"</strong>.";
    }
  }

  // Create guesses ul
   result = function () {
    wordHolder = document.getElementById('hold');
    correct = document.createElement('ul');

    for (var i = 0; i < word.length; i++) {
      correct.setAttribute('id', 'my-word');
      guess = document.createElement('li');
      guess.setAttribute('class', 'guess');
      if (word[i] === "-") {
        guess.innerHTML = "-";
        space = 1;
      } else {
        guess.innerHTML = "_";
      }

      guesses.push(guess);
      wordHolder.appendChild(correct);
      correct.appendChild(guess);
    }
  }
  
  // Show lives
   comments = function () {
    showLives.innerHTML = "You have <strong>" + lives + "</strong> lives";
    if (lives < 1) {
      showLives.innerHTML = "Game Over";
      _death();
      getHint.style.display = "none"
      showTimer.style.display = "none";
      myButtons = document.getElementById('buttons');
      myButtons.style.display = "none";
      window.removeEventListener('keydown', kblisten, true)
    }
    for (var i = 0; i < guesses.length; i++) {
      if (counter + space === guesses.length) {
        showTimer.style.display = "none";
        window.removeEventListener('keydown', kblisten, true)
        showLives.innerHTML = "<strong>Congrats! You won a Kudo!</strong> – <a href=\"#\">(Redeem)</a>";
      }
    }
  }

      // Animate man
  var animate = function () {
    var drawMe = lives ;
    drawArray[drawMe]();
     toggle_character_class($('#protagonist'), [ 'harm', '' ]);
     toggle_character_class($('#enemy'), [ 'heal', '' ]);

  }

  
   // Hangman
  canvas =  function(){

    myStickman = document.getElementById("stickman");
    context = myStickman.getContext('2d');
    context.beginPath();
    context.strokeStyle = "#fff";
    context.lineWidth = 2;
  };
  
    head = function(){
      myStickman = document.getElementById("stickman");
      context = myStickman.getContext('2d');
      context.beginPath();
      context.arc(60, 25, 10, 0, Math.PI*2, true);
      context.stroke();
    }
    
  draw = function($pathFromx, $pathFromy, $pathTox, $pathToy) {
    
    context.moveTo($pathFromx, $pathFromy);
    context.lineTo($pathTox, $pathToy);
    context.stroke(); 
}

   frame1 = function() {
     draw (0, 150, 150, 150);
   };
   
   frame2 = function() {
     draw (10, 0, 10, 600);
   };
  
   frame3 = function() {
     draw (0, 5, 70, 5);
   };
  
   frame4 = function() {
     draw (60, 5, 60, 15);
   };
  
   torso = function() {
     draw (60, 36, 60, 70);
   };
  
   rightArm = function() {
     draw (60, 46, 100, 50);
   };
  
   leftArm = function() {
     draw (60, 46, 20, 50);
   };
  
   rightLeg = function() {
     draw (60, 70, 100, 100);
   };
  
   leftLeg = function() {
     draw (60, 70, 20, 100);
   };
  
  drawArray = [rightLeg, leftLeg, rightArm, leftArm,  torso,  head, frame4, frame3, frame2, frame1]; 


  // OnClick Function
   check = function () {
    list.onclick = function () {
      var guess = (this.innerHTML);
      this.setAttribute("class", "active");
      this.onclick = null;
      for (var i = 0; i < word.length; i++) {
        if (word[i] === guess) {
          guesses[i].innerHTML = guess;
          counter += 1;
         toggle_character_class($('#protagonist'), [ 'heal', '' ]);
         toggle_character_class($('#enemy'), [ 'harm', '' ]);
        } 
      }
      var j = (word.indexOf(guess));
      if (j === -1) {
        lives -= 1;
        comments();
        animate();
      } else {
        comments();
      }
    }
  }
  _death = function(){
    orb_state('dead');
    $('body').addClass('_death');
    $('#protagonist .ded').removeClass('hidden');
    $('.prize').effect('explode');
    $('.prize').remove();
    $('#protagonist').effect('explode');
    $('#protagonist').addClass('hidden');
  }
  win = function(){
    orb_state('dead');
    $('body').addClass('_death');
    $('#enemy .ded').removeClass('hidden');
    $('#enemy').effect('explode');
    $('#enemy').addClass('hidden');
  }
  timer = function startTimer(duration, display) {
    var timer = duration, minutes, seconds;
    setInterval(function () {
        minutes = parseInt(timer / 60, 10)
        seconds = parseInt(timer % 60, 10);

        minutes = minutes < 10 ? "0" + minutes : minutes;
        seconds = seconds < 10 ? "0" + seconds : seconds;

        display.innerHTML = "and <strong>"+minutes + ":" + seconds+"</strong> left.";

        if (--timer < 0) {
          showTimer.innerHTML = "";
          showLives.innerHTML = "Game Over";
          getHint.style.display = "none"
          showTimer.style.display = "none";
          myButtons = document.getElementById('buttons');
          myButtons.style.display = "none";
          _death()
          window.removeEventListener('keydown', kblisten, true);

        }
    }, 1000);
  } 
    
  // Play
  play = function () {
    // words to guess are selected randomly.
    categories = [
        document.word
    ];

    chosenCategory = categories[Math.floor(Math.random() * categories.length)];
    word = chosenCategory[Math.floor(Math.random() * chosenCategory.length)];
    word = word.replace(/\s/g, "-");
    display = document.querySelector('#time');
    buttons();

    guesses = [ ];
    lives = 10;
    counter = 0;
    space = 0;
    result();
    comments();
    selectCat();
    canvas();
    timer(60, display);
  }

  play();
  
  // Hint

    hint.onclick = function() {
      // Hints should be in the same order as guessable words
      hints = [
        document.hint
    ];
    
    getHint.style.display = "none"
    var categoryIndex = categories.indexOf(chosenCategory);
    var hintIndex = chosenCategory.indexOf(word);
    showClue.innerHTML = "<strong>Hint: </strong>" +  hints [categoryIndex][hintIndex];
  };

   // Reset

  document.getElementById('reset').onclick = function() {
    correct.parentNode.removeChild(correct);
    letters.parentNode.removeChild(letters);
    showClue.innerHTML = "";
    context.clearRect(0, 0, 400, 400);
    play();
  }
}
