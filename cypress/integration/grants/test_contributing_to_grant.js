describe('contributing to grant', () => {
  beforeEach(() => {
    cy.visit('http://localhost:8000/_administrationlogin');

    cy.get('[name=username]').type('root');
    cy.get('[name=password]').type('gitcoinco');
    cy.contains('Log in').click();

    cy.contains('Impersonate Users').click();
    cy.contains('test3').click();

    cy.get('#navbarDropdownWallet').as('wallet').click();
    cy.contains('Connect Wallet').click();
    cy.contains('MetaMask').click();
    cy.acceptMetamaskAccess();
  });

  it('contributes eth to a grant', () => {
    // TODO: This grant is already in the local db - it is NOT created
    // as part of the test process, creation of these types of entities
    // should be automated
    cy.visit('http://localhost:8000/grants/4/local-fund');

    cy.get('#CookielawBannerAccept').click();
    cy.contains('Add to Cart').click();

    cy.get('#select2-side-cart-currency-4-container').click();
    cy.get('input[role=searchbox]').type('ETH{enter}');
    cy.contains('CHECKOUT').click();

    cy.get('#gitcoin-grant-input-amount').type('{backspace}0');

    cy.contains('Standard Checkout').click();
    cy.confirmMetamaskTransaction();

    cy.get('body').should('contain.text', 'Thank you for contributing to open source!');
  });
});
