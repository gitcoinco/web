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

    let tags = [ 'Python', 'Lua', 'Web Assembly' ];

    tags.forEach(tag => {
      if (tag === 'Python') {
        cy.contains(tag).click();
      } else {
        cy.get('#bounty_tags').find('.vs__search').type(tag + '{enter}');
      }
    });
    cy.get('#bounty_tags').find('.vs__search').click();

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
    // cy.get('#payout_token').should('be.disabled');    TODO: this check does not work
    cy.get('#usd_amount').should('be.disabled');
    cy.get('#amount').should('be.disabled');
    cy.get('#new_bounty_peg_to_usd').should('be.disabled');
    cy.get('#bounty_owner').should('be.enabled');

    cy.get('#payout_chain').find('.vs__search').click().type('ETH{enter}');
    // cy.get('#payout_token').should('be.enabled');           TODO: this check does not work

    cy.get('#payout_token').find('.vs__search').click().type('ETH{enter}');

    cy.get('#usd_amount').should('be.enabled');
    cy.get('#usd_amount').should('be.enabled');
    cy.get('#new_bounty_peg_to_usd').should('be.enabled');

    cy.get('#usd_amount').clear().type('123.34');

    cy.contains('Next').click();

    // Screen 4

    cy.contains('Standard').click();
    cy.contains('Approval Required').click();

    cy.contains('Next').click();

    // Screen 5

    tags.forEach(tag => {
      cy.contains(tag);
    });

    // cy.contains('Time Left').parent().contains();
    cy.log('Opened', cy.contains('Opened'));
    cy.log('Opened', cy.contains('Opened').parent());
    // cy.log('Opened', cy.contains('Opened').parent().contains('Few Seconds Ago'));
    // cy.contains('Opened').parent().contains('Few Seconds Ago');
    // cy.get('#bounty_type').contains('Improvement');
    // cy.get('#admin_override_suspend_auto_approval').contains('Off');
    // cy.contains('Project Type').parent().contains('Traditional');
    // cy.contains('Time Commitment').parent().contains('Days');
    cy.get('#experience_level').contains('Beginner');
    // cy.contains('Permission').parent().contains('Approval');


    // Save and navigate to the details screen
    cy.contains('Confirm').click();


    // Verify that the redirect happened
    cy.url().should('include', '/issue/');

    // cy.contains('Time Left').parent().contains();
    cy.log('Opened', cy.contains('Opened'));
    cy.log('Opened', cy.contains('Opened').parent());
    // cy.log('Opened', cy.contains('Opened').parent().contains('Few Seconds Ago'));
    // cy.contains('Opened').parent().contains('Few Seconds Ago');
    // cy.get('#bounty_type').contains('Improvement');
    // cy.get('#admin_override_suspend_auto_approval').contains('Off');
    // cy.contains('Project Type').parent().contains('Traditional');
    // cy.contains('Time Commitment').parent().contains('Days');
    cy.get('#experience_level').contains('Beginner');
    // cy.contains('Permission').parent().contains('Approval');
  });


  describe('Verify bounty field validation', () => {
    /*
 * Screen 1
 */

    it('Should validated the mandatory fields on screen 1 ', () => {
      cy.visit('bounty/new');
      cy.wait(1000);

      // Screen 1
      cy.contains('Next').click();

      cy.contains('Select at least one category').should('be.visible');
      cy.contains('Please select the bounty type').should('be.visible');
      cy.contains('Please select the experience level').should('be.visible');
      cy.contains('Please select the project length').should('be.visible');

    });

    /*
 * Screen 2 - Initial
 */

    it('Should validated that bounty information source was selected on screen 2 ', () => {
      cy.visit('bounty/new');
      cy.wait(1000);

      // Screen 1
      cy.contains('Feature').click();
      cy.get('#bounty_tags').find('.vs__search').click();

      let tags = [ 'Python', 'Lua', 'Web Assembly' ];

      tags.forEach(tag => {
        if (tag === 'Python') {
          cy.contains(tag).click();
        } else {
          cy.get('#bounty_tags').find('.vs__search').type(tag + '{enter}');
        }
      });
      cy.get('#bounty_tags').find('.vs__search').click();

      cy.get('#experience_level').find('.vs__search').click();
      cy.contains('Beginner').click();
      cy.get('#project_length').find('.vs__search').click();
      cy.contains('Hours').click();

      cy.contains('Next').click();


      // Screen 2
      cy.contains('Next').click();

      cy.contains('Select the bounty information source').should('be.visible');
    });

    /*
     * Screen 2 - GitHub Issue
     */
    it('Should validated that bounty github details are loaded on screen 2 ', () => {
      cy.visit('bounty/new');
      cy.wait(1000);

      // Screen 1
      cy.contains('Feature').click();
      cy.get('#bounty_tags').find('.vs__search').click();

      let tags = [ 'Python', 'Lua', 'Web Assembly' ];

      tags.forEach(tag => {
        if (tag === 'Python') {
          cy.contains(tag).click();
        } else {
          cy.get('#bounty_tags').find('.vs__search').type(tag + '{enter}');
        }
      });
      cy.get('#bounty_tags').find('.vs__search').click();

      cy.get('#experience_level').find('.vs__search').click();
      cy.contains('Beginner').click();
      cy.get('#project_length').find('.vs__search').click();
      cy.contains('Hours').click();

      cy.contains('Next').click();

      // Screen 2
      cy.contains('Import from GitHub').click();
      cy.contains('Next').click();

      cy.contains('Please input a GitHub issue').should('be.visible');

    });

    /*
     * Screen 2 - Custom Issue
     */
    it('Should validated that bounty title and description for custom bounties mandatory on screen 2 ', () => {
      cy.visit('bounty/new');
      cy.wait(1000);

      // Screen 1
      cy.contains('Feature').click();
      cy.get('#bounty_tags').find('.vs__search').click();

      let tags = [ 'Python', 'Lua', 'Web Assembly' ];

      tags.forEach(tag => {
        if (tag === 'Python') {
          cy.contains(tag).click();
        } else {
          cy.get('#bounty_tags').find('.vs__search').type(tag + '{enter}');
        }
      });
      cy.get('#bounty_tags').find('.vs__search').click();

      cy.get('#experience_level').find('.vs__search').click();
      cy.contains('Beginner').click();
      cy.get('#project_length').find('.vs__search').click();
      cy.contains('Hours').click();

      cy.contains('Next').click();

      // Screen 2
      cy.contains('Create Custom Bounty').click();
      cy.contains('Next').click();

      cy.contains('Please input bounty title').should('be.visible');
      cy.contains('Please input bounty description').should('be.visible');
    });


    /*
     * Screen 3
     */
    it('Should validated screen 3 ', () => {
      cy.visit('bounty/new');
      cy.wait(1000);

      // Screen 1
      cy.contains('Feature').click();
      cy.get('#bounty_tags').find('.vs__search').click();

      let tags = [ 'Python', 'Lua', 'Web Assembly' ];

      tags.forEach(tag => {
        if (tag === 'Python') {
          cy.contains(tag).click();
        } else {
          cy.get('#bounty_tags').find('.vs__search').type(tag + '{enter}');
        }
      });
      cy.get('#bounty_tags').find('.vs__search').click();

      cy.get('#experience_level').find('.vs__search').click();
      cy.contains('Beginner').click();
      cy.get('#project_length').find('.vs__search').click();
      cy.contains('Hours').click();

      cy.contains('Next').click();

      // Screen 2
      cy.contains('Create Custom Bounty').click();

      cy.get('#new-bounty-custom-title').type('My Custom Bounty');
      cy.get('#new-bounty-custom-editor').type('My custom bounty long long long description');

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
      cy.contains('Please select a chain').should('be.visible');
    });

    /*
    * Screen 4
    */
    it('Should validated screen 4 ', () => {
      cy.visit('bounty/new');
      cy.wait(1000);

      // Screen 1
      cy.contains('Feature').click();
      cy.get('#bounty_tags').find('.vs__search').click();

      let tags = [ 'Python', 'Lua', 'Web Assembly' ];

      tags.forEach(tag => {
        if (tag === 'Python') {
          cy.contains(tag).click();
        } else {
          cy.get('#bounty_tags').find('.vs__search').type(tag + '{enter}');
        }
      });
      cy.get('#bounty_tags').find('.vs__search').click();

      cy.get('#experience_level').find('.vs__search').click();
      cy.contains('Beginner').click();
      cy.get('#project_length').find('.vs__search').click();
      cy.contains('Hours').click();

      cy.contains('Next').click();

      // Screen 2
      cy.contains('Create Custom Bounty').click();

      cy.get('#new-bounty-custom-title').type('My Custom Bounty');
      cy.get('#new-bounty-custom-editor').type('My custom bounty long long long description');

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
      cy.get('#usd_amount').should('be.disabled');
      cy.get('#amount').should('be.disabled');
      cy.get('#new_bounty_peg_to_usd').should('be.disabled');
      cy.get('#bounty_owner').should('be.enabled');

      cy.get('#payout_chain').find('.vs__search').click().type('BTC{enter}');

      // cy.get('#payout_token').find('.vs__search').click().type('ETH{enter}');

      cy.get('#usd_amount').should('be.enabled');
      cy.get('#usd_amount').should('be.enabled');
      cy.get('#new_bounty_peg_to_usd').should('be.enabled');

      cy.get('#usd_amount').clear().type('123.34');

      cy.contains('Next').click();

      // Screen 4
      cy.contains('Next').click();
      cy.contains('Select the project type').should('be.visible');
      cy.contains('Select the permission type').should('be.visible');
    });

  });

});

