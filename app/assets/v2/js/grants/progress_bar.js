Vue.component('progress-bar', {
  props: {
    steps: { type: Array, 'default': () => [] }
  },
  delimiters: [ '[[', ']]' ]
});