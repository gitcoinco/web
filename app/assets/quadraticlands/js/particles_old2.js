document.addEventListener("DOMContentLoaded",function(){

  /// DEFAULT CONFIG
  const particlesConfig = {
    amount : 11,
    size : { min: 11, max: 36 },
    color : { purple: "#6F3FF5", pink: "#F35890", aqua: "#02E2AC" },
    colorcycleTime : { min: 600, max: 6000 },
    rotationTime : { min: 3000, max: 12000 },
    padding: "5px",
    paddingTime : { min: 600, max: 4000 },
    opacityTime : { min: 600, max: 6000 },
    scene : { width : document.documentElement.clientWidth, height: document.documentElement.clientHeight },
    force : "",
    defaultforce : "",
    windRight : { min: 40, max: 200 },
    windLeft : { min: 40, max: 200 },
    randomFloating : { min: -50, max: 50 },
    paths : [
      "M63 20L99 90L29 108L63 20Z", "M85 22L82 102L42 106L85 22Z",
      "M103 96L52 23L28 77L103 96Z", "M103 101L78 26L24 83L103 101Z",
      "M30 30L107 25L93 104H22L30 30Z", "M13 80L70 31L115 75L19 95L13 80Z",
      "M107 109L21 25L27 54L80 107L107 109Z", "M104 82L26 20L23 35L57 109L104 82Z",
      "M31 29L66 16L97 45L88 80L54 112L31 29Z", "M63 14L103 48L92 104H34L16 48L63 14Z",
      "M74 27L109 42L95 101L26 83L20 65L74 27Z", "M37 16L79 36L107 110L30 70L21 36L37 16Z"
    ]
  }


  // check if external override for defaultforce exists
  if (typeof window.particlesConfig !== 'undefined') {
    if (window.particlesConfig.defaultforce) { 
      particlesConfig.defaultforce = window.particlesConfig.defaultforce
      particlesConfig.force = window.particlesConfig.defaultforce
    }
  }

  





  /// ON RESIZE SET NEW SCENE DIMENSIONS
  window.addEventListener('resize', (event) => {
    console.debug("RESIZE")
    console.log(event)
    particlesConfig.scene.width = document.documentElement.clientWidth
    particlesConfig.scene.height = document.documentElement.clientHeight
    console.log(particlesConfig)
  } );



  /// ARRAY : generate a Particle System (Array)
  let particles = new Array
  for (var p = 0; p < particlesConfig.amount; p++) {
    particles[p] = new Particle(particlesConfig)
  }



  /// CREATE SECTION#particles ( the place where all particles live )
  const div = document.createElement("section")
  div.setAttribute("id","particles")
  document.body.appendChild(div)



  /// SVG : generate inline svgs from this Array ( one time only per page )
  particles.forEach(p => {
    create(p, particlesConfig)
  })



  /// DRAW : add behaviours like position, size, rotation to each svg based on generated rng
  const svgs = document.querySelectorAll("#particles svg")
  svgs.forEach((svg, index) => {
    draw(svg, index, particles, particlesConfig)
  })


  // FORCE - DRAW NEW PARTICLE POSITIONS WHEN FORCE EXISTS EACH 240ms ( as its 240ms in css transition as well )
  intervalID = setInterval( function() {
    if (particlesConfig.force) { force(particles, particlesConfig) }
    }, 240 
  );





  /// INTERACTIVE LINKS
  /// mouseover : find links internal dimensions and attrackt + spread SOME rnd particles within links X,Y range
  /// mouseout : distribute back to where it was before
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

      if (!particlesConfig.force){
        svgs.forEach((svg, index) => { draw(svg, index, particles, particlesConfig) })
      }

      // definitly bring back original px size for each particle
      svgs.forEach((svg, index) => { 
        svg.style.width = particles[index].size + "px"
        svg.style.height = particles[index].size + "px"
      })

    };



  });



  
  
  /// FIND FORCE in html ( .particleForce + data-force )
  /// e.g. <div class="particleForce" data-force="windLeft">

  const particleForce = document.querySelectorAll('.particleForce');

  particleForce.forEach((force) => {

    force.addEventListener('sal:in', () => {
      particlesConfig.force = force.getAttribute("data-force")
      console.debug("FORCE:START " + particlesConfig.force )
    });

    force.addEventListener('sal:out', () => {
      console.debug("FORCE:STOP " + particlesConfig.force )
    });

  })

 
 




});







function force(particles, particlesConfig){

  let svgs = document.querySelectorAll("#particles svg")

  svgs.forEach((svg, index) => {

    // windRight
    if (particlesConfig.force=="windRight")
    {
      cX = parseInt(svg.style.left,10)
      x = cX - particles[index].windRight
      if (x < -600) { x = particlesConfig.scene.width + 300 }
      if (x < -200 ) { svg.style.display = 'none' }
      if (x > particlesConfig.scene.width ) {
        svg.style.display = 'block'
        y = ~~(Math.random() * particlesConfig.scene.height)
        svg.style.top = y + "px"
      }
      svg.style.left = x + "px"
    }


    // windLeft
    if (particlesConfig.force=="windLeft")
    {
      cX = parseInt(svg.style.left,10)
      x = cX + particles[index].windLeft
      if (x > particlesConfig.scene.width + 600) { x = -600 }
      if (x > particlesConfig.scene.width ) { 
        svg.style.display = 'none'
        y = ~~(Math.random() * particlesConfig.scene.height)
        svg.style.top = y + "px" 
      }
      if (x < particlesConfig.scene.width ) { svg.style.display = 'block'
      }
      svg.style.left = x + "px"
    }



    // randomFloating
    if (particlesConfig.force=="randomFloating")
    {
      cX = parseInt(svg.style.left,10)
      cY = parseInt(svg.style.top,10)

      x = cX + particles[index].randomFloatingX
      y = cY + particles[index].randomFloatingY

      if ( x > particlesConfig.scene.width || x < -600  ) {  particles[index].randomFloatingX = -particles[index].randomFloatingX  }
      if ( y > particlesConfig.scene.height || y < -600 ) {  particles[index].randomFloatingY = -particles[index].randomFloatingY  }

      svg.style.left = x + "px"
      svg.style.top = y + "px"

    } 



  })


}







function draw(svg, index, particles, particlesConfig){

  svg.style.left = particles[index].x + "px"
  svg.style.top = particles[index].y + "px" 

  svg.style.width = particles[index].size + "px"
  svg.style.height = particles[index].size + "px"

  svg.animate({ fill: [ particlesConfig.color.purple, particlesConfig.color.pink, particlesConfig.color.aqua, particlesConfig.color.purple ]}, 
    { duration: particles[index].colorcycleTime, delay: 0, iterations: Infinity })

  svg.animate({ transform: ["rotate(0deg)","rotate(360deg)"] },
    { duration: particles[index].rotationTime, delay: 0, iterations: Infinity })

  svg.animate({ padding: ["0px" , particlesConfig.padding , "0px" ]},
    { duration: particles[index].paddingTime, delay: 0, iterations: Infinity })

  svg.animate({ opacity: [ 0.8, 1, 0.8] },
    { duration: particles[index].opacityTime, delay: 0, iterations: Infinity })

}









function create(p, particlesConfig){

  const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg")
  svg.setAttribute ("width", "128" )
  svg.setAttribute ("height", "128" )
  svg.setAttribute ("viewBox", "0 0 128 128")
  const path = document.createElementNS("http://www.w3.org/2000/svg", "path")
  path.setAttribute("d", p.artwork)
  svg.appendChild(path)
  document.getElementById("particles").appendChild(svg)

}









class Particle{

  constructor(particlesConfig){
    this.artwork = particlesConfig.paths[~~(Math.random() * particlesConfig.paths.length)]
    this.size = ~~(Math.random() * (particlesConfig.size.max - particlesConfig.size.min) + particlesConfig.size.min)
    this.x = ~~(Math.random() * (particlesConfig.scene.width + this.size) - this.size )
    this.y = ~~(Math.random() * (particlesConfig.scene.height + this.size) - this.size )
    this.colorcycleTime = ~~(Math.random() * (particlesConfig.colorcycleTime.max - particlesConfig.colorcycleTime.min) + particlesConfig.colorcycleTime.min)
    this.rotationTime = ~~(Math.random() * (particlesConfig.rotationTime.max - particlesConfig.rotationTime.min) + particlesConfig.rotationTime.min)
    this.paddingTime = ~~(Math.random() * (particlesConfig.paddingTime.max - particlesConfig.paddingTime.min) + particlesConfig.paddingTime.min)
    this.opacityTime = ~~(Math.random() * (particlesConfig.opacityTime.max - particlesConfig.opacityTime.min) + particlesConfig.opacityTime.min)
    this.windRight = ~~(Math.random() * (particlesConfig.windRight.max - particlesConfig.windRight.min) + particlesConfig.windRight.min)
    this.windLeft = ~~(Math.random() * (particlesConfig.windLeft.max - particlesConfig.windLeft.min) + particlesConfig.windLeft.min)
    this.randomFloatingX = ~~(Math.random() * (particlesConfig.randomFloating.max - particlesConfig.randomFloating.min) + particlesConfig.randomFloating.min)
    this.randomFloatingY = ~~(Math.random() * (particlesConfig.randomFloating.max - particlesConfig.randomFloating.min) + particlesConfig.randomFloating.min)
  }

}













