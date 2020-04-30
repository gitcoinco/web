let CURRENT_MODE;
const LIGHT_MODE = 'light';
const DARK_MODE = 'dark';

const isDarkMode = window.matchMedia('(prefers-color-scheme: dark)').matches;
const theme = window.localStorage.getItem('theme');

if (theme === 'dark' || (!theme && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
  document.documentElement.classList.add('dark-mode');
}

document.addEventListener('DOMContentLoaded', subscribe, false);

function subscribe() {
  // Handle preferred user theme mode
  document.getElementById('theme-switcher').addEventListener('click', onToggleMode);

  // Load theme if persisted
  const mode = window.localStorage.getItem('theme');

  if (mode) {
    return activateMode(mode);
  }

  // Attempt to detect theme mode
  const isDarkMode = window.matchMedia('(prefers-color-scheme: dark)').matches;
  const isLightMode = window.matchMedia('(prefers-color-scheme: light)').matches;

  window.matchMedia('(prefers-color-scheme: dark)').addListener(e => e.matches && activateDarkMode());
  window.matchMedia('(prefers-color-scheme: light)').addListener(e => e.matches && activateLightMode());

  if (isDarkMode) {
    activateDarkMode();
  }

  if (isLightMode) {
    activateLightMode();
  }
}

function onToggleMode() {
  const mode = CURRENT_MODE === LIGHT_MODE ? DARK_MODE : LIGHT_MODE;

  window.localStorage.setItem('theme', mode);
  activateMode(mode);
}

function activateLightMode() {
  activateMode(LIGHT_MODE);
}

function activateDarkMode() {
  activateMode(DARK_MODE);
}

function activateMode(mode) {
  CURRENT_MODE = mode;

  // Toggle root dark-mode class
  document.documentElement.classList.toggle('dark-mode', mode === DARK_MODE);
}
