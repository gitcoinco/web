// LOTTIE PLAYER
//
// https://github.com/airbnb/lottie-web

var lottieBackground = bodymovin.loadAnimation({
  container: document.getElementById('lottieBackground'),
  renderer: 'svg',
  loop: true,
  autoplay: true,
  path: lottieAnimation,
    rendererSettings: {
      preserveAspectRatio: 'xMidYMid slice'
    }
})

console.log("init lottie background");
console.log("load lottieAnimation : " + animation);


