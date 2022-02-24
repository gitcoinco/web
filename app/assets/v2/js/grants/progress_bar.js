Vue.component('progress-bar', {
  props: {
    steps: { type: Array, 'default': () => [] }
  },
  delimiters: [ '[[', ']]' ],
  computed: {
    lineWidth() {
      if (this.steps.length >= 4) {
        return 80;
      }
      return this.steps.length * 20 + 10;
    }
  }
});