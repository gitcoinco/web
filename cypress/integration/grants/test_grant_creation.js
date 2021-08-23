describe('Creating a new grant', () => {
  before(() => {
    cy.setupMetamask();
  });
  after(() => {
    cy.clearWindows();
  });

  beforeEach(() => {
    cy.impersonateUser();
  });

  afterEach(() => {
    cy.logout();
  });

  it('can navigate to the new grant screen', () => {
    cy.get('#dropdownProducts').trigger('mouseenter');
    cy.get('[data-submenu=products]').find('[data-submenu=grants]').click();

    cy.get('#grants-showcase').contains('Create a Grant').click();
    cy.url().should('contain', 'grants/new');
  });

  describe('creation:success - required fields only', () => {
    it('submits a grant for review', () => {
      cy.visit('grants/new');

      cy.get('form').within(() => {
        cy.get('input[name=title]').type('Gitcoin Fund');
        cy.get('.quill-editor').type('We’re on a mission to build an internet that is open source, collaborative, and economically empowering.');
        cy.get('input[name=reference_url]').type('https://gitcoin.co');
        cy.get('input[name=twitter_handle_1]').type('@gitcoin');

        cy.contains('ETH').click();
        cy.get('input[name=eth_payout_address]').type('0xd08Fe0c97c80491C6ee696Ee8151bc6E57d1Bf1d');
        cy.get('input[placeholder="Yes/No"]').click();
        cy.contains('No, this project has not raised external funding.').click();

        cy.get('input[placeholder="Pick a category"]').click();
        cy.contains('Community').click();
        cy.get('input[placeholder="Select categories"]').click();
        cy.contains('subtype').click();

        cy.contains('Create Grant').click();
      });

      cy.url().should('contain', 'gitcoin-fund');
    });
  });
});
