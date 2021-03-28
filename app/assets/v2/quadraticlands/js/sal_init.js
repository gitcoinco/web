console.log("init scroll animation  library");


// SCROLL ANIMATION LIBRARY () SAL )
//
// https://github.com/mciastek/sal

// fade slide-up slide-down slide-left slide-right
// zoom-in zoom-out flip-up flip-down flip-left flip-right

// add data atributes to html code



// important to listen to scroll in events for particle start stop
const particleForce = document.querySelectorAll(".particleForce"); 
particleForce.forEach(element => {
    element.setAttribute("data-sal", "fade");
    element.setAttribute("data-sal-delay", "100");
    element.setAttribute("data-sal-duration", "1800");
});


/*  lets get rid of that fade in animations , it sucks. 

const h1 = document.querySelectorAll("h1");
h1.forEach(element => {
    element.setAttribute("data-sal", "flip-up");
    element.setAttribute("data-sal-delay", "100");
    element.setAttribute("data-sal-duration", "300");
});


const btn = document.querySelectorAll(".btn");
btn.forEach(element => {
    element.setAttribute("data-sal", "flip-up");
    element.setAttribute("data-sal-delay", "300");
    element.setAttribute("data-sal-duration", "500");
});


const figure = document.querySelectorAll("figure");
figure.forEach(element => {
    element.setAttribute("data-sal", "fade");
    element.setAttribute("data-sal-delay", "100");
    element.setAttribute("data-sal-duration", "1800");
});
*/


// init sal

sal({
  threshold: 0.3,
  once: false
});