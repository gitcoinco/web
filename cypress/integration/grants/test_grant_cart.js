describe('Grant cart', () => {
  before(() => {
    cy.setupMetamask();
  });

  afterEach(() => {
    cy.disconnectMetamaskWallet();
    cy.logout();
  });

  after(() => {
    cy.clearWindows();
  });

  it('defaults donation amount to 25 DAI', () => {
    cy.createGrantSubmission().then((response) => {
      const grantUrl = response.body.url;

      cy.approveGrant(grantUrl);
      cy.impersonateUser();

      cy.visit(grantUrl);

      cy.get('.grant-checkout').contains('Add to Cart').click();
      cy.wait(1000); // slow the test down to allow cart data to load

      cy.get('#gc-cart').click();
      cy.contains('Checkout').click();

      cy.contains('MetaMask').click();
      cy.acceptMetamaskAccess();

      cy.get('[placeholder="Amount"]').should('have.value', '25') // assert donation input field has default value of 25 DAI
    });
  });
});