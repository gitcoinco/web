// ***********************************************
// This example commands.js shows you how to
// create various custom commands and overwrite
// existing commands.
//
// For more comprehensive examples of custom
// commands please read more here:
// https://on.cypress.io/custom-commands
// ***********************************************
//
//
// -- This is a parent command --
// Cypress.Commands.add("login", (email, password) => { ... })
//
//
// -- This is a child command --
// Cypress.Commands.add("drag", { prevSubject: 'element'}, (subject, options) => { ... })
//
//
// -- This is a dual command --
// Cypress.Commands.add("dismiss", { prevSubject: 'optional'}, (subject, options) => { ... })
//
//
// -- This is will overwrite an existing command --
// Cypress.Commands.overwrite("visit", (originalFn, url, options) => { ... })

// authentication
Cypress.Commands.add('loginRootUser', () => {
  const url = '_administrationlogin/';

  cy.request({url, method: 'GET', log: true}).then((response) => {
    const body = Cypress.$(response.body);
    const csrfmiddlewaretoken = body.find('input[name=csrfmiddlewaretoken]').val();

    cy.request({
      url,
      method: 'POST',
      body: {
        csrfmiddlewaretoken,
        username: 'root',
        password: 'gitcoinco'
      },
      form: true
    });
  });
});

Cypress.Commands.add('impersonateUser', () => {
  cy.loginRootUser();
  cy.visit('impersonate/4/');
});

Cypress.Commands.add('logout', () => {
  cy.request('logout/?next=/');
});

// grants
Cypress.Commands.add('createGrantSubmission', (options = {}) => {
  cy.logout();
  cy.impersonateUser();

  const url = 'grants/new/';

  return cy.request(url)
    .then((response) => {
      const body = Cypress.$(response.body);
      const csrfmiddlewaretoken = body.find('input[name=csrfmiddlewaretoken]').val();

      return cy.request({
        url,
        method: 'POST',
        body: {
          csrfmiddlewaretoken,
          grant_type: options.grant_type || 'media',
          title: options.title || 'Test Grant Submission',
          description: options.description || 'Describing grant submission',
          description_rich: options.description_rich || "{'ops':[{'insert':'The mission of the grant is to...},{'insert':'\n'}]}'",
          has_external_funding: options.has_exeternal_funding || 'no',
          eth_payout_address: options.eth_payout_address || '0xB81C935D01e734b3D8bb233F5c4E1D72DBC30f6c',
          handle1: options.handle1 || '@gitcoin',
          handle2: options.handle2 || '@kbw',
          region: options.region || 'north_america',
          reference_url: options.reference_url || 'https://gitcoin.co',
          github_project_url: options.github_project_url || 'https://github.com/gitcoinco/web',
          'team_members[]': options.team_members || '',
          'tags[]': options.tags || '1'
        },
        form: true
      });
    });
});

Cypress.Commands.add('approveGrant', (grantSlug) => {
  cy.logout();
  cy.loginRootUser();

  const pk = grantSlug.match(/\/grants\/(\d*)\//)[1];
  const changePath = `_administrationgrants/grant/${pk}/change/`;

  cy.visit(changePath);
  cy.get('[name=active]').check();
  cy.get('[name=visible]').check();
  cy.get('[name=hidden]').uncheck();
  cy.get('[name=_save]').click();

  cy.logout();
});

/**
 * Simulates a paste event.
 *
 * @param subject A jQuery context representing a DOM element.
 * @param pasteOptions Set of options for a simulated paste event.
 * @param pasteOptions.pastePayload Simulated data that is on the clipboard.
 * @param pasteOptions.simple Determines whether or not to use a simple paste. Use this when there is no paste event bound to the element
 *                              resolved by the selector.
 * @param pasteOptions.pasteFormat The format of the simulated paste payload. Default value is 'text'.
 *
 * @returns The subject parameter.
 *
 * @example
 * cy.get('some-selector').paste({
 *  pastePayload: 'yolo',
 *  simple: false,
*  });
 */
export function paste(subject, { pastePayload, simple = true, pasteType = 'text' }) {
  if (simple) {
      subject[0].value = pastePayload;
      return;
  }

  // https://developer.mozilla.org/en-US/docs/Web/API/Element/paste_event
  const pasteEvent = Object.assign(new Event('paste', { bubbles: true, cancelable: true }), {
      clipboardData: {
          getData: (type = pasteType) => pastePayload,
      },
  });
  subject[0].dispatchEvent(pasteEvent);

  return subject;
}

Cypress.Commands.add(
  'paste',
  {
      prevSubject: true,
  },
  paste
);
