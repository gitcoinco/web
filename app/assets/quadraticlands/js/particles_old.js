document.addEventListener("DOMContentLoaded",function(){

  console.debug("PARTICLES")

  // init particle system
  particleInit()

  // check if this is a touch device
  // to prevent particleAttract() on mobile
  mobile = false
  window.addEventListener('touchstart', function() { 
    mobile = true
  });


});




// particleInit
//
// distribute the existing svg particles
// on random position, scale, animation properties, on the site 

function particleInit() { 


  const vw = Math.max(document.documentElement.clientWidth || 0, window.innerWidth || 0);
  const vh = Math.max(document.documentElement.clientHeight || 0, window.innerHeight || 0);
  const p = document.querySelectorAll("#particles svg");
 
  p.forEach(p => {

      // random positioning within screen
      p.style.left = (Math.floor(Math.random() * vw)) + "px";
      p.style.top = (Math.floor(Math.random() * vh)) + "px";

      // random scale
      size = Math.floor(Math.random() * (30 - 10) + 10);
      p.style.width = size + "px";
      p.style.height = size + "px";

      // apply color animation with random timing
      durationFill = Math.floor(Math.random() * (6000 - 600) + 600);
      p.animate({
        fill: [ "#6F3FF5", "#F35890", "#02E2AC", "#6F3FF5" ]
      }
      , { 
        duration: durationFill,
        delay: 0,
        iterations: Infinity
      });

      // apply opacity animation with random timing
      durationOpacity = Math.floor(Math.random() * (6000 - 600) + 600);
      p.animate({
        opacity: [ 0.8, 1, 0.8]
      }
      , { 
        duration: durationOpacity,
        delay: 0,
        iterations: Infinity
      });

      // apply rotation animation with random timing
      durationRotate = Math.floor(Math.random() * (12000 - 3000) + 3000);
      p.animate({
        transform: ["rotate(0deg)","rotate(360deg)"]
      }
      , { 
        duration: durationRotate,
        delay: 0,
        iterations: Infinity
      });

      // apply rotation animation with random timing
      durationx = Math.floor(Math.random() * (4000 - 600) + 600);
      p.animate({
        padding: ["0px","6px","0px"]
      }
      , { 
        duration: durationx,
        delay: 0,
        iterations: Infinity
      });


      /*
      // apply floating animation with random timing
      durationFloating = Math.floor(Math.random() * (10000 - 3000) + 3000);
      p.animate({
        transform: ["translateY(0px)", "translateY(10px)", "translateY(0px)"]
      }
      , { 
        duration: durationFloating,
        delay: 0,
        iterations: Infinity
      });
      */

  });

}




// attractParticles
//
// attract existing Particles
// to mouse position and make it a bit bigger
// (NOT FOR MOBILE)


function particleAttract() {

  if (!mobile) {

    const p = document.querySelectorAll("#particles svg");
    p.forEach(p => {

      p.style.left = (event.clientX - 32) + "px";
      p.style.top = (event.clientY - 32) + "px";

      // random scale
      size = Math.floor(Math.random() * (64 - 8) + 8);
      p.style.width = size + "px";
      p.style.height = size + "px";

    });

  }

}




// particleStarfield
//
// use all the existing particles
// to generate a starfield from right to left
// once .. have to call in a loop to move the stars

function particleStarfield() {

    const vw = Math.max(document.documentElement.clientWidth || 0, window.innerWidth || 0);
    const p = document.querySelectorAll("#particles svg");
    
    speed = 25;

    p.forEach(p => {

      speed = speed + 25;

      var left = parseInt(p.style.left,10) - speed; 
      p.style.left = left + "px";
      
      // out of screen (left)
      if (parseInt(p.style.left,10) <= -100)
        {
            p.style.left = (vw+100)  + "px";
        }

    });

}






// particleAttractTrigger
//
// by class .particleAttract, section a, section .btn
// preventable attraction to a link by class "noparticles"

const particleAttractTrigger = document.querySelectorAll(".particleAttract, section a, section .btn");

particleAttractTrigger.forEach(p => {

  if ( !p.classList.contains("noparticles") )
  {

    p.addEventListener("mouseover", () => {
      particleAttract();
    });

    p.addEventListener("mouseout", () => {
      particleInit();
    });  

  }


});





// particleStarfieldTrigger
//
// observe the page for .particleStarfieldTrigger ( for unicorn )
// and if this is in viewport - then fire up 
// particleStarfield function
// if its not in viewport kill the particleStarfield function



const particleStarfieldTrigger = document.querySelector('.particleStarfieldTrigger');

if(particleStarfieldTrigger)
  {

  let intervalID;
  
  particleStarfieldTrigger.addEventListener('sal:in', ({ detail }) => {
    intervalID = setInterval(particleStarfield, 300);
  });

  particleStarfieldTrigger.addEventListener('sal:out', ({ detail }) => {
    clearInterval(intervalID);
    particleInit();
  });

  }








