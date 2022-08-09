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

  it.skip('allows a user to add additional bounty owners', () => {
    cy.visit('bounty/new');
    cy.wait(1000);

    // TODO create a command out of this
    cy.get('#navbarDropdownWallet').click();
    cy.wait(1000);
    cy.get('#wallet-btn').click();

    // Screen 1
    cy.contains('Feature').click();

    let tags = [ 'Python', 'Lua', 'Web Assembly' ];

    tags.forEach(tag => {
      if (tag === 'Python') {
        cy.get('#bounty_tags').find('.vs__search').click();
        cy.contains(tag).click();
      } else {
        cy.get('#bounty_tags').find('.vs__search').type(tag + '{enter}');
      }
    });

    cy.get('#experience_level').find('.vs__search').click().type('Beginner{enter}');
    cy.get('#project_length').find('.vs__search').click().type('Hours{enter}');

    cy.contains('Next').click();

    // Screen 2
    cy.contains('Create Custom Bounty').click();
    let bountyTitle = 'My Custom Bounty Title';
    let bountyDescription = 'My Custom Bounty Description';

    cy.get('#new-bounty-custom-title').type(bountyTitle);
    cy.get('#new-bounty-custom-editor').type(bountyDescription);

    cy.get('#new-bounty-acceptace-criteria').type('Custom bounty acceptance criteria');
    cy.get('#new-bounty-resources').type('Custom bounty resource');
    cy.get('#new-bounty-organisation-url').type('https://github.com/gitcoinco/');

    let contactDiscord = '#myhandle289346';
    let contactTelegram = 'telegramUser';
    let contactEmail = 'contact@email.com';

    cy.get('.new-bounty-contact-details-form-0').find('.new-bounty-contact-type').find('.vs__search').click().type('Discord{enter}');
    cy.get('.new-bounty-contact-details-form-0').find('.new-bounty-contact-value').clear().type(contactDiscord);

    // Add another row
    cy.get('.new-bounty-contact-details-form-0').find('.new-bounty-btn-add-contact').click();
    cy.get('.new-bounty-contact-details-form-1').find('.new-bounty-contact-type').find('.vs__search').click().type('Telegram{enter}');
    cy.get('.new-bounty-contact-details-form-1').find('.new-bounty-contact-value').clear().type(contactTelegram);

    // Add another row
    cy.get('.new-bounty-contact-details-form-1').find('.new-bounty-btn-add-contact').click();
    cy.get('.new-bounty-contact-details-form-2').find('.new-bounty-contact-type').find('.vs__search').click().type('Mail{enter}');
    cy.get('.new-bounty-contact-details-form-2').find('.new-bounty-contact-value').clear().type(contactEmail);


    cy.contains('Next').click();

    // Screen 3
    // cy.get('#payout_token').should('be.disabled');    TODO: this check does not work
    cy.get('#usd_amount').should('be.disabled');
    cy.get('#amount').should('be.disabled');
    cy.get('#new_bounty_peg_to_usd').should('be.disabled');

    cy.get('#payout_chain').find('.vs__search').click().type('ETH{enter}');
    // cy.get('#payout_token').should('be.enabled');           TODO: this check does not work

    cy.get('#payout_token').find('.vs__search').click().type('ETH{enter}');

    cy.get('#usd_amount').should('be.enabled');
    cy.get('#new_bounty_peg_to_usd').should('be.enabled');

    let additionalBountyOwners = [ 'funder1', 'test1', 'test3' ];

    additionalBountyOwners.forEach(owner => {
      cy.get('#bounty_owner').find('.vs__search').click().type(owner);
      cy.wait(2000);
      cy.get('#bounty_owner').find('.vs__search').click().type('{enter}');
    });

    let usdAmount = '5.5';

    cy.get('#usd_amount').clear().type(usdAmount);

    cy.contains('Next').click();

    // Screen 4

    cy.contains('Standard').click();
    cy.contains('Approval Required').click();

    cy.contains('Next').click();

    // Screen 5

    tags.forEach(tag => {
      cy.contains(tag);
    });

    cy.get('#experience_level').contains('Beginner');
    cy.contains(bountyTitle).should('be.visible');
    cy.contains(bountyDescription).should('be.visible');

    // Save and navigate to the details screen
    cy.contains('Confirm').click();

    // Verify that the redirect happened
    cy.url().should('include', '/issue/');

    cy.get('#experience_level').contains('Beginner');

    cy.contains(contactDiscord).should('be.visible');
    cy.contains(contactTelegram).should('be.visible');
    cy.contains(contactEmail).should('be.visible');

    cy.contains(bountyTitle).should('be.visible');
    cy.contains(bountyDescription).should('be.visible');

    // Ensure proper information is displayed to the user about payment
    cy.get('#value_in_usdt').should('contain', usdAmount);

    additionalBountyOwners.forEach(owner => {
      cy.contains(owner);
    });

  });

});

