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

const Web3 = require('web3');
const HDWalletProvider = require("@truffle/hdwallet-provider");

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

Cypress.Commands.add('impersonateStaffUser', () => {
  cy.loginRootUser();
  cy.visit('impersonate/1/');
});

Cypress.Commands.add('logout', () => {
  cy.request('logout/?next=/');
});

// accept cookie banner
Cypress.Commands.add('acceptCookies', () => {
  cy.visit('/');
  cy.contains('I agree').click();
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

Cypress.Commands.add('createActiveGrantRound', () => {
  cy.logout();
  
  cy.loginRootUser();

  cy.visit('_administrationgrants/grantclr/add/');
  cy.get('[name=customer_name]').type('TestGrantCLR');
  cy.get('[name=round_num]').type('1');
  cy.get('[name=sub_round_slug]').type('TestGrantCLR');
  cy.get('[name=display_text]').type('Test Grant CLR');
  cy.get('[name=is_active]').check();
  cy.get('[name=start_date_0]').type('2021-12-20');
  cy.get('[name=start_date_1]').type('21:12:38');
  cy.get('[name=end_date_0]').type('2041-1-1');
  cy.get('[name=end_date_1]').type('21:12:38');
  cy.get('[name=_save]').click();

  cy.logout();
});


Cypress.Commands.add('setupWallet', () => {
  cy.on('window:load', (win) => {

    let hd_provider = new HDWalletProvider({
      mnemonic: Cypress.env('SECRET_WORDS'),
      providerOrUrl: 'http://127.0.0.1:8545',
      addressIndex: 5
    });

    win.ethereum = hd_provider;
    win.provider = hd_provider;
    win.web3 = new Web3(hd_provider);
    let onConnect = async function() {
      console.log('TESTING -- dummy onConnect override');
    };

    Object.defineProperty(win, 'onConnect', {
      set (value) {
      },
      get () {
        return onConnect;
      }
    })

  });
});
