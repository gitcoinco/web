Vue.component('grant-creation-wrapper', {
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
  template: '#grant-creation-wrapper'
});