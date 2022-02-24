Vue.component('progress-bar', {
  delimiters: [ '[[', ']]' ],
  data() {
    return {
      signals: [
        {
          text: 'Eligibility & Discovery'
        },
        {
          text: 'Grant Details'
        }
      ]
    };
  }
});