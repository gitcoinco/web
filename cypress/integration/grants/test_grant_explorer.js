describe('Grants Explorer page', () => {
  before(() => {
    cy.setupMetamask();
  });
  
  beforeEach(() => {
    cy.acceptCookies();
  });

  afterEach(() => {
    cy.logout();
  });

  after(() => {
    cy.clearWindows();
  });

  describe('grants explorer sort menu', () => {
    it('contains the proper sort options', () => {
      cy.impersonateUser();

      cy.visit('grants/explorer');

      cy.get('.vselect-clean').click();

      cy.get('.vs__dropdown-menu')
        .should('contain', 'Discover')
        .should('contain', 'Current Round')
        .should('contain', 'All-Time')
        .should('contain', 'Weighted Shuffle')
        .should('contain', 'Trending')
        .should('contain', 'Undiscovered Gems')
        .should('contain', 'Recently Updated')
        .should('contain', 'Newest')
        .should('contain', 'Oldest')
        .should('contain', 'A to Z')
        .should('contain', 'Z to A')
        .should('contain', 'Highest Match Amount');

      cy.get('.vs__dropdown-menu li').filter(':contains("Highest Amount Raised")').should('have.length', 2);
      cy.get('.vs__dropdown-menu li').filter(':contains("Highest Contributor Count")').should('have.length', 2);
    });

    it('does not contain Most Relevant option by default', () => {
      cy.impersonateUser();

      cy.visit('grants/explorer');

      cy.get('.vselect-clean').click();
      cy.get('.vs__dropdown-menu').should('not.contain', 'Most Relevant');
    });

    it('contains Most Relevant option when user performs keyword search', () => {
      cy.impersonateUser();

      cy.visit('grants/explorer');

      cy.get('[placeholder="Search..."]').click().type('Test');

      cy.get('.vselect-clean').click();
      cy.get('.vs__dropdown-menu').should('contain', 'Most Relevant');
    });

    it('divides the sort options into category names with disabled labels', () => {
      cy.impersonateUser();

      cy.visit('grants/explorer');

      cy.get('.vselect-clean').click();

      cy.contains('Discover').parent().should('have.class', 'vs__dropdown-option--disabled');
      cy.contains('Current Round').parent().should('have.class', 'vs__dropdown-option--disabled');
      cy.contains('All-Time').parent().should('have.class', 'vs__dropdown-option--disabled');
    });

    it('does not display admin options when user is not staff', () => {
      cy.impersonateUser();

      cy.visit('grants/explorer');

      cy.get('.vselect-clean').click();

      cy.get('.vs__dropdown-menu')
        .should('not.contain', 'Misc')
        .should('not.contain', 'ADMIN: Risk Score')
        .should('not.contain', 'ADMIN: Sybil Score');
    });

    it('displays admin options when user is staff', () => {
      cy.impersonateStaffUser();

      cy.visit('grants/explorer');

      cy.get('.vselect-clean').click();

      cy.get('.vs__dropdown-menu')
        .should('contain', 'Misc')
        .should('contain', 'ADMIN: Risk Score')
        .should('contain', 'ADMIN: Sybil Score');
    });

    it('sends the proper sort request to the API', () => {
      cy.impersonateStaffUser();

      cy.visit('grants/explorer');

      cy.get('.vselect-clean').click();

      // Options in Discover category
      cy.get('.vs__dropdown-menu').contains('Weighted Shuffle').click();
      cy.url().should('contain', 'sort_option=weighted_shuffle');

      cy.get('.vselect-clean').click();

      cy.get('.vs__dropdown-menu').contains('Trending').click();
      cy.url().should('contain', 'sort_option=-metadata__upcoming');

      cy.get('.vselect-clean').click();

      cy.get('.vs__dropdown-menu').contains('Undiscovered Gems').click();
      cy.url().should('contain', 'sort_option=-metadata__gem');

      cy.get('.vselect-clean').click();

      cy.get('.vs__dropdown-menu').contains('Recently Updated').click();
      cy.url().should('contain', 'sort_option=-last_update');

      cy.get('.vselect-clean').click();

      cy.get('.vs__dropdown-menu').contains('Newest').click();
      cy.url().should('contain', 'sort_option=-created_on');

      cy.get('.vselect-clean').click();

      cy.get('.vs__dropdown-menu').contains('Oldest').click();
      cy.url().should('contain', 'sort_option=created_on');

      cy.get('.vselect-clean').click();

      cy.get('.vs__dropdown-menu').contains('A to Z').click();
      cy.url().should('contain', 'sort_option=title');

      cy.get('.vselect-clean').click();

      cy.get('.vs__dropdown-menu').contains('Z to A').click();
      cy.url().should('contain', 'sort_option=-title');

      // Options in Current Round category
      cy.get('.vselect-clean').click();

      cy.get('.vs__dropdown-menu').contains('Highest Match Amount').click();
      cy.url().should('contain', 'sort_option=-clr_prediction_curve__0__1');

      cy.get('.vselect-clean').click();

      cy.get('.vs__dropdown-menu').contains('Highest Amount Raised').click();
      cy.url().should('contain', 'sort_option=-amount_received_in_round');

      cy.get('.vselect-clean').click();

      cy.get('.vs__dropdown-menu').contains('Highest Contributor Count').click();
      cy.url().should('contain', 'sort_option=-positive_round_contributor_count');

      // Options in All-Time category
      cy.get('.vselect-clean').click();

      cy.get('.vs__dropdown-menu li').filter(':contains("Highest Amount Raised")').last().click();
      cy.url().should('contain', 'sort_option=-amount_received');

      cy.get('.vselect-clean').click();

      cy.get('.vs__dropdown-menu li').filter(':contains("Highest Contributor Count")').last().click();
      cy.url().should('contain', 'sort_option=-contributor_count');

      // Admin options
      cy.get('.vselect-clean').click();

      cy.get('.vs__dropdown-menu').contains('ADMIN: Risk Score').click();
      cy.url().should('contain', 'sort_option=-weighted_risk_score');

      cy.get('.vselect-clean').click();

      cy.get('.vs__dropdown-menu').contains('ADMIN: Sybil Score').click();
      cy.url().should('contain', 'sort_option=-sybil_score');
    });
  });

  describe('grants explorer filters', () => {
    it('contains the proper filter options', () => {
      cy.createActiveGrantRound();

      cy.impersonateUser();

      cy.visit('grants/explorer');

      cy.contains('Grant Round').click();

      cy.get('.dropdown-menu').should('contain', 'Test Grant CLR');
    });
  });

  describe('selecting a grant', () => {
    it('opens the grant in a new browser tab', () => {
      cy.createGrantSubmission().then((response) => {
        const grantUrl = response.body.url;

        cy.approveGrant(grantUrl);
        cy.impersonateUser();

        cy.visit('grants/explorer');

        cy.contains('Test Grant Submission')
          .should('have.attr', 'target', '_blank')
          .should('have.attr', 'rel', 'noopener noreferrer')
          .then(link => {
            cy.request(link.prop('href')).its('status').should('eq', 200);
          });
      });
    });
  });
});
