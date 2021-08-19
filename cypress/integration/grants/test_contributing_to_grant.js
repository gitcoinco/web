describe('contributing to grant', () => {
  before(() => {
    cy.setupMetamask();
    cy.changeMetamaskNetwork('localhost');
  });

  afterEach(() => {
    cy.disconnectWallet();
    cy.logout();
  });

  after(() => {
    cy.clearWindows();
  });

  it('contributes eth to a single grant', () => {
    cy.createGrantSubmission().then((response) => {
      const grantUrl = response.body.url;

      cy.approveGrant(grantUrl);
      cy.impersonateUser();

      cy.visit(grantUrl);
      cy.get('#CookielawBannerAccept').click();

      cy.get('#navbarDropdownWallet').click();
      cy.contains('Connect Wallet').click();
      cy.contains('MetaMask').click();

      cy.acceptMetamaskAccess();

      cy.contains('Add to Cart').click();

      const pk = grantUrl.match(/\/grants\/(\d*)\//)[1];

      cy.get(`#select2-side-cart-currency-${pk}-container`).click();
      cy.get('input[role=searchbox]').type('ETH{enter}');
      cy.contains('CHECKOUT').click();

      cy.get('#gitcoin-grant-input-amount').type('{backspace}0');
      cy.contains('Standard Checkout').click();

      cy.confirmMetamaskTransaction();

      cy.get('body').should('contain.text', 'Thank you for contributing to open source!');
    });
  });

  it('contributes eth to multiple grants', () => {
    cy.createGrantSubmission().then((response) => {
      const grantUrl = response.body.url;

      cy.wrap(grantUrl).as('grant1');

      cy.approveGrant(grantUrl);
    });

    cy.createGrantSubmission().then((response) => {
      const grantUrl = response.body.url;

      cy.wrap(grantUrl).as('grant2');

      cy.approveGrant(grantUrl);
    });

    cy.impersonateUser();

    cy.get('#CookielawBannerAccept').click();

    cy.get('@grant1').then((grantUrl) => {
      cy.visit(grantUrl);
      cy.contains('Add to Cart').click();

      const pk = grantUrl.match(/\/grants\/(\d*)\//)[1];

      cy.get(`#select2-side-cart-currency-${pk}-container`).click();
      cy.get('input[role=searchbox]').type('ETH{enter}');
    });

    cy.get('@grant2').then((grantUrl) => {
      cy.visit(grantUrl);
      cy.contains('Add to Cart').click({force: true});

      const pk = grantUrl.match(/\/grants\/(\d*)\//)[1];

      cy.get(`#select2-side-cart-currency-${pk}-container`).click();
      cy.get('input[role=searchbox]').type('ETH{enter}');
    });

    cy.visit('grants/cart?');


    cy.contains('MetaMask').click();
    cy.acceptMetamaskAccess();

    cy.get('#gitcoin-grant-input-amount').type('{backspace}0');
    cy.contains('Standard Checkout').click();

    cy.confirmMetamaskTransaction();

    cy.get('body').should('contain.text', 'Thank you for contributing to open source!');
  });
});
