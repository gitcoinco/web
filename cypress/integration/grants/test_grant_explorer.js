describe('Grants Explorer page', () => {
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
  
  describe('grants explorer sort menu', () => {
    it('contains the proper sort options', () => {
      cy.visit('grants/explorer');
  
      cy.get('.vselect-clean').click();

      cy.get('.vs__dropdown-menu')
        .should('contain', 'Discover')
        .should('contain', 'Weighted Shuffle')
        .should('contain', 'Trending')
        .should('contain', 'Undiscovered Gems')
        .should('contain', 'Recently Updated')
        .should('contain', 'Newest')
        .should('contain', 'Oldest')
        .should('contain', 'A to Z')
        .should('contain', 'Z to A')
        .should('contain', 'Current Round')
        .should('contain', 'Most Relevant')
        .should('contain', 'All-Time')
        .should('contain', 'Highest Amount Raised')
        .should('contain', 'Highest Contributor Count')
        .should('not.contain', 'Misc')
        .should('not.contain', 'ADMIN: Risk Score')
        .should('not.contain', 'ADMIN: Sybil Score');
        
      cy.contains('Discover').parent().should('have.class', 'vs__dropdown-option--disabled');
      cy.contains('Current Round').parent().should('have.class', 'vs__dropdown-option--disabled');
      cy.contains('All-Time').parent().should('have.class', 'vs__dropdown-option--disabled');
    });
  });
});
  