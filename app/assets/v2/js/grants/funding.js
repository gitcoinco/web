
// DOCUMENT

$(document).ready(function() {

  // Check localStorage to see if we need to show alert
  const shouldShowAlert = Boolean(localStorage.getItem('contributions_were_successful'));

  if (shouldShowAlert) {
    const numberOfContributions = Number(localStorage.getItem('contributions_count'));
    const grantWord = numberOfContributions === 1 ? 'grant' : 'grants';
    const message = `You have successfully funded ${numberOfContributions} ${grantWord}. Thank you for your contribution!`;

    _alert(message, 'success');
    localStorage.removeItem('contributions_were_successful');
    localStorage.removeItem('contributions_count');
    $('#tweetModal').modal('show');
    let donations = CartData.loadCart();

    if (donations.length) {
      let cart_html = 'You just funded: ';
      let bulk_add_cart = CartData.share_url();

      for (let i = 0; i < donations.length; i += 1) {
        const donation = donations[i];

        cart_html += '<li><a href=' + donation.grant_url + ' target=_blank>' + donation['grant_title'] + '</a> for ' + donation['grant_donation_amount'] + ' ' + donation['grant_donation_currency'] + ' (+' + donation['grant_donation_clr_match'] + ' DAI match)</li>';
      }
      cart_html += '<HR><a href=' + bulk_add_cart + ' target=_blank>Here is a handy link</a> for sharing this collection with others.';
      $("<span class='mt-2 mb-2 w-100'>" + cart_html + '</span>').insertBefore($('#tweetModal span.copy'));
      $('#tweetModal a.button').attr('href', 'https://twitter.com/intent/tweet?text=I%20just%20funded%20these%20' + donations.length + '%20grants%20on%20@gitcoin%20=%3E%20' + bulk_add_cart);
      $('#tweetModal a.button').text('Tweet about it');
    }
    CartData.setCart([]);
  }

  $('#js-addToCart-form').submit(function(event) {
    event.preventDefault();

    const formData = objectifySerialized($(this).serializeArray());

    CartData.addToCart(formData);

    showSideCart();
  });

  $('.infinite-container').on('submit', '.js-addDetailToCart-form', function(event) {
    event.preventDefault();

    const formData = objectifySerialized($(this).serializeArray());

    CartData.addToCart(formData);

    showSideCart();
  });

  $('#close-side-cart').click(function() {
    hideSideCart();
  });

  $('#side-cart-data').on('click', '#apply-to-all', async function() {
    // Get preferred cart data
    let cartData = CartData.loadCart();
    const network = document.web3network || 'mainnet';
    const selected_grant_index = $(this).data('id');
    const preferredAmount = cartData[selected_grant_index].grant_donation_amount;
    const preferredTokenName = cartData[selected_grant_index].grant_donation_currency;
    const preferredTokenAddress = tokens(network)
      .filter(token => token.name === preferredTokenName)
      .map(token => token.addr)[selected_grant_index];

    // Get fallback amount in ETH (used when token is not available for a grant)
    const url = `${window.location.origin}/sync/get_amount?amount=${preferredAmount}&denomination=${preferredTokenName}`;
    const response = await fetch(url);
    const fallbackAmount = (await response.json())[0].eth;

    // Update cart values
    cartData.forEach((grant, index) => {
      const acceptsAllTokens = (grant.grant_token_address === '0x0000000000000000000000000000000000000000');
      const acceptsSelectedToken = grant.grant_token_address === preferredTokenAddress;

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
          <div class="col-2">
            <img src="${grant.grant_logo}" alt="Grant logo" width="40">
          </div>
          <div class="col-9">
              ${grant.grant_title}
          </div>
          <div class="col-1" style="opacity: 40%">
            <i id="side-cart-row-remove-${grant.grant_id}" class="fas fa-trash-alt" style="cursor: pointer"></i>
          </div>
        </div>
        <div class="form-row">
          <div class="col-2"></div>
          <div class="col-5">
            <input type="number" id="side-cart-amount-${grant.grant_id}" class="form-control" value="${grant.grant_donation_amount}">
          </div>
          <div class="col-5">
            <select id="side-cart-currency-${grant.grant_id}" class="form-control">
    `;

  cartRow += tokenOptionsForGrant(grant);

  cartRow += `
            </select>
          </div>
        </div>
        <div class="form-row">
          <div class="col-2"></div>
          <div class="col-auto font-smaller-3 pt-1 text-highlight-gc-blue" style="cursor:pointer;" data-id="${index}" id="apply-to-all">
            Apply to all
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

  let tokenDataList = tokens(network);
  const acceptsAllTokens = (grant.grant_token_address === '0x0000000000000000000000000000000000000000');

  let options = '';

  if (!acceptsAllTokens) {
    options += `
            <option value="ETH">ETH</option>
        `;

    tokenDataList = tokenDataList.filter(tokenData => {
      return (tokenData.addr === grant.grant_token_address);
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
                <option value="${tokenData.name}">${tokenData.name}</option>
            `;
    }
  }

  return options;
}

function showSideCart() {
  // Remove elements in side cart
  $('#side-cart-data')
    .find('div.side-cart-row')
    .remove();

  // Add all elements in side cart
  let cartData = CartData.loadCart();

  cartData.forEach((grant, index) => {
    const cartRowHtml = sideCartRowForGrant(grant, index);

    $('#side-cart-data').append(cartRowHtml);

    // Register remove click handler
    $(`#side-cart-row-remove-${grant.grant_id}`).click(function() {
      $(`#side-cart-row-${grant.grant_id}`).remove();
      CartData.removeIdFromCart(grant.grant_id);
    });

    // Register change amount handler
    $(`#side-cart-amount-${grant.grant_id}`).change(function() {
      const newAmount = parseFloat($(this).val());

      CartData.updateCartItem(grant.grant_id, 'grant_donation_amount', newAmount);
    });

    // Select appropriate currency
    $(`#side-cart-currency-${grant.grant_id}`).val(grant.grant_donation_currency);

    // Register currency change handler
    $(`#side-cart-currency-${grant.grant_id}`).change(function() {
      CartData.updateCartItem(grant.grant_id, 'grant_donation_currency', $(this).val());
    });
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
  $('#grants-details > div').toggleClass('col-12 col-md-8 col-lg-9 d-none d-md-block');

  $('#side-cart').toggle();
  $('#side-cart').toggleClass('col-12 col-md-4 col-lg-3');
  $('#funding-card').toggleClass('mr-md-5 mr-md-3 d-none d-lg-block');
}
