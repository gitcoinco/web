describe('Products menu', () => {
  it('navigates to the grants explorer when \'Explore Grants\' is selected', () => {
    cy.impersonateUser();

    cy.get('#dropdownProducts').trigger('mouseenter');
    cy.contains('Grants Crowdfunding for Open Source').trigger('mouseenter');
    cy.contains('Explore Grants').click();

    cy.url().should('contain', 'grants/explorer');
  });
});
