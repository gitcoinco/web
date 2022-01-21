describe('contributing to grant', () => {
  // before(() => {
  // });

  beforeEach(() => {
    cy.setupWallet();
    cy.acceptCookies();
  });

  afterEach(() => {
    cy.logout();
  });

  // after(() => {
  // });

  it('contributes eth to a single grant', () => {
    cy.createGrantSubmission().then((response) => {
      const grantUrl = response.body.url;

      cy.approveGrant(grantUrl);
      cy.impersonateUser();

      cy.visit(grantUrl);

      cy.get('.grant-checkout').contains('Add to Cart').click();
      cy.wait(1000); // slow the test down to allow cart data to load

      cy.get('#gc-cart').click();
      cy.contains('Checkout').click();

      cy.get('#vs3__combobox').click().type('ETH{enter}');
      cy.get('#gitcoin-grant-input-amount').type('{backspace}');
      cy.contains("I'm Ready to Checkout").scrollIntoView().click();
      cy.get('#js-fundGrants-button').click();

      cy.get('body', {timeout: 10000}).should('contain.text', 'Thank you for contributing to open source!');
    });
  });

  it('contributes eth to multiple grants', () => {
    cy.createGrantSubmission().then((response) => {
      const grantUrl = response.body.url;

      cy.wrap(grantUrl).as('grant1');

      cy.approveGrant(grantUrl);
    });

    cy.createGrantSubmission().then((response) => {
      const grantUrl = response.body.url;

      cy.wrap(grantUrl).as('grant2');

      cy.approveGrant(grantUrl);
    });

    cy.impersonateUser();

    cy.get('@grant1').then((grantUrl) => {
      cy.visit(grantUrl);
      cy.get('.grant-checkout').contains('Add to Cart').click();
    });

    cy.get('@grant2').then((grantUrl) => {
      cy.visit(grantUrl);
      cy.get('.grant-checkout').contains('Add to Cart').click();
    });

    cy.visit('grants/cart?');

    cy.get('#vs3__combobox').click().type('ETH{enter}');
    cy.get('#gitcoin-grant-input-amount').type('{backspace}');
    cy.contains("I'm Ready to Checkout").scrollIntoView().click();
    cy.get('#js-fundGrants-button').click();

    cy.get('body', {timeout: 10000}).should('contain.text', 'Thank you for contributing to open source!');
  });

  it('defaults donation amount to 25 DAI in the cart', () => {
    cy.createGrantSubmission().then((response) => {
      const grantUrl = response.body.url;

      cy.approveGrant(grantUrl);
      cy.impersonateUser();

      cy.visit(grantUrl);

      cy.get('.grant-checkout').contains('Add to Cart').click();
      cy.wait(1000); // slow the test down to allow cart data to load

      cy.get('#gc-cart').click();
      cy.contains('Checkout').click();

      cy.get('[placeholder="Amount"]').should('have.value', '25'); // assert donation input field has default value of 25 DAI
    });
  });
});
