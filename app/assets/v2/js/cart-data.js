class CartData {

  static hasItems() {
    return this.loadCart().length > 0;
  }

  static cartContainsGrantWithId(grantId) {
    const cart = this.loadCart();
    const idList = cart.map(grant => {
      return grant.grant_id;
    });

    return idList.includes(grantId);
  }

  static share_url(title) {
    const donations = this.loadCart();
    let bulk_add_cart = 'https://gitcoin.co/grants/cart/bulk-add/';

    let network = document.web3network;

    if (!network) {
      network = 'mainnet';
    }

    for (let i = 0; i < donations.length; i += 1) {
      const donation = donations[i];
      // eslint-disable-next-line no-loop-func
      const token = tokens(network).filter(t => t.name === donation.grant_donation_currency);
      let token_id = '';

      if (token.length) {
        token_id = token[0].id;
      }
      bulk_add_cart += `${donation['grant_id']};${donation['grant_donation_amount']};${token_id},`;
    }

    if (document.contxt['github_handle']) {
      bulk_add_cart += ':' + document.contxt['github_handle'];
    }

    if (title && typeof title != 'undefined') {
      bulk_add_cart += ':' + encodeURI(title);
    }

    return bulk_add_cart;
  }

  static addToCart(grantData, no_report) {
    if (this.cartContainsGrantWithId(grantData.grant_id)) {
      return;
    }

    // Add donation defaults
    var network = document.web3network;

    if (!network) {
      network = 'mainnet';
    }
    const acceptsAllTokens = (grantData.grant_token_address === '0x0000000000000000000000000000000000000000' ||
      grantData.grant_token_address === '0x0');

    let accptedTokenName;

    try {
      const token = tokenAddressToDetailsByNetwork(grantData.grant_token_address, network);

      grantData.token_local_id = token.id;
      accptedTokenName = token.name;
    } catch (e) {
      // When numbers are too small toWei fails because there's too many decimal places
      const dai = tokens(network).filter(t => t.name === 'DAI');

      if (dai.length) {
        grantData.token_local_id = dai[0].id;
      }
      accptedTokenName = 'DAI';
    }

    grantData.uuid = get_UUID();

    if (acceptsAllTokens || 'DAI' == accptedTokenName) {
      if (!grantData.grant_donation_amount) {
        grantData.grant_donation_amount = 5;
      }
      if (!grantData.grant_donation_currency) {
        grantData.grant_donation_currency = 'DAI';
      }
    } else {
      if (!grantData.grant_donation_amount) {
        grantData.grant_donation_amount = 0.01;
      }
      grantData.grant_donation_currency = 'ETH';
    }

    grantData.grant_donation_num_rounds = 1;
    grantData.grant_donation_clr_match = 0;

    let cartList = this.loadCart();

    cartList.push(grantData);
    this.setCart(cartList);

    if (!no_report) {
      fetchData(`/grants/${grantData.grant_id}/activity`, 'POST', {
        action: 'ADD_ITEM',
        metadata: JSON.stringify(cartList)
      }, {'X-CSRFToken': $("input[name='csrfmiddlewaretoken']").val()});
    }
  }

  static removeIdFromCart(grantId) {
    let cartList = this.loadCart();

    const newList = cartList.filter(grant => grant.grant_id !== grantId);

    fetchData(`/grants/${grantId}/activity`, 'POST', {
      action: 'REMOVE_ITEM',
      metadata: JSON.stringify(newList)
    }, {'X-CSRFToken': $("input[name='csrfmiddlewaretoken']").val()});

    this.setCart(newList);
  }

  static updateCartItem(grantId, field, value) {
    let cartList = this.loadCart();

    let grant = null;

    for (let index = 0; index < cartList.length; index++) {
      const maybeGrant = cartList[index];

      if (maybeGrant.grant_id === grantId) {
        grant = maybeGrant;
        break;
      }
    }

    if (null === grant) {
      throw new Error(`Tried to update grant with Id ${grantId} that is not in cart`);
    }

    grant[field] = value;

    this.setCart(cartList);
  }

  static clearCart() {
    let cartList = this.loadCart();

    fetchData('/grants/0/activity', 'POST', {
      action: 'CLEAR_CART',
      metadata: JSON.stringify(cartList),
      bulk: true
    }, {'X-CSRFToken': $("input[name='csrfmiddlewaretoken']").val()});

    localStorage.setItem('grants_cart', JSON.stringify([]));
    applyCartMenuStyles();
  }

  static loadCart() {
    const cartList = localStorage.getItem('grants_cart');

    if (!cartList) {
      return [];
    }

    const parsedCart = JSON.parse(cartList);

    if (!Array.isArray(parsedCart)) {
      return [];
    }

    return parsedCart;
  }

  static setCart(list) {
    localStorage.setItem('grants_cart', JSON.stringify(list));
    applyCartMenuStyles();
  }
}
