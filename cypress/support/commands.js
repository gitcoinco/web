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
Cypress.Commands.add('loginRootUser', () => {
  const url = 'http://localhost:8000/_administrationlogin/';
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
  cy.visit('http://localhost:8000/impersonate/4/');
});
