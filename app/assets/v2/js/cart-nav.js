Vue.component('gc-cart-content', {
  template: '#gc-cart-content',
  delimiters: [ '[[', ']]' ],
  props: {
    items: Array
  },
  methods: {
    removeItem: function(grant_id) {
      // remove the item
      CartData.removeIdFromCart(grant_id);
      // refresh the data
      this.items = CartData.loadCart();
      // remove on grants pages
      if (typeof appGrants !== 'undefined') {
        appGrants.grants.filter((grantSingle) => {
          if (Number(grantSingle.id) === Number(grant_id)) {
            grantSingle.isInCart = false;
          }
        });
      } else if (typeof appGrantDetails !== 'undefined' && appGrantDetails.grant.id === Number(grant_id)) {
        appGrantDetails.grant.isInCart = false;
      }
    }
  }
});

if (document.getElementById('gc-cart')) {
  var app = new Vue({
    delimiters: [ '[[', ']]' ],
    el: '#gc-cart',
    data: {
      items: []
    },
    methods: {
      init: function() {
        // update items each time we open the dropdown
        this.items = CartData.loadCart();
      }
    }
  });

  $(document).on('click', '.gc-cart .dropdown-menu', function(event) {
    event.stopPropagation();
  });
}

