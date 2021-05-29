// DOCUMENT
let allTokens;
const fetchTokens = async() => {
  const tokensResponse = await fetch('/api/v1/tokens');

  allTokens = await tokensResponse.json();
};

fetchTokens();

$(document).ready(function() {

  $('#js-addToCart-form').submit(function(event) {
    event.preventDefault();

    // const formData = objectifySerialized($(this).serializeArray());
    // const formData = objectifySerialized($(this).serializeArray());

    CartData.addToCart(grantDetails);

    showSideCart();
  });

  $('.infinite-container').on(
    'submit',
    '.js-addDetailToCart-form',
    function(event) {
      event.preventDefault();

      const formData = objectifySerialized($(this).serializeArray());

      CartData.addToCart(formData);

      showSideCart();
    }
  );

  $('#close-side-cart').click(function() {
    hideSideCart();
  });

  $('#side-cart-data').on('click', '#apply-to-all', async function() {
    // Get preferred cart data
    let cartData = CartData.loadCart();
    const network = document.web3network || 'mainnet';
    const selected_grant_index = $(this).data('id');
    const preferredAmount =
      cartData[selected_grant_index].grant_donation_amount;
    const preferredTokenName =
      cartData[selected_grant_index].grant_donation_currency;
    const preferredTokenAddress = tokens(network)
      .filter((token) => token.name === preferredTokenName)
      .map((token) => token.addr)[selected_grant_index];

    // Get fallback amount in ETH (used when token is not available for a grant)
    const url = `${window.location.origin}/sync/get_amount?amount=${preferredAmount}&denomination=${preferredTokenName}`;
    const response = await fetch(url);
    const fallbackAmount = (await response.json())[0].eth;

    // Update cart values
    cartData.forEach((grant, index) => {
      const acceptsAllTokens =
        grant.grant_token_address ===
        '0x0000000000000000000000000000000000000000';
      const acceptsSelectedToken =
        grant.grant_token_address === preferredTokenAddress;

      if (acceptsAllTokens || acceptsSelectedToken) {
        // Use the user selected option
        cartData[index].grant_donation_amount = preferredAmount;
        cartData[index].grant_donation_currency = preferredTokenName;
      } else {
        // If the selected token is not available, fallback to ETH
        cartData[index].grant_donation_amount = fallbackAmount;
        cartData[index].grant_donation_currency = 'ETH';
      }
    }); // end cartData.forEach

    // Update cart
    CartData.setCart(cartData);
    showSideCart();
  });
});

// HELPERS

function sideCartRowForGrant(grant, index) {
  let cartRow = `
      <div id="side-cart-row-${grant.grant_id}" class="side-cart-row mb-3">
        <div class="form-row mb-2">
          <div class="d-flex col-2 justify-content-center" style="overflow:hidden;">
            <img src="${grant.grant_logo}" alt="Grant logo" width="40">
          </div>
          <div class="col-8 line-clamp">
              ${grant.grant_title}
          </div>
          <div class="col-2 text-right" style="opacity: 40%;">
            <i id="side-cart-row-remove-${grant.grant_id}" class="fas fa-trash-alt" style="cursor: pointer"></i>
          </div>
        </div>
        <div class="form-row">
          <div class="d-flex col-2"></div>
          <div class="col-5">
            <input type="number" id="side-cart-amount-${grant.grant_id}" class="form-control" value="${grant.grant_donation_amount}">
          </div>
          <div class="col-5">
            <select id="side-cart-currency-${grant.grant_id}" class="form-control" style="width:100%;">
    `;

  cartRow += tokenOptionsForGrant(grant);

  cartRow += `
            </select>
          </div>
        </div>

      </div>
  `;

  return cartRow;
}

function tokenOptionsForGrant(grant) {
  var network = document.web3network;

  if (!network) {
    network = 'mainnet';
  }

  // let tokenDataList = tokens(network);
  let tokenDataList = allTokens.filter(
    (token) => token.network === networkName || 'mainnet'
  );
  let tokenDefault = 'ETH';

  if (grant.tenants && grant.tenants.includes('ZCASH')) {
    tokenDataList = tokenDataList.filter((token) => token.chainId === 123123);
    tokenDefault = 'ZEC';
  } else if (grant.tenants && grant.tenants.includes('CELO')) {
    tokenDataList = tokenDataList.filter((token) => token.chainId === 42220);
    tokenDefault = 'CELO';
  } else if (grant.tenants && grant.tenants.includes('ZIL')) {
    tokenDataList = tokenDataList.filter((token) => token.chainId === 102);
    tokenDefault = 'ZIL';
  } else if (grant.tenants && grant.tenants.includes('HARMONY')) {
    tokenDataList = tokenDataList.filter((token) => token.chainId === 1000);
    tokenDefault = 'ONE';
  } else if (grant.tenants && grant.tenants.includes('BINANCE')) {
    tokenDataList = tokenDataList.filter((token) => token.chainId === 56);
    tokenDefault = 'BNB';
  } else if (grant.tenants && grant.tenants.includes('POLKADOT')) {
    tokenDataList = tokenDataList.filter((token) => token.chainId === 58);
    tokenDefault = 'DOT';
  } else if (grant.tenants && grant.tenants.includes('KUSAMA')) {
    tokenDataList = tokenDataList.filter((token) => token.chainId === 59);
    tokenDefault = 'KSM';
  } else if (grant.tenants && grant.tenants.includes('RSK')) {
    tokenDataList = tokenDataList.filter(token => token.chainId === 30);
    tokenDefault = 'RBTC';
  } else {
    tokenDataList = tokenDataList.filter((token) => token.chainId === 1);
  }

  const acceptsAllTokens =
    grant.grant_token_address ===
      '0x0000000000000000000000000000000000000000' ||
    grant.grant_token_address === '0x0';

  let options = '';

  if (!acceptsAllTokens) {
    options += `
            <option value="${tokenDefault}">${tokenDefault}</option>
        `;

    tokenDataList = tokenDataList.filter((tokenData) => {
      return tokenData.address === grant.grant_token_address;
    });
  }

  for (let index = 0; index < tokenDataList.length; index++) {
    const tokenData = tokenDataList[index];

    if (tokenData.divider) {
      options += `
                <option disabled>&mdash;&mdash;&mdash;&mdash;</option>
            `;
    } else {
      options += `
                <option value="${tokenData.symbol}">${tokenData.symbol}</option>
            `;
    }
  }

  return options;
}

function showSideCart() {
  // Remove elements in side cart
  $('#side-cart-data').find('div.side-cart-row').remove();

  // Add all elements in side cart
  let cartData = CartData.loadCart();

  cartData.forEach((grant, index) => {
    const cartRowHtml = sideCartRowForGrant(grant, index);

    $('#side-cart-data').append(cartRowHtml);

    // Register remove click handler
    $(`#side-cart-row-remove-${grant.grant_id}`).click(function() {
      if (typeof appGrants !== 'undefined') {
        appGrants.grants.filter((grantSingle) => {
          if (Number(grantSingle.id) === Number(grant.grant_id)) {
            grantSingle.isInCart = false;
          }
        });
      } else if (
        typeof appGrantDetails !== 'undefined' &&
        appGrantDetails.grant.id === Number(grant.grant_id)
      ) {
        appGrantDetails.grant.isInCart = false;
      }

      $(`#side-cart-row-${grant.grant_id}`).remove();
      CartData.removeIdFromCart(grant.grant_id);
    });

    // Register change amount handler
    $(`#side-cart-amount-${grant.grant_id}`).change(function() {
      const newAmount = parseFloat($(this).val());

      CartData.updateCartItem(
        grant.grant_id,
        'grant_donation_amount',
        newAmount
      );
    });

    // Select appropriate currency
    $(`#side-cart-currency-${grant.grant_id}`).val(
      grant.grant_donation_currency
    );

    // Register currency change handler
    $(`#side-cart-currency-${grant.grant_id}`).change(function() {
      CartData.updateCartItem(
        grant.grant_id,
        'grant_donation_currency',
        $(this).val()
      );
    });

    $(`#side-cart-currency-${grant.grant_id}`).select2();
  });

  const isShowing = $('#side-cart').hasClass('col-12');

  if (!isShowing) {
    toggleSideCart();
  }

  // Scroll To top on mobile
  if (window.innerWidth < 768) {
    const cartTop = $('#side-cart').position().top;

    window.scrollTo(0, cartTop);
  }
}

function hideSideCart() {
  const isShowing = $('#side-cart').hasClass('col-12');

  if (!isShowing) {
    return;
  }

  toggleSideCart();
}

function toggleSideCart() {
  $('#grants-details > div').toggleClass(
    'col-12 col-md-8 col-lg-9 d-none d-md-block side-cart-open'
  );

  $('#side-cart').toggle();
  $('#side-cart').toggleClass('col-12 col-md-4 col-lg-3');
  $('#funding-card').toggleClass('mr-md-5 mr-md-3 d-none d-lg-block');
}
