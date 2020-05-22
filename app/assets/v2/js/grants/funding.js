
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
                        <option value="DAI">DAI</option>
                        <option value="ETH">ETH</option>
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
    cartData.forEach( grant => {
        const cartRowHtml = sideCartRowForGrant(grant);
        $("#side-cart-data").append(cartRowHtml);

        // Register remove click handler
        $(`#side-cart-row-remove-${grant.grant_id}`).click(function() {
            $(`#side-cart-row-${grant.grant_id}`).remove();
            removeIdFromCart(grant.grant_id);
        });

        // Register change amount handler
        $(`#side-cart-amount-${grant.grant_id}`).change(function() {
            const newAmount = parseFloat($(this).val());
            updateCartItem(grant.grant_id, 'grant_donation_amount', newAmount);
        });

        // Select appropriate currency
        $(`#side-cart-currency-${grant.grant_id}`).val(grant.grant_donation_currency);

        // Register currency change handler
        $(`#side-cart-currency-${grant.grant_id}`).change(function() {
            updateCartItem(grant.grant_id, 'grant_donation_currency', $(this).val());
        });
    });

    toggleSideCart();
}

function hideSideCart() {
    const isShowing = $('#side-cart').hasClass('col-3');

    if (!isShowing) {
        return;
    }

    toggleSideCart();

    // Remove elements in cart
    $("#side-cart-data")
        .find("div.side-cart-row")
        .remove();
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

function cartContainsGrantWithId(grantId) {
    const cart = loadCart();
    const idList = cart.map(grant => {
        return grant.grant_id;
    });

    return idList.includes(grantId);
}

function addToCart(grantData) {
    if (cartContainsGrantWithId(grantData.grant_id)) {
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

function removeIdFromCart(grantId) {
    let cartList = loadCart();

    const newList = cartList.filter(grant => {
        return (grant.grant_id !== grantId);
    });

    setCart(newList);
}

function updateCartItem(grantId, field, value) {
    let cartList = loadCart();

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
