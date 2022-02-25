Vue.component('form-wrapper', {
  delimiters: [ '[[', ']]' ],
  props: {
    heading: {
      type: String
    },
    'current-step': {
      type: Number, required: true
    },
    'total-steps': {
      type: Number, required: true
    }
  },
  template: '#form-wrapper'
});