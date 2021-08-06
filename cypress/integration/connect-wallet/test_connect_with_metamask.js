describe('connect wallet: metamask', () => {
  before(() => {
    cy.setupMetamask();
    cy.changeMetamaskNetwork('Localhost 8545');
  });
  it('pulls address from metamask accounts', () => {
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

    cy.get('@wallet').click();
    cy.get('#wallet-btn').should('contain.text', 'Change Wallet');
  });
});
