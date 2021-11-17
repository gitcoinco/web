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

        cy.get('.vs__dropdown-menu').should('contain', 'Discover');
        cy.get('.vs__dropdown-menu').should('contain', 'Weighted Shuffle');
        cy.get('.vs__dropdown-menu').should('contain', 'Trending');
        cy.get('.vs__dropdown-menu').should('contain', 'Undiscovered Gems');
        cy.get('.vs__dropdown-menu').should('contain', 'Recently Updated');
        cy.get('.vs__dropdown-menu').should('contain', 'Newest');
        cy.get('.vs__dropdown-menu').should('contain', 'Oldest');
        cy.get('.vs__dropdown-menu').should('contain', 'A to Z');
        cy.get('.vs__dropdown-menu').should('contain', 'Z to A');
        cy.get('.vs__dropdown-menu').should('contain', 'Current Round');
        cy.get('.vs__dropdown-menu').should('contain', 'Most Relevant');
        cy.get('.vs__dropdown-menu').should('contain', 'All-Time');
        cy.get('.vs__dropdown-menu').should('contain', 'Highest Amount Raised');
        cy.get('.vs__dropdown-menu').should('contain', 'Highest Contributor Count');

        cy.contains('Discover').parent().should('have.class', 'vs__dropdown-option--disabled');
        cy.contains('Current Round').parent().should('have.class', 'vs__dropdown-option--disabled');
        cy.contains('All-Time').parent().should('have.class', 'vs__dropdown-option--disabled');
       });
    });
  });
  