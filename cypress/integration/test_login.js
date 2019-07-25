const _ = Cypress._;

describe('Login Tests', () => {

  /**
   * Defines a Cypress command that is able to navigate the different personas of the domain
   */
  Cypress.Commands.add('persona', (userType) => {
    userType = userType.toLowerCase();
    Cypress.log({
      name: `persona-${userType}`
    });
    //
    cy.get('body', {timeout: 10000}).contains('Are you a Funder or a Contributor?');

    cy.get(`button[data-persona="persona_is_${userType}"]`)
      .then($personaButton => {
        if ($personaButton.length) {
          cy.wrap($personaButton).click();

          if (userType === 'funder') {
            cy.get('#step-1').contains('Get Started with Gitcoin!');
            cy.get('#next-btn').click();
            cy.get('#next-btn').click();

            cy.get('#later-button').click();

            cy.get('body').should('contain', 'Funder Guide');
          } else {
            cy.get('#step-1').contains('Get Started with Gitcoin!');
            cy.get('#next-btn').click();
            cy.get('#next-btn').click();
            cy.get('#later-button').click();
            cy.get('#next-btn').click();
            cy.get('#next-btn').click();

            cy.wait(1000);
            // cy.get('#onboard-dashboard').contains('Welcome To Gitcoin'); // success condition hard to verify with hunter workflow
          }

        }
      });

  });

  /**
   * adds a generalized login call for the cypress engine to be able to login as either a funder or a hunter
   */
  Cypress.Commands.add('login', (userType, forcePersona = false) => {

    userType = userType.toUpperCase();
    Cypress.log({
      name: `login-${userType}`
    });

    // login and reqeust an authorization for the application
    const loginOptions = {
      method: 'PUT',
      url: `https://api.github.com/authorizations/clients/${Cypress.env('GITHUB_CLIENT_ID')}`,
      form: true, // we are submitting a regular form body
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Basic ${btoa(`${Cypress.env(userType)}:${Cypress.env(`${userType}_PASS`)}`)}`
      },
      body: JSON.stringify({
        'client_secret': Cypress.env('GITHUB_CLIENT_SECRET'),
        'scopes': [
          'read:user', 'user:email'
        ],
        'note': 'LocalGitcoinTesting'
      })
    };

    // allow us to override defaults with passed in overrides
    // _.extend(options.body, overrides)

    // cy.request(logoutOptions);
    cy.request(loginOptions);

    cy.visit(
      'http://localhost:8000/login/github/?next=/'
    )
      .then(() => {

        cy.get('body').then(($body) => {
          if ($body.find("input[name='login']").length) {
            cy.get("input[name='login']").type(Cypress.env(userType))
              .get("input[name='password']").type(Cypress.env(`${userType}_PASS`))
              .get("input[type='submit']").click();
          }
        }).wait(500);
        if (Cypress.env('NEW_USER') || forcePersona === true) {
          cy.persona(userType);
        } else {
          cy.get('body').should('contain', 'We Care About Your Privacy');
          cy.get('#notify_policy_update .modal-dialog button.button').click();
        }
      });


  });

  it('Login as a Funder', () => {
    const userType = 'hunter';
    // if a new user, set the NEW_USER env variable to test persona
    cy.login(userType);

  });

})
;
