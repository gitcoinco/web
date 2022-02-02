// TODO: commented out tests require github login support

describe('Visit Tests', { tags: ['platform'] }, function() {
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
  it('Visits the Labs Page', function() {
    cy.visit('http://localhost:8000/explorer');
  });
  it('Visits the Mission Page', function() {
    cy.visit('http://localhost:8000/mission');
  });
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
