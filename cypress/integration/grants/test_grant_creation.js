describe('Creating a new grant', () => {
  it('can navigate to the new grant screen', () => {
    cy.visit('http://localhost:8000');

    cy.get('#dropdownProducts').trigger('mouseenter');
    cy.get('[data-submenu=grants]').click();
    cy.url().should('eq', 'http://localhost:8000/grants/');

    cy.visit('http://localhost:8000/grants/');

    cy.contains('Create a Grant').click();
    cy.url().should('eq', 'http://localhost:8000/grants/new');
  });
});
