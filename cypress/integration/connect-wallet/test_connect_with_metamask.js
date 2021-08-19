describe('connect wallet: metamask', () => {
  before(() => {
    cy.setupMetamask();
    cy.changeMetamaskNetwork('localhost');
  });

  after(() => {
    cy.disconnectWallet();
    cy.clearWindows();
  });

  it('pulls address from metamask accounts', () => {
    cy.impersonateUser();

    cy.get('#navbarDropdownWallet').as('wallet').click();
    cy.contains('Connect Wallet').click();
    cy.contains('MetaMask').click();

    cy.acceptMetamaskAccess();

    cy.get('@wallet').click();
    cy.get('#wallet-btn').should('contain.text', 'Change Wallet');
  });
});
