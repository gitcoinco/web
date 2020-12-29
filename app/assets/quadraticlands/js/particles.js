document.addEventListener("DOMContentLoaded",function(){

  /// CONFIG
  const config = {
    amount : 15,
    size : { min: 12, max: 40 },
    color : { purple: "#6F3FF5", pink: "#F35890", aqua: "#02E2AC" },
    colorcycleTime : { min: 600, max: 6000 },
    rotationTime : { min: 3000, max: 12000 },
    padding: "5px",
    paddingTime : { min: 600, max: 4000 },
    opacityTime : { min: 600, max: 6000 },
    starfieldspeed : { min: 15, max: 100 },
    w : Math.max(document.documentElement.clientWidth || 0, window.innerWidth || 0),
    h : Math.max(document.documentElement.clientHeight || 0, window.innerHeight || 0),
    paths : [
      "M63 20L99 90L29 108L63 20Z", "M85 22L82 102L42 106L85 22Z",
      "M103 96L52 23L28 77L103 96Z", "M103 101L78 26L24 83L103 101Z",
      "M30 30L107 25L93 104H22L30 30Z", "M13 80L70 31L115 75L19 95L13 80Z",
      "M107 109L21 25L27 54L80 107L107 109Z", "M104 82L26 20L23 35L57 109L104 82Z",
      "M31 29L66 16L97 45L88 80L54 112L31 29Z", "M63 14L103 48L92 104H34L16 48L63 14Z",
      "M74 27L109 42L95 101L26 83L20 65L74 27Z", "M37 16L79 36L107 110L30 70L21 36L37 16Z"
    ]   
  }



  /// ARRAY : generate a particles Array
  let particles = new Array
  for (var p = 0; p < config.amount; p++) {
    particles[p] = new Particle(config)
  }



  /// CREATE SECTION#particles ( the place where all particles live )
  const div = document.createElement("section")
  div.setAttribute("id","particles")
  document.body.appendChild(div)



  /// SVG : generate inline svgs from this Array ( one time only per page )
  particles.forEach(p => {
    create(p, config)
  })



  /// DRAW : add behaviours like position, size, rotation to each svg based on generated rng
  const svgs = document.querySelectorAll("#particles svg")
  svgs.forEach((svg, index) => {
    draw(svg, index, particles, config)
  })




  /// INTERACTIVE LINKS
  const particleAttract = document.querySelectorAll(".particleAttract, section a, section .btn")

  particleAttract.forEach(link => {

    /// on mouseover
    link.onmouseover = (event) => {

      if (link.dataset.particlesize) { var particlesize = link.dataset.particlesize } else { var particlesize = 60 }

      var box = link.getBoundingClientRect();
      var area = { width : link.offsetWidth, height : link.offsetHeight }
      let svgs = document.querySelectorAll("#particles svg")

        svgs.forEach( (svg, i) => {

          // just pick some random particles
          if ( Math.random() >= 0.5) {
            svg.style.left = box.left + ( ~~(Math.random() * area.width)) - ( particlesize / 2 ) + "px"
            svg.style.top =  box.top + ( ~~(Math.random() * area.height)) - ( particlesize / 2 ) + "px"
            svg.style.width = particlesize + "px"
            svg.style.height = particlesize + "px"           
          }

        });

    };



    /// on mouseout
    link.onmouseout = (event) => {

      let svgs = document.querySelectorAll("#particles svg")
      svgs.forEach((svg, index) => {
        draw(svg, index, particles, config)
      })

    };



  });



  /// FIND STARFIELD TRIGGERS ON PAGE
  const particleStarfieldTrigger = document.querySelector('.particleStarfieldTrigger');
  var requestID = undefined;

  if(particleStarfieldTrigger) {

    let intervalID;

    // particleStarfieldTrigger in visible screen area
    particleStarfieldTrigger.addEventListener('sal:in', () => {
      var scene = document.getElementById("particles")
      scene.classList.add("starfield-mode")
      intervalID = setInterval( function() { drawStarfield(particles, config) }, 60 ); 
      console.debug("STARFIELD:START")
    });

    // particleStarfieldTrigger not in visible area
    particleStarfieldTrigger.addEventListener('sal:out', () => {
      var scene = document.getElementById("particles")
      scene.classList.remove("starfield-mode")
      let svgs = document.querySelectorAll("#particles svg")
      svgs.forEach((svg, index) => { draw(svg, index, particles, config) })
      clearInterval(intervalID);
      console.debug("STARFIELD:STOP")
    });

  }



});








function create(p, config){

  const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg")
  svg.setAttribute ("width", "128" )
  svg.setAttribute ("height", "128" )
  svg.setAttribute ("viewBox", "0 0 128 128")
  const path = document.createElementNS("http://www.w3.org/2000/svg", "path")
  path.setAttribute("d", p.artwork)
  svg.appendChild(path)
  document.getElementById("particles").appendChild(svg)

}



function draw(svg, index, particles, config){

  svg.style.left = particles[index].x + "px"
  svg.style.top = particles[index].y + "px" 

  svg.style.width = particles[index].size + "px"
  svg.style.height = particles[index].size + "px"

  svg.animate({ fill: [ config.color.purple, config.color.pink, config.color.aqua, config.color.purple ]}, 
    { duration: particles[index].colorcycleTime, delay: 0, iterations: Infinity })

  svg.animate({ transform: ["rotate(0deg)","rotate(360deg)"] },
    { duration: particles[index].rotationTime, delay: 0, iterations: Infinity })

  svg.animate({ padding: ["0px" , config.padding , "0px" ]},
    { duration: particles[index].paddingTime, delay: 0, iterations: Infinity })

  svg.animate({ opacity: [ 0.8, 1, 0.8] },
    { duration: particles[index].opacityTime, delay: 0, iterations: Infinity })

}



function drawStarfield(particles, config){

  const width = config.w

  let svgs = document.querySelectorAll("#particles svg")

  svgs.forEach((svg, index) => {

    svg.style.left = parseInt(svg.style.left,10) - particles[index].starfieldspeed + "px"

      if (parseInt(svg.style.left,10) < -300  )
        { 
          svg.style.left = width + 300 + "px" // out of screen left > set again on right side
          svg.top = ~~(Math.random() * (config.h + this.size) - this.size )
        }

      // prevent jump svgs fast from left to right cause of css transition 300ms on position
      // the particle back on left side of screen
      if (parseInt(svg.style.left,10) <= 0 ) { svg.style.display = 'none'; }
      if (parseInt(svg.style.left,10) >= width) { svg.style.display = 'block'; }


  })


}






class Particle{

  constructor(config){
    this.artwork = config.paths[~~(Math.random() * config.paths.length)]
    this.size = ~~(Math.random() * (config.size.max - config.size.min) + config.size.min)
    this.x = ~~(Math.random() * (config.w + this.size) - this.size )
    this.y = ~~(Math.random() * (config.h + this.size) - this.size )
    this.colorcycleTime = ~~(Math.random() * (config.colorcycleTime.max - config.colorcycleTime.min) + config.colorcycleTime.min)
    this.rotationTime = ~~(Math.random() * (config.rotationTime.max - config.rotationTime.min) + config.rotationTime.min)
    this.paddingTime = ~~(Math.random() * (config.paddingTime.max - config.paddingTime.min) + config.paddingTime.min)
    this.opacityTime = ~~(Math.random() * (config.opacityTime.max - config.opacityTime.min) + config.opacityTime.min)
    this.starfieldspeed = ~~(Math.random() * (config.starfieldspeed.max - config.starfieldspeed.min) + config.starfieldspeed.min)
  }

}











