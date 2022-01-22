describe.skip('Products menu', () => {
  // before(() => {
  // });

  beforeEach(() => {
    cy.acceptCookies();
    cy.impersonateUser();
  });

  afterEach(() => {
    cy.logout();
  });

  // after(() => {
  // });

  it('navigates to the grants explorer when \'Explore Grants\' is selected', () => {
    cy.get('#dropdownProducts').trigger('mouseenter');
    cy.contains('Grants Crowdfunding for Open Source').trigger('mouseenter');
    cy.contains('Explore Grants').click();

    cy.url().should('contain', 'grants/explorer');
  });
});
