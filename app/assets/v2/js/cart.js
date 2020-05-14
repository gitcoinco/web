let testString = 'qwertyyyyyy';

Vue.component('grants-cart', {
  delimiters: [ '[[', ']]' ],
  // props: [ 'tribe', 'is_my_org' ],
  data: function() {
    return {
      testString
    };
  },

  mounted() {
    //
  },
  created() {
    //
  },
  beforeMount() {
    window.addEventListener('scroll', () => {
      this.bottom = this.bottomVisible();
    }, false);
  },
  beforeDestroy() {
    window.removeEventListener('scroll', () => {
      this.bottom = this.bottomVisible();
    });
  }
});

if (document.getElementById('gc-grants-cart')) {

  var app = new Vue({
    delimiters: [ '[[', ']]' ],
    el: '#gc-grants-cart',
    data: {
      testString
    },
    mounted() {
      //
    },
    created() {
      //
    },
    beforeMount() {
      window.addEventListener('scroll', () => {
        this.bottom = this.bottomVisible();
      }, false);
    },
    beforeDestroy() {
      window.removeEventListener('scroll', () => {
        this.bottom = this.bottomVisible();
      });
    }
  });
}