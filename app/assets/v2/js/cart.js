let grantHeaders = [ 'Grant', 'Amount', 'Type', 'Total CLR Match Amount' ];
let grantData = [];

Vue.component('grants-cart', {
  delimiters: [ '[[', ']]' ],

  data: function() {
    return {
      grantHeaders,
      grantData
    };
  },

  mounted() {
    // Read array of grants in cart from localStorage
    this.grantData = JSON.parse(window.localStorage.getItem('grants_cart'));
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