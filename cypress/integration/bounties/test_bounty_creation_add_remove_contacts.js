describe('Creating adding & removing contacts in new bounty', { tags: ['bounties'] }, () => {

  beforeEach(() => {
    cy.setupWallet();
    cy.acceptCookies();
    cy.impersonateUser();
    cy.window().then((win) => {
      win.localStorage.setItem('quickstart_dontshow', true);
    });
  });

  afterEach(() => {
    cy.logout();
  });


  it('can add and remove contacts in new bounty', () => {
    cy.visit('bounty/new');

    // unfortunately some of the events do not seem bound in time for this
    // to run without any errors. adding in this manual wait is not advised
    // and is used here to slow the tests down to allow the modal close click
    // events to bind properly
    // in addition to the wait, we are using the force options on the click,
    // if there is an alternative means for clicking on buttons, please use those
    // instead of jumping to force. force may click on items hidden by other elements
    // and is not how a user would interact with the application. we should make every
    // attempt to use the UI as a real user would.
    cy.wait(1000);

    // Screen 1
    cy.contains('Next').click();

    // Screen 2
    cy.contains('Import from GitHub').click();

    cy.get('.new-bounty-contact-details-form-0').find('.new-bounty-contact-type').find('.vs__search').click().type('Discord{enter}');
    cy.get('.new-bounty-contact-details-form-0').find('.new-bounty-contact-value').clear().type('#myhandle289346');

    // Add another row
    cy.get('.new-bounty-contact-details-form-0').find('.new-bounty-btn-add-contact').click();
    cy.get('.new-bounty-contact-details-form-1').find('.new-bounty-contact-type').find('.vs__search').click().type('Telegram{enter}');
    cy.get('.new-bounty-contact-details-form-1').find('.new-bounty-contact-value').clear().type('telegram-user');

    // Check that add only exists on last row
    cy.get('.new-bounty-contact-details-form-0').find('.new-bounty-btn-add-contact').should('not.be.visible');
    cy.get('.new-bounty-contact-details-form-1').find('.new-bounty-btn-add-contact').should('be.visible');

    // Add another row
    cy.get('.new-bounty-contact-details-form-1').find('.new-bounty-btn-add-contact').click();
    cy.get('.new-bounty-contact-details-form-2').find('.new-bounty-contact-type').find('.vs__search').click().type('Mail{enter}');
    cy.get('.new-bounty-contact-details-form-2').find('.new-bounty-contact-value').clear().type('my.demo.name@email.com');

    // Check that add only exists on last row
    cy.get('.new-bounty-contact-details-form-0').find('.new-bounty-btn-add-contact').should('not.be.visible');
    cy.get('.new-bounty-contact-details-form-1').find('.new-bounty-btn-add-contact').should('not.be.visible');
    cy.get('.new-bounty-contact-details-form-2').find('.new-bounty-btn-add-contact').should('be.visible');

    // Add another row
    cy.get('.new-bounty-contact-details-form-2').find('.new-bounty-btn-add-contact').click();
    cy.get('.new-bounty-contact-details-form-3').find('.new-bounty-contact-type').find('.vs__search').click().type('Mail{enter}');
    cy.get('.new-bounty-contact-details-form-3').find('.new-bounty-contact-value').clear().type('my.demo.name@email.com');

    // Check that add only exists on last row
    cy.get('.new-bounty-contact-details-form-0').find('.new-bounty-btn-add-contact').should('not.be.visible');
    cy.get('.new-bounty-contact-details-form-1').find('.new-bounty-btn-add-contact').should('not.be.visible');
    cy.get('.new-bounty-contact-details-form-2').find('.new-bounty-btn-add-contact').should('not.be.visible');
    cy.get('.new-bounty-contact-details-form-3').find('.new-bounty-btn-add-contact').should('be.visible');
    
    // Add another row
    cy.get('.new-bounty-contact-details-form-3').find('.new-bounty-btn-add-contact').click();
    cy.get('.new-bounty-contact-details-form-4').find('.new-bounty-contact-type').find('.vs__search').click().type('Mail{enter}');
    cy.get('.new-bounty-contact-details-form-4').find('.new-bounty-contact-value').clear().type('my.demo.name@email.com');
    
    // Check that add only exists on last row
    cy.get('.new-bounty-contact-details-form-0').find('.new-bounty-btn-add-contact').should('not.be.visible');
    cy.get('.new-bounty-contact-details-form-1').find('.new-bounty-btn-add-contact').should('not.be.visible');
    cy.get('.new-bounty-contact-details-form-2').find('.new-bounty-btn-add-contact').should('not.be.visible');
    cy.get('.new-bounty-contact-details-form-3').find('.new-bounty-btn-add-contact').should('not.be.visible');
    cy.get('.new-bounty-contact-details-form-4').find('.new-bounty-btn-add-contact').should('be.visible');

    // Delete row
    cy.get('.new-bounty-contact-details-form-0').find('.new-bounty-btn-delete-contact').click();
    cy.get('.new-bounty-contact-details-form-4').should('not.exist');
    
    // Delete row
    cy.get('.new-bounty-contact-details-form-3').find('.new-bounty-btn-delete-contact').click();
    cy.get('.new-bounty-contact-details-form-3').should('not.exist');

    // Delete row
    cy.get('.new-bounty-contact-details-form-1').find('.new-bounty-btn-delete-contact').click();
    cy.get('.new-bounty-contact-details-form-2').should('not.exist');
  });
});

