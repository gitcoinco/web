let testString = 'qwertyyyyyy';
let numberOfGrants = 'TBD';

Vue.component('grants-cart', {
  delimiters: [ '[[', ']]' ],
  // props: [ 'tribe', 'is_my_org' ],
  data: function() {
    return {
      testString,
      numberOfGrants
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
      numberOfGrants
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