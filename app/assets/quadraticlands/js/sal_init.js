console.log("init scroll animation  library");


// SCROLL ANIMATION LIBRARY () SAL )
//
// https://github.com/mciastek/sal

// fade slide-up slide-down slide-left slide-right
// zoom-in zoom-out flip-up flip-down flip-left flip-right

// add data atributes to html code


const h1 = document.querySelectorAll("h1");
const h3 = document.querySelectorAll("h3");
const btn = document.querySelectorAll(".btn");
const figure = document.querySelectorAll("figure");

h3.forEach(element => {
    element.setAttribute("data-sal", "zoom-in");
    element.setAttribute("data-sal-delay", "0");
    element.setAttribute("data-sal-duration", "1500");
});

h1.forEach(element => {
    element.setAttribute("data-sal", "flip-up");
    element.setAttribute("data-sal-delay", "100");
    element.setAttribute("data-sal-duration", "300");
});

btn.forEach(element => {
    element.setAttribute("data-sal", "flip-up");
    element.setAttribute("data-sal-delay", "300");
    element.setAttribute("data-sal-duration", "500");
});

figure.forEach(element => {
    element.setAttribute("data-sal", "fade");
    element.setAttribute("data-sal-delay", "100");
    element.setAttribute("data-sal-duration", "1800");
});


// init sal

sal({
  threshold: 0.3,
  once: false
});