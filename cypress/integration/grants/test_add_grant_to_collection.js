describe('add grants to a collection', () => {
  before(() => {
    cy.setupMetamask();
    cy.createGrantSubmission().then((response) => {
      cy.approveGrant(response.body.url);
    });
  });

  after(() => {
    cy.clearWindows();
  });

  it('adding from the explore page', () => {
    cy.impersonateUser();

    cy.visit('grants/explore');

    cy.logout();
  });
});
