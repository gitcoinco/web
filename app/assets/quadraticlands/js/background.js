document.addEventListener("DOMContentLoaded",function(){

  console.debug("BACKGROUND")

  initBackground()


  setInterval(() => {
    newPos()
  }, 5000);


});



function newPos(){
  let w = Math.max(document.documentElement.clientWidth || 0, window.innerWidth || 0);
  let h = Math.max(document.documentElement.clientHeight || 0, window.innerHeight || 0);
  let minPosX = -200
  let maxPosX = w + 200
  let minPosY = -200
  let maxPosY = h + 200
  let p = document.querySelectorAll("#background svg");

  p.forEach(p => {
    p.style.left = Math.random() * (maxPosX - minPosX) + minPosX;
    p.style.top = Math.random() * (maxPosY - minPosY) + minPosY;   
  });


}




function initBackground() {

  const minSize = 5
  const maxSize = 60
  const minColorCycle = 5000
  const maxColorCycle = 10000
  const minRotation = 100000
  const maxRotation = 300000

  const background = document.querySelector("#background");
  background.classList.remove("hide") 

  const w = Math.max(document.documentElement.clientWidth || 0, window.innerWidth || 0);
  const h = Math.max(document.documentElement.clientHeight || 0, window.innerHeight || 0);
  const p = document.querySelectorAll("#background svg");


  const minPosX = -200
  const maxPosX = w + 200
  const minPosY = -200
  const maxPosY = h + 200



  p.forEach(p => {

    // position
    p.style.left = Math.random() * (maxPosX - minPosX) + minPosX;
    p.style.top = Math.random() * (maxPosY - minPosY) + minPosY;

    // size
    size = Math.floor(Math.random() * maxSize ) + minSize
    p.style.width = size + "vw";
    p.style.height = size + "vh";

    // colorcycle
    durationFill = Math.floor(Math.random() * (maxColorCycle-minColorCycle))  + minColorCycle;
    p.animate({
      fill: [ "#6F3FF5", "#F35890", "#02E2AC", "#6F3FF5" ]
    }
    , { 
      duration: durationFill,
      delay: 0,
      iterations: Infinity
    });


    // rotate
    if ( Math.random() > 0.5 ) { transform = ["rotate(0deg)","rotate(360deg)"] }
    else { transform = ["rotate(360deg)","rotate(0deg)"] }

    durationRotate = Math.floor(Math.random() * (maxRotation-minRotation)) + minRotation;
    p.animate({
      transform: transform
    }
    , { 
      duration: durationRotate,
      delay: 0,
      iterations: Infinity
    });




  });


}




