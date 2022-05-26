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
    },
    'disable-confirm': {
      type: Boolean,
      'default': false
    },
    isPreview: {
      type: Boolean,
      'default': false
    }
  },
  template: '#form-wrapper'
});
