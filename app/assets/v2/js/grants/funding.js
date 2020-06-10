
// DOCUMENT

$(document).ready(function() {

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

    $("#close-side-cart").click(function() {
        hideSideCart();
    });
});

// HELPERS

function sideCartRowForGrant(grant) {
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
        </div>
    `;

    return cartRow;
}

function tokenOptionsForGrant(grant) {
    let tokenDataList = tokens(network);
    const acceptsAllTokens = (grant.grant_token_address === "0x0000000000000000000000000000000000000000");

    let options = "";

    if (!acceptsAllTokens) {
        options +=  `
            <option value="ETH">ETH</option>
        `;

        tokenDataList = tokenDataList.filter( tokenData => {
            return (tokenData.addr === grant.grant_token_address);
        });
    }

    for (let index = 0; index < tokenDataList.length; index++) {
        const tokenData = tokenDataList[index];

        if (tokenData.divider) {
            options += `
                <option disabled>_________</option>
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
    $("#side-cart-data")
        .find("div.side-cart-row")
        .remove();

    // Add all elements in side cart
    let cartData = CartData.loadCart();
    cartData.forEach( grant => {
        const cartRowHtml = sideCartRowForGrant(grant);
        $("#side-cart-data").append(cartRowHtml);

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
    $('#grants-details').toggleClass('col-12');
    $('#grants-details').toggleClass('col-md-8');
    $('#grants-details').toggleClass('col-lg-9');
    $('#grants-details').toggleClass('d-none');
    $('#grants-details').toggleClass('d-md-block');

    $('#side-cart').toggle();
    $('#side-cart').toggleClass('col-12');
    $('#side-cart').toggleClass('col-md-4');
    $('#side-cart').toggleClass('col-lg-3');

    $('#funding-card').toggleClass('mr-md-5');
    $('#funding-card').toggleClass('mr-md-3');
    $('#funding-card').toggleClass('d-none');
    $('#funding-card').toggleClass('d-lg-block');
}

function objectifySerialized(data) {
    let objectData = {};

    for (let i = 0; i < data.length; i++) {
        const item = data[i];
        objectData[item.name] = item.value;
    }

    return objectData;
}
