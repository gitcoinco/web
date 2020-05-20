
// DOCUMENT

$(document).ready(function() {

    $('#js-addToCart-form').submit(function(event) {
        event.preventDefault();

        const formData = objectifySerialized($(this).serializeArray());
        addToCart(formData);
        // console.log("CART", loadCart());
    });
});

// HELPERS

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
    // TODO Update to use real data
    grantData.grant_donation_amount = 1;
    grantData.grant_donation_currency = 'DAI';
    grantData.grant_donation_type = 'one-time'; // options are 'one-time' and 'recurring'
    grantData.grant_donation_num_rounds = 0; // N/A if type is one-time
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
