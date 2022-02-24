Vue.component('progress-bar', {
  delimiters: [ '[[', ']]' ],
  data() {
    return {
      signals: [
        {
          text: 'Eligibility & Discovery',
          active: true
        },
        {
          text: 'Grant Details'
        },
        {
          text: 'Eligibility & Discovery'
        },
        {
          text: 'Eligibility & Discovery'
        }
      ]
    };
  }
});