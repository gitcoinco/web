let testString = 'qwertyyyyyy';
let grantHeaders = [ 'Grant', 'Amount', 'Type', 'Total CLR Match Amount' ];
// Using dummy data for now
let grantData = [
  {
    grantImgPath: '../static/v2/images/gitcoinco.png',
    grantName: 'Burner Wallet',
    donationAmount: 1,
    donationCurrency: 'DAI',
    donationType: 'Recurring',
    numberOfRounds: 3,
    clrMatchAmount: 250
  },
  {
    grantImgPath: '../static/v2/images/gitcoinco.png',
    grantName: 'Covid Mask',
    donationAmount: 1,
    donationCurrency: 'DAI',
    donationType: 'Recurring',
    numberOfRounds: 2,
    clrMatchAmount: 250
  },
  {
    grantImgPath: '../static/v2/images/gitcoinco.png',
    grantName: 'Save Whales',
    donationAmount: 1,
    donationCurrency: 'ETH',
    donationType: 'One Time',
    numberOfRounds: undefined,
    clrMatchAmount: 250
  }
];

Vue.component('grants-cart', {
  delimiters: [ '[[', ']]' ],
  // props: [ 'tribe', 'is_my_org' ],
  data: function() {
    return {
      testString,
      grantHeaders,
      grantData
    };
  },

  mounted() {
    //
  },
  created() {
    //
  },
  beforeMount() {
    //
  },
  beforeDestroy() {
    //
  }
});

if (document.getElementById('gc-grants-cart')) {

  var app = new Vue({
    delimiters: [ '[[', ']]' ],
    el: '#gc-grants-cart',
    data: {
      testString,
      grantHeaders,
      grantData
    },
    mounted() {
      //
    },
    created() {
      //
    },
    beforeMount() {
      //
    },
    beforeDestroy() {
      //
    }
  });
}