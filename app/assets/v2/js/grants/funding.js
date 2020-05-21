
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

function showSideCart() {
    const isShowing = $('#side-cart').hasClass('col-3');

    if (isShowing) {
        return;
    }

    toggleSideCart();
}

function hideSideCart() {
    const isShowing = $('#side-cart').hasClass('col-3');

    if (!isShowing) {
        return;
    }

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
