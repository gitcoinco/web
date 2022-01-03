describe('connect wallet: metamask', () => {
  it('pulls address from metamask accounts', () => {
    cy.impersonateUser();

    cy.visit('/', {
      onBeforeLoad(win) {
        win.web3 = {
          currentProvider: {
            autoRefreshOnNetworkChange: false,
            chainId: "0x539",
            isMetaMask: true,
            networkVersion: "1639855158747",
            selectedAddress: null
          }
        };
      }
    });

    cy.get('#navbarDropdownWallet').as('wallet').click();
    cy.contains('Connect Wallet').click();
    cy.contains('MetaMask').click();

    cy.get('@wallet').click();
    cy.get('#wallet-btn').should('contain.text', 'Change Wallet');
  });
});
