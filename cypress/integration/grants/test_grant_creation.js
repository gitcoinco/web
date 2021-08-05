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

  describe('creation:success', () => {
    it('submits a grant for review', () => {
      cy.visit('http://localhost:8000/_administrationlogin');

      cy.get('[name=username]').type('root');
      cy.get('[name=password]').type('gitcoinco');
      cy.contains('Log in').click();

      cy.contains('Impersonate Users').click();
      cy.contains('test3').click();

      cy.visit('http://localhost:8000/grants/new');

      cy.get('input[name=title]').type('Gitcoin Fund');
      cy.get('.quill-editor').type('We’re on a mission to build an internet that is open source, collaborative, and economically empowering.');
      cy.get('input[name=reference_url').type('https://gitcoin.co');
      cy.get('input[name=twitter_handle_1').type('@gitcoin');
      cy.contains('ETH').click();
      cy.get('input[name=eth_payout_address]').type('0xd08Fe0c97c80491C6ee696Ee8151bc6E57d1Bf1d');
      cy.contains('Yes/No').click();
      cy.contains('No, this project has not raised external funding.').click();
      cy.contains('Pick a category').click();
      cy.contains('Community').click();
      cy.contains('Select categories');
      cy.contains('subtype').click();
      cy.contains('Create Grant').click();

      cy.url().should('contain', 'gitcoin-fund');
    });
  });
});
