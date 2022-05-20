// handle from contxt
const trustHandle = document.contxt.github_handle;

const reader = new PassportReader('https://ceramic-clay.3boxlabs.com');

const apiCall = (url, givenPayload) => {

  return new Promise((resolve, reject) => {
    const csrfmiddlewaretoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    const headers = {'X-CSRFToken': csrfmiddlewaretoken, 'content_type': 'application/json'};
    const payload = Object.assign({
      'gitcoin_handle': this.githubHandle
    }, givenPayload || {});
    const verificationRequest = fetchData(url, 'POST', payload, headers);

    $.when(verificationRequest).then(response => {
      resolve(response);
    }).catch((err) => {
      reject(err);
    });
  });
};

Vue.component('active-trust-manager', {
  delimiters: [ '[[', ']]' ],
  data() {
    return {
      visibleModal: 'none',
      did: undefined,
      passport: undefined,
      passportVerified: false,
      loading: false,
      verificationError: false,
      console: console,
      round_start_date: parseMonthDay(document.round_start_date),
      round_end_date: parseMonthDay(document.round_end_date),
      services: document.services || []
    };
  },
  computed: {
    trust_bonus: function() {

      return Math.min(150, this.services.reduce((total, service) => {
        return (service.is_verified ? service.match_percent : 0) + total;
      }, 50));
    },
    serviceDict: function() {

      return this.services.reduce((services, service) => {
        // service by ref
        services[service.ref] = service;

        return services;
      }, {});
    }
  },
  methods: {
    showModal(modalName) {
      this.visibleModal = modalName;
      console.log(this.visibleModal);
    },
    hideModal() {
      this.visibleModal = 'none';
    },
    reset(clearStamps) {
      this.did = false;
      this.passport = false;
      this.passportVerified = false;

      if (clearStamps) {
        this.services.forEach((service) => {
          this.serviceDict[service.ref].is_verified = false;
        });
      }
    },
    async connectPassport() {
      // ensure selected account is known
      if (!selectedAccount) {
        // global wallet setup requirements
        needWalletConnection();
        initWallet();
      }

      // enter loading state
      this.loading = true;
      this.passportVerified = false;
      // clear errors
      this.verificationError = false;

      // get the selectedAccounts ceramic DID
      this.did = await reader.getDID(selectedAccount);

      // with did...
      if (this.did) {
        // extract passport from reader
        this.passport = await reader.getPassport(this.did);
        // with passport...
        if (this.passport) {
          this.passport.stamps.forEach((stamp) => {
            // validate the contents of the stamp collection
            const ignore_expiry_check = true;
            const expiry_check = ignore_expiry_check || new Date(stamp.credential.expirationDate) > new Date();

            if (stamp && stamp.credential && expiry_check && this.serviceDict[stamp.provider]) {
              // do didkit verify here? or only serverside?
              this.serviceDict[stamp.provider].is_verified = true;
              // make a request here to store the new state on the backend - need a nonce to sign and to pass the did to the backend
            }
          });
        }
      } else {
        // clear all state
        this.reset(true);
      }

      // done with loading state
      this.loading = false;
    },
    async verifyPassport() {
      // attempt to verify the passport
      try {
        if (document.challenge) {
          // request signature
          let signature = false;

          // attempt the signature
          try {
            signature = await web3.eth.personal.sign(document.challenge, selectedAccount);
          } catch {
            // set error state
            this.verificationError = 'There was an error; please sign the requested message';
            // clear all state
            this.reset(true);
          }

          // if we have sig, attempt to save the passports details into the backend
          const response = await apiCall(`/api/v2/profile/${trustHandle}/dpopp/verify`, {
            'eth_address': selectedAccount,
            'signature': signature,
            'did': this.did
          });

          // merge the response with state
          this.services.forEach((service) => {
            this.serviceDict[service.ref].is_verified = response.passport.stamps[service.ref] ? response.passport.stamps[service.ref].is_verified : false;
          });
          // notify success (temp)
          _alert('Your dPoPP Trust Bonus has been saved!', 'success', 6000);
          // mark verified
          this.passportVerified = true;
        }
      } catch (err) {
        // set error state
        this.verificationError = 'There was an error; please try again later';
        // clear all state but not the stamps
        this.reset();
      }
    }
  }
});

if (document.getElementById('gc-trust-manager-app')) {

  const trustManagerApp = new Vue({
    delimiters: [ '[[', ']]' ],
    el: '#gc-trust-manager-app',
    data: { }
  });
}

$(document).ready(function() {

  // scroll to the start of the trust requirements
  document.getElementById('gc-trust-manager-app').scrollIntoView({
    behavior: 'smooth'
  });

});
