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
  });

  $('.infinite-container').on(
    'submit',
    '.js-addDetailToCart-form',
    function(event) {
      event.preventDefault();

      const formData = objectifySerialized($(this).serializeArray());

      CartData.addToCart(formData);
    }
  );
});
