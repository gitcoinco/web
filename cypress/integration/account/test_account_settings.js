describe('Account settings', () => {
    before(() => {
      cy.setupMetamask();
    });
  
    beforeEach(() => {
      cy.impersonateUser();
    });
  
    afterEach(() => {
      cy.logout();
    });
  
    after(() => {
      cy.clearWindows();
    });
  
    it('can navigate to the account settings menu', () => {
      cy.get('#dropdownProfile').trigger('mouseenter');
      cy.get('.gc-profile-submenu').contains('Settings').click();
  
      cy.url().should('contain', 'settings/email');
    });
  });
  