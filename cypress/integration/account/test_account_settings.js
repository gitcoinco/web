describe('Account settings', () => {
  before(() => {
    cy.setupWallet();
  });
  
  beforeEach(() => {
    cy.impersonateUser();
  });
  
  afterEach(() => {
    cy.logout();
  });
  
  it('can navigate to the account settings menu', () => {
    cy.get('#dropdownProfile').trigger('mouseenter');
    cy.contains('My Account').click();
    cy.get('.gc-profile-submenu').contains('Settings').click();
  
    cy.url().should('contain', 'settings/email');
  });
});
  