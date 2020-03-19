const MODE_LIGHT = 'light';
const MODE_DARK = 'dark';

const MODE_COLORS = {
  [MODE_LIGHT]: {
    '--main-bg': '#EFF3F6'
  },
  [MODE_DARK]: {
    '--main-bg': 'var(--gc-black)'
  }
};

$('document').ready(subscribe);

function subscribe() {
  const isDarkMode = window.matchMedia("(prefers-color-scheme: dark)").matches
  const isLightMode = window.matchMedia("(prefers-color-scheme: light)").matches
  const isNotSpecified = window.matchMedia("(prefers-color-scheme: no-preference)").matches
  const hasNoSupport = !isDarkMode && !isLightMode && !isNotSpecified;

  window.matchMedia("(prefers-color-scheme: dark)").addListener(e => e.matches && activateDarkMode())
  window.matchMedia("(prefers-color-scheme: light)").addListener(e => e.matches && activateLightMode())

  if(isDarkMode) activateDarkMode()
  if(isLightMode) activateLightMode()
  if(isNotSpecified || hasNoSupport) {
    console.log('You specified no preference for a color scheme or your browser does not support it. I schedule dark mode during night time.')
    now = new Date();
    hour = now.getHours();
    if (hour < 4 || hour >= 16) {
      activateDarkMode();
    }
  }
}

function activateLightMode() {
  console.log('light mode');
  activateMode(MODE_LIGHT);
}

function activateDarkMode() {
  console.log('dark mode');
  activateMode(MODE_DARK);
}

function activateMode(mode) {
  const rootElement = document.querySelector(':root');

  Object.entries(MODE_COLORS[mode]).forEach(([ k, v ]) => {
    rootElement.style.setProperty(k, v);
  });
}
