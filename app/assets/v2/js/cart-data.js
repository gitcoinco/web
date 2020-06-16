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

  static share_url() {
    const donations = this.loadCart();
    let bulk_add_cart = 'https://gitcoin.co/grants/cart/bulk-add/';

    for (let i = 0; i < donations.length; i += 1) {
      const donation = donations[i];

      bulk_add_cart += String(donation['grant_id']) + ',';
    }
    return bulk_add_cart;
  }

  static addToCart(grantData) {
    if (this.cartContainsGrantWithId(grantData.grant_id)) {
      return;
    }

    // Add donation defaults
    var network = document.web3network;

    if (!network) {
      network = 'mainnet';
    }
    const acceptsAllTokens = (grantData.grant_token_address === '0x0000000000000000000000000000000000000000');

    let accptedTokenName;

    try {
      accptedTokenName = tokenAddressToDetailsByNetwork(grantData.grant_token_address, network).name;
    } catch (e) {
      // When numbers are too small toWei fails because there's too many decimal places
      accptedTokenName = 'DAI';
    }

    if (acceptsAllTokens || 'DAI' == accptedTokenName) {
      grantData.grant_donation_amount = 5;
      grantData.grant_donation_currency = 'DAI';
    } else {
      grantData.grant_donation_amount = 0.01;
      grantData.grant_donation_currency = 'ETH';
    }

    grantData.grant_donation_num_rounds = 1;
    grantData.grant_donation_clr_match = 0;

    let cartList = this.loadCart();

    cartList.push(grantData);
    this.setCart(cartList);
  }

  static removeIdFromCart(grantId) {
    let cartList = this.loadCart();

    const newList = cartList.filter(grant => {
      return (grant.grant_id !== grantId);
    });

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
