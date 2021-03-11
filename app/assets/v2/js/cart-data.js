class CartData {

  static hasItems() {
    return this.loadCart().length > 0;
  }

  static length() {
    return this.loadCart().length;
  }

  static cartContainsGrantWithId(grantId) {
    grantId = Number(grantId);
    const cart = this.loadCart();
    const idList = cart.map((grant) => Number(grant.grant_id));

    return idList.includes(grantId);
  }

  static share_url(title) {
    const checkedOut = this.loadCheckedOut();
    const donations = (checkedOut.length > 0 ? checkedOut : this.loadCart());
    let bulk_add_cart = `${window.location.host}/grants/cart/bulk-add/`;
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
    // Enforce that grant ID is a number, since backend returns it as a number
    grantData.grant_id = Number(grantData.grant_id);
    
    // Return if grant is already in cart
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

    if (grantData.tenants.includes('ZCASH')) {
      if (!grantData.grant_donation_amount) {
        grantData.grant_donation_amount = 0.01;
      }
      if (!grantData.grant_donation_currency) {
        grantData.grant_donation_currency = 'ZEC';
      }
    } else if (grantData.tenants.includes('CELO')) {
      if (!grantData.grant_donation_amount) {
        grantData.grant_donation_amount = 0.1;
      }
      if (!grantData.grant_donation_currency) {
        grantData.grant_donation_currency = 'CELO';
      }
    } else if (grantData.tenants.includes('ZIL')) {
      if (!grantData.grant_donation_amount) {
        grantData.grant_donation_amount = 0.1;
      }
      if (!grantData.grant_donation_currency) {
        grantData.grant_donation_currency = 'ZIL';
      }
    } else if (grantData.tenants.includes('HARMONY')) {
      if (!grantData.grant_donation_amount) {
        grantData.grant_donation_amount = 1;
      }
      if (!grantData.grant_donation_currency) {
        grantData.grant_donation_currency = 'ONE';
      }
    } else if (grantData.tenants.includes('BINANCE')) {
      if (!grantData.grant_donation_amount) {
        grantData.grant_donation_amount = 1;
      }
      if (!grantData.grant_donation_currency) {
        grantData.grant_donation_currency = 'BNB';
      }
    } else if (grantData.tenants.includes('POLKADOT')) {
      if (!grantData.grant_donation_amount) {
        grantData.grant_donation_amount = 1;
      }
      if (!grantData.grant_donation_currency) {
        grantData.grant_donation_currency = 'DOT';
      }
    } else if (grantData.tenants.includes('KUSAMA')) {
      if (!grantData.grant_donation_amount) {
        grantData.grant_donation_amount = 1;
      }
      if (!grantData.grant_donation_currency) {
        grantData.grant_donation_currency = 'KSM';
      }
    } else if (grantData.tenants.includes('RSK')) {
      if (!grantData.grant_donation_amount) {
        grantData.grant_donation_amount = 0.0001;
      }
      if (!grantData.grant_donation_currency) {
        grantData.grant_donation_currency = 'R-BTC';
      }
    } else if (acceptsAllTokens || 'DAI' == accptedTokenName) {
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

    grantData.payment_status = 'waiting';
    grantData.txnid = null;

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
    grantId = Number(grantId);

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

  // Updates localStorage with the latest grant data from the backend and returns the new cart
  static async updateCart() {
    // Read cart data from local storage
    const cartData = this.loadCart();

    // Make sure no grants have empty currencies, and if so default to 0.001 ETH. This prevents cart
    // from being stuck as 'loading' if a currency is empty
    cartData.forEach((grant, index) => {
      if (!grant.grant_donation_currency) {
        cartData[index].grant_donation_currency = 'ETH';
        cartData[index].grant_donation_amount = '0.001';
      }
    });

    // Get list of all grant IDs and fetch updated grant data from backend
    const grantIds = cartData.map((grant) => grant.grant_id);
    const url = `${window.location.origin}/grants/v1/api/grants?pks=${grantIds.join(',')}`;
    const response = await fetch(url);
    const latestGrantsData = (await response.json()).grants;

    // Update grant info with latest data
    cartData.forEach((grant, index) => {
      // Find the latestGrantsData entry with the same grant ID as this grant
      const grantIndex = latestGrantsData.findIndex((item) => Number(item.id) === Number(grant.grant_id));
      const latestGrantData = latestGrantsData[grantIndex];

      // Update with the grant data from server
      cartData[index].binance_payout_address = latestGrantData.binance_payout_address;
      cartData[index].celo_payout_address = latestGrantData.celo_payout_address;
      cartData[index].clr_round_num = latestGrantData.clr_round_num;
      cartData[index].grant_admin_address = latestGrantData.admin_address;
      cartData[index].grant_clr_prediction_curve = latestGrantData.clr_prediction_curve;
      cartData[index].grant_contract_address = latestGrantData.contract_address;
      cartData[index].grant_contract_version = latestGrantData.contract_version;
      cartData[index].grant_donation_num_rounds = 1; // always 1, since recurring contributions are not supported
      cartData[index].grant_id = Number(latestGrantData.id); // should already be a number, so this is an extra safety check
      cartData[index].grant_image_css = latestGrantData.image_css;
      cartData[index].grant_logo = latestGrantData.logo_url;
      cartData[index].grant_slug = latestGrantData.slug;
      cartData[index].grant_title = latestGrantData.title;
      cartData[index].grant_token_address = latestGrantData.token_address;
      cartData[index].grant_token_symbol = latestGrantData.token_symbol;
      cartData[index].grant_url = latestGrantData.url;
      cartData[index].harmony_payout_address = latestGrantData.harmony_payout_address;
      cartData[index].is_clr_eligible = latestGrantData.is_clr_eligible;
      cartData[index].is_on_team = latestGrantData.is_on_team;
      cartData[index].kusama_payout_address = latestGrantData.kusama_payout_address;
      cartData[index].polkadot_payout_address = latestGrantData.polkadot_payout_address;
      cartData[index].rsk_payout_address = latestGrantData.rsk_payout_address;
      cartData[index].tenants = latestGrantData.tenants;
      cartData[index].zcash_payout_address = latestGrantData.zcash_payout_address;
      cartData[index].zil_payout_address = latestGrantData.zil_payout_address;

      // Other localStorage properties not updated above:
      //   grant_donation_amount:     Existing localStorage value is preserved
      //   grant_donation_clr_match:  Updated in cart.js `grantData` watcher
      //   grant_donation_currency:   Existing localStorage value is preserved
      //   payment_status:            Updated on-demand in cart.js `updatePaymentStatus()` method
      //   token_local_id:            Existing localStorage value is preserved
      //   txnid:                     Updated on-demand in cart.js `updatePaymentStatus()` method
      //   uuid:                      TODO is this needed or can it be removed? Currently existing value is preserved
    });

    // Save the updated cart data to local storage and return it
    this.setCart(cartData);
    return cartData;
  }

  static loadCheckedOut() {
    const checkedOutList = localStorage.getItem('contributions_were_successful');

    if (!checkedOutList) {
      return [];
    }

    const parsedCheckout = JSON.parse(checkedOutList);

    if (!Array.isArray(parsedCheckout)) {
      return [];
    }

    return parsedCheckout;
  }

  static setCheckedOut(list) {
    localStorage.setItem('contributions_were_successful', JSON.stringify(list));
  }

  static clearCheckedOut() {
    localStorage.removeItem('contributions_were_successful');
  }
}
