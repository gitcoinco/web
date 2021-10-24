describe('Creating a new bounty', () => {
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

  it('can navigate to the create bounty screen', () => {
    cy.get('#dropdownProfile').trigger('mouseenter');
    cy.get('.gc-profile-submenu').contains('Create a Bounty').click();

    cy.url().should('contain', 'bounty/new');
  });

  it('can create a new bounty', () => {
    cy.visit('bounty/new');

    cy.contains('I agree').click();

    cy.wait(1000);
    cy.get('button.btn-primary[data-dismiss]').scrollIntoView().click();

    cy.contains('ETH').click();
    cy.contains('MetaMask').click();
    cy.acceptMetamaskAccess();

    cy.get('#issueURL').type('https://github.com/gitcoinco/web/issues/1');

    cy.contains('Front End').click();
    cy.contains('Traditional').click();

    cy.contains('Approval Required').click();

    cy.get('#experience_level').find('.vs__search').click();
    cy.contains('Beginner').click();
    cy.get('#project_length').find('.vs__search').click();
    cy.contains('Hours').click();
    cy.get('#bounty_type').find('.vs__search').click();
    cy.contains('Bug').click();

    cy.get('#terms').check();
    cy.get('#termsPrivacy').check();

    cy.get('Button').contains('Fund Issue').click();

    cy.disconnectMetamaskWallet();
  });
});
