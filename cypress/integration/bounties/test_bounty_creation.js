describe('Creating a new bounty', { tags: ['bounties'] }, () => {

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

  it('can navigate to the create bounty screen', () => {
    cy.get('#dropdownProfile').trigger('mouseenter');
    cy.get('.gc-profile-submenu').contains('Create a Bounty').click();

    cy.url().should('contain', 'bounty/new');
  });

  it('can create a new bounty', () => {
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
    cy.contains('Feature').click();
    cy.get('#bounty_tags').find('.vs__search').click();
    cy.contains('Python').click();
    cy.get('#experience_level').find('.vs__search').click();
    cy.contains('Beginner').click();
    cy.get('#project_length').find('.vs__search').click();
    cy.contains('Hours').click();

    cy.contains('Next').click();

    // Screen 2
    cy.contains('Import from GitHub').click();
    cy.get('#new-bounty-issue-url').type('https://github.com/gitcoinco/web/issues/1');
    cy.get('#new-bounty-acceptace-criteria').type('Custom bounty acceptance criteria');
    cy.get('#new-bounty-resources').type('Custom bounty resource');
    cy.get('#new-bounty-organisation-url').type('https://github.com/gitcoinco/');

    cy.get('.new-bounty-contact-details-form-0').find('.new-bounty-contact-type').find('.vs__search').click().type('Discord{enter}');
    cy.get('.new-bounty-contact-details-form-0').find('.new-bounty-contact-value').clear().type('#myhandle289346');

    // Add another row
    cy.get('.new-bounty-contact-details-form-0').find('.new-bounty-btn-add-contact').click();
    cy.get('.new-bounty-contact-details-form-1').find('.new-bounty-contact-type').find('.vs__search').click().type('Telegram{enter}');
    cy.get('.new-bounty-contact-details-form-1').find('.new-bounty-contact-value').clear().type('telegram-user');

    // Add another row
    cy.get('.new-bounty-contact-details-form-1').find('.new-bounty-btn-add-contact').click();
    cy.get('.new-bounty-contact-details-form-2').find('.new-bounty-contact-type').find('.vs__search').click().type('Mail{enter}');
    cy.get('.new-bounty-contact-details-form-2').find('.new-bounty-contact-value').clear().type('my.demo.name@email.com');


    cy.contains('Next').click();

    // Screen 3

    cy.contains('Next').click();
    
    // Screen 4

    cy.contains('Next').click();
    
    // Screen 5

    cy.contains('Confirm').click();

    // cy.contains('ETH').click();

    // cy.get('#issueURL').type('https://github.com/gitcoinco/web/issues/1');

    // cy.contains('Front End').click();
    // cy.contains('Traditional').click();

    // cy.contains('Approval Required').click();

    // cy.get('#experience_level').find('.vs__search').click();
    // cy.contains('Beginner').click();
    // cy.get('#project_length').find('.vs__search').click();
    // cy.contains('Hours').click();
    // cy.get('#bounty_type').find('.vs__search').click();
    // cy.contains('Bug').click();

    // cy.get('#terms').check();
    // cy.get('#termsPrivacy').check();

    // cy.get('Button').contains('Fund Issue').click();

  });
});

