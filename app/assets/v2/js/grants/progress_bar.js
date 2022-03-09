Vue.component('progress-bar', {
  props: {
    steps: { type: Array, 'default': () => [] }
  },
  delimiters: [ '[[', ']]' ],
  computed: {
    lineWidth() {
      return (100 / this.steps.length) * (this.steps.length - 1);
    },
    margin() {
      return (100 / this.steps.length) / 2;
    }
  }
});
