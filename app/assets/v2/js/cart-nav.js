Vue.component('gc-cart-content', {
  template: '#gc-cart-content',
  delimiters: [ '[[', ']]' ],
  data: () => {

    return {
      items: []
    };
  },
  methods: {
    init: function() {
      // update items each time we open the dropdown
      this.items = CartData.loadCart();
    },
    removeGrantFromCart: function(grant_id) {
      // remove the item
      CartData.removeIdFromCart(grant_id);
      // refresh the data
      this.items = CartData.loadCart();
    }
  }
});

if (document.getElementById('gc-cart')) {
  var app = new Vue({
    delimiters: [ '[[', ']]' ],
    el: '#gc-cart',
    data: {
      cart_data_count: CartData.length()
    },
    methods: {
      updateCartCount: function(e) {
        this.cart_data_count = e.detail.list.length || 0;
      }
    },
    mounted() {
      // watch for cartUpdates
      window.addEventListener('cartDataUpdated', this.updateCartCount);
    },
    beforeDestroy() {
      // unwatch cartUpdates
      window.removeEventListener('cartDataUpdated', this.updateCartCount);
    }
  });

  $(document).on('click', '.gc-cart .dropdown-menu', function(event) {
    event.stopPropagation();
  });
}

