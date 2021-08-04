describe('Creating a new grant', () => {
  it('can navigate to the new grant screen', () => {
    cy.visit('http://localhost:8000/_administrationlogin');
    cy.get('[name=username]').type('root');
    cy.get('[name=password]').type('gitcoinco');
    cy.contains('Log in').click();

    cy.contains('Impersonate Users').click();

    cy.contains('test3').click();

    cy.get('#dropdownProducts').trigger('mouseenter');
    cy.get('[data-submenu=products]').find('[data-submenu=grants]').click();
    cy.url().should('eq', 'http://localhost:8000/grants/');

    cy.get('#grants-showcase').contains('Create a Grant').click();
    cy.url().should('eq', 'http://localhost:8000/grants/new');
  });
});
