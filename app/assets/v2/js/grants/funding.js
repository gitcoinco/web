
// DOCUMENT

$(document).ready(function() {

    $('#js-addToCart-form').submit(function(event) {
        event.preventDefault();

        const formData = objectifySerialized($(this).serializeArray());
        addToCart(formData);
        console.log("CART", loadCart());

        showSideCart();
    });

    $("#close-side-cart").click(function() {
        hideSideCart();
    });
});

// HELPERS

function sideCartRowForGrant(grant) {

    const cartRow = `
        <div class="side-cart-row mb-3">
            <div class="form-row mb-2">
                <div class="col-2">
                    <img src="${grant.grant_logo}" alt="Grant logo" width="40">
                </div>
                <div class="col-9">
                    ${grant.grant_title}
                </div>
                <div class="col-1" style="opacity: 40%">
                    <i class="fas fa-trash-alt" style="cursor: pointer"></i>
                </div>
            </div>
            <div class="form-row">
                <div class="col-2"></div>
                <div class="col-3">
                    <input type="number" class="form-control" value="${grant.grant_donation_amount}">
                </div>
                <div class="col-5">
                    <select class="form-control">
                        <option>DAI</option>
                        <option>ETH</option>
                    </select>
                </div>
            </div>
        </div>
    `;

    return cartRow;
}

function showSideCart() {
    const isShowing = $('#side-cart').hasClass('col-3');

    if (isShowing) {
        return;
    }

    // Add all elements in cart
    let cartData = loadCart();
    cartData.forEach( grantInCart => {
        const cartRow = sideCartRowForGrant(grantInCart);
        $("#side-cart-data").append(cartRow);
    });

    toggleSideCart();
}

function hideSideCart() {
    const isShowing = $('#side-cart').hasClass('col-3');

    if (!isShowing) {
        return;
    }

    // Remove elements in cart
    $("#side-cart-data")
        .find("div.side-cart-row")
        .remove();

    toggleSideCart();
}

function toggleSideCart() {
    $('#grants-details').toggleClass('col-12');
    $('#grants-details').toggleClass('col-9');
    $('#side-cart').toggleClass("col-3");
    $('#side-cart').toggleClass("col-0");
    $('#funding-card').toggleClass("mr-md-5");
    $('#funding-card').toggleClass("mr-md-3");
}

function objectifySerialized(data) {
    let objectData = {};

    for (let i = 0; i < data.length; i++) {
        const item = data[i];
        objectData[item.name] = item.value;
    }

    return objectData;
}

function cartContainsGrantWithSlug(grantSlug) {
    const cart = loadCart();
    const slugList = cart.map(grant => {
        return grant.grant_slug;
    });

    return slugList.includes(grantSlug);
}

function addToCart(grantData) {
    if (cartContainsGrantWithSlug(grantData.grant_slug)) {
        return;
    }

    // Add donation defaults
    grantData.grant_donation_amount = 1;
    grantData.grant_donation_currency = 'DAI';
    grantData.grant_donation_num_rounds = 1;
    grantData.grant_donation_clr_match = 250;

    let cartList = loadCart()
    cartList.push(grantData);
    setCart(cartList);
}

function loadCart() {
    let cartList = localStorage.getItem('grants_cart');

    if (!cartList) {
        return [];
    }

    return JSON.parse(cartList);
}

function setCart(list) {
    localStorage.setItem('grants_cart', JSON.stringify(list));
}
