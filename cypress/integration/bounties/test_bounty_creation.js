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

    // {force: true} is being used here as a last resort
    // because access to the element it needs to click is blocked
    // by a container. It is not a best practice and should be used sparingly.
    // Anyone considering basing future tests off of this code is encouraged to
    // seek out better ways to interact with the UI.
    cy.contains("Ok, I'm ready").click({ force: true });

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