// TODO: commented out tests require github login support

describe('Visit Tests', function() {
  it('Visits the Explorer', function() {
    cy.visit('http://localhost:8000/explorer');
  });
  it('Visits the Grants Page', function() {
    cy.visit('http://localhost:8000/grants');
  });
  it('Visits the Landing Page', function() {
    cy.visit('http://localhost:8000/');
  });
  it('Visits the Kudos Page', function() {
    cy.visit('http://localhost:8000/kudos');
  });
  it('Visits the Kudos Marketplace', function() {
    cy.visit('http://localhost:8000/kudos/marketplace');
  });
  /*
  it('Visits the Kudos Sender', function() {
    cy.visit('http://localhost:8000/kudos/send');
    cy.url().should('contain', 'github.com');
  });
  */
  it('Visits the Labs Page', function() {
    cy.visit('http://localhost:8000/explorer');
  });
  it('Visits the About Page', function() {
    cy.visit('http://localhost:8000/about');
  });
  it('Visits the Mission Page', function() {
    cy.visit('http://localhost:8000/mission');
  });
  /*
  it('Visits the Results Page', function() {
    cy.visit('http://localhost:8000/results');
  });
  */
  it('Visits the Activity Page', function() {
    cy.visit('http://localhost:8000/activity');
  });
  it('Visits the Help Page', function() {
    cy.visit('http://localhost:8000/help');
  });
  it('Visits the Terms of Service Page', function() {
    cy.visit('http://localhost:8000/legal/terms');
  });
  it('Visits the Privacy Page', function() {
    cy.visit('http://localhost:8000/legal/privacy');
  });
});
