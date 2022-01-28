describe('Creating a new grant', { tags: ['grants-no-run'] }, () => {
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

  it('can navigate to the new grant screen', () => {
    cy.get('#dropdownProducts').trigger('mouseenter');
    cy.get('[data-submenu=products]').find('[data-submenu=grants]').click();

    cy.get('#grants-showcase').contains('Create a Grant').click();
    cy.url().should('contain', 'grants/new');
  });

  describe('creation:success - required fields only', () => {
    it('extracts the user\'s Twitter handle when the full Twitter URL is entered into the form', () => {
      const orgTwitterURL = 'https://twitter.com/gitcoin';
      const userTwitterURL = 'https://twitter.com/gitcoinbot';

      cy.visit('grants/new');

      cy.get('input[name=twitter_handle_1]').type(orgTwitterURL).blur();
      cy.get('input[name=twitter_handle_2]').type(userTwitterURL).blur();

      cy.get('input[name=twitter_handle_1]').should('have.value', '@gitcoin');
      cy.get('input[name=twitter_handle_2]').should('have.value', '@gitcoinbot');
    });

    it('submits a grant for review', () => {
      cy.visit('grants/new');

      cy.get('form').within(() => {
        cy.get('input[name=title]').type('Gitcoin Fund');
        cy.get('.quill-editor').type('We’re on a mission to build an internet that is open source, collaborative, and economically empowering.');
        cy.get('input[name=reference_url]').type('https://gitcoin.co');
        cy.get('input[name=twitter_handle_1]').type('@git');

        cy.get('input[placeholder="Select a blockchain to receive funding"]').type('eth').click();
        cy.contains('Ethereum').click();

        cy.get('input[name=eth_payout_address]').type('0xd08Fe0c97c80491C6ee696Ee8151bc6E57d1Bf1d');

        cy.get('input[placeholder="Has this project received external funding?"]').click();
        cy.contains('No, this project has not raised external funding.').click();


        cy.get('input[placeholder="Add tags to help others discover your grant"]').click();
        cy.contains('education').click();

        cy.contains('Create Grant').click();
      });

      cy.url().should('contain', 'gitcoin-fund');
    });
  });
});
