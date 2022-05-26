// Helper to formulate csrfmiddlewaretoken authenticated POST requests
const apiCall = (url, givenPayload) => {

  return new Promise((resolve, reject) => {
    const csrfmiddlewaretoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    const headers = {'X-CSRFToken': csrfmiddlewaretoken, 'content_type': 'application/json'};
    const payload = Object.assign({
      'gitcoin_handle': document.contxt.github_handle
    }, givenPayload || {});
    const verificationRequest = fetchData(url, 'POST', payload, headers);

    $.when(verificationRequest).then(response => {
      resolve(response);
    }).catch((err) => {
      reject(err);
    });
  });
};

Vue.component('error-passport-content', {
  template: '<a>passport error</a>'
});

Vue.component('error-wallet-content', {
  template: '<a>wallet error</a>'
});

Vue.component('success-verify-content', {
  template: '<a>passport verified</a>'
});

// Modal to display state in
Vue.component('state-modal', {
  delimiters: [ '[[', ']]' ],
  props: {
    showModal: {
      type: Boolean,
      required: false,
      'default': false
    },
    type: {
      type: [ String, Boolean ],
      required: false,
      'default': false
    }
  },
  template: `
    <b-modal id="error-modal" @hide="dismissModal()" :visible="showModal" size="md" body-class="p-0" hide-header hide-footer>
      <template v-slot:default="{ hide }">
        <div class="modal-content rounded-0 p-0">
          <div class="p-2 text-center">
            [[type]]
            <template v-if="type == 'success-verify'">
              <success-verify-content></success-verify-content>
            </template>
            <template v-else-if="type == 'error-passport'">
              <error-passport-content></error-passport-content>
            </template>
            <template v-else-if="type == 'error-wallet'">
              <error-wallet-content></error-wallet-content>
            </template>
          </div>
        </div>
      </template>
    </b-modal>`,
  methods: {
    dismissModal() {
      this.$emit('modal-dismissed');
    }
  }
});

// Create the trust-bonus view
Vue.component('active-trust-manager', {
  delimiters: [ '[[', ']]' ],
  data() {
    return {
      IAMIssuer: document.iam_issuer,
      DIDKit: undefined,
      reader: new PassportReader(document.ceramic_url, 1),
      did: undefined,
      passport: document.is_passport_connected ? {} : undefined,
      passportVerified: document.is_passport_connected,
      trustBonus: (document.trust_bonus * 100) || 50,
      loading: false,
      verificationError: false,
      roundStartDate: parseMonthDay(document.round_start_date),
      roundEndDate: parseMonthDay(document.round_end_date),
      services: document.services || [],
      modalShow: false,
      modalName: false
    };
  },
  async mounted() {
    // await DIDKits bindings
    this.DIDKit = (await DIDKit);

    // on account change/connect etc... (get Passport state for wallet -- if verified, ensure that the passport connect button has been clicked first)
    document.addEventListener('dataWalletReady', () => (!this.passportVerified || this.loading) && this.connectPassportListener());
    // on wallet disconnect (clear Passport state)
    document.addEventListener('walletDisconnect', () => (!this.passportVerified ? this.reset(true) : false));
  },
  computed: {
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
      this.modalShow = true;
      this.modalName = modalName;
    },
    hideModal() {
      this.modalShow = false;

      // reset modal content after timeout
      setTimeout(() => {
        this.modalName = false;
      }, 1000);
    },
    reset(fullReset) {
      // this is set after we savePassport() if no verifications failed
      this.passportVerified = false;

      if (fullReset) {
        // clear current user state
        this.did = false;
        this.passport = false;

        // clear the stamps
        this.services.forEach((service) => {
          this.serviceDict[service.ref].is_verified = false;
        });
      }
    },
    async connectPassportListener() {
      this.connectPassport();
    },
    async connectPassport() {
      // enter loading state
      this.loading = true;
      // clear error state
      this.verificationError = false;

      // clear all state
      this.reset(true);

      // ensure selected account is known
      if (!selectedAccount) {
        // global wallet setup requirements - initiates web3 modal and then onConnect will emit dataWalletReady
        needWalletConnection();
        initWallet();

        return;
      }

      // get the selectedAccounts ceramic DID
      this.did = await this.reader.getDID(selectedAccount);

      // if loaded then the user has a ceramicAccount
      if (this.did) {
        // grab all the streams at once to reduce the required number of reqs
        const genesis = await this.reader._tulons.getGenesisHash(this.did);
        const streams = await this.reader._tulons.getGenesisStreams(genesis);
        // get records from the reader
        const records = await Promise.all([
          await this.reader.getPassport(this.did, streams),
          await this.reader.getAccounts(this.did, streams)
        ]);
        // extract passport from reader each refresh to ensure we catch any newly created streams
        const passport = records[0];
        // extract all accounts who have control of the passport
        const accounts = records[1];

        // if we didn't discover a passport or the accounts then enter fail state
        if (passport && accounts) {
          // check the validity of the Passport updating the score
          await this.verifyPassport(passport, accounts).then(() => {
            // store passport into state after verifying content to avoid display scoring until ready
            this.passport = passport;
          });
        } else {
          // error if no passport found
          this.verificationError = 'There is no Passport associated with this wallet';
        }
      } else {
        // error if no ceramic account found
        this.verificationError = 'There is no Ceramic Account associated with this wallet';
      }

      // done with loading state
      this.loading = false;
    },
    async verifyPassport(passport, accounts) {
      // check for a passport and then its validity
      if (passport) {

        // check if the stamps are unique to this user...
        const stampHashes = await apiCall(`/api/v2/profile/${document.contxt.github_handle}/passport/stamp/check`, {
          'did': this.did,
          'stamp_hashes': passport.stamps.map((stamp) => {
            return stamp.credential.credentialSubject.root;
          })
        });

        // perform checks on issuer, expiry, owner, VC validity and stamp_hash validity
        await Promise.all(passport.stamps.map(async(stamp) => {
          // set the service against provider and issuer
          const serviceDictId = `${this.IAMIssuer}#${stamp.provider}`;
          // validate the contents of the stamp collection
          const ignoreExpiryCheck = true;
          const ignoreIssuerCheck = false;
          const ignoreHashCheck = false;
          const ignoreOwnerCheck = false;
          const expiryCheck = ignoreExpiryCheck || new Date(stamp.credential.expirationDate) > new Date();
          const issuerCheck = ignoreIssuerCheck || stamp.credential.issuer === this.IAMIssuer;
          const hashCheck = ignoreHashCheck || stampHashes.checks[stamp.credential.credentialSubject.root] === true;
          const ownerCheck = ignoreOwnerCheck || accounts.indexOf(
            stamp.credential.credentialSubject.id.replace('did:ethr:', '').replace('#' + stamp.provider, '').toLowerCase()
          ) !== -1;

          // check exists and has valid expiry / issuer / hash / owner...
          if (stamp && this.serviceDict[serviceDictId] && stamp.credential && expiryCheck && issuerCheck && hashCheck && ownerCheck) {
            // verify with DIDKits verifyCredential()
            const verified = JSON.parse(await this.DIDKit.verifyCredential(
              JSON.stringify(stamp.credential),
              `{"proofPurpose":"${stamp.credential.proof.proofPurpose}"}`
            ));

            // if no errors then this is a valid VerifiableCredential issued by the known issuer and is unique to our store
            this.serviceDict[serviceDictId].is_verified = verified.errors.length === 0;
          }
          // collect array of true/false to check validity of every issued stamp (if stamp isn't recognised then it should be ignored (always true))
          return !this.serviceDict[serviceDictId] ? true : this.serviceDict[serviceDictId].is_verified;
        }));

        // set the new trustBonus score
        this.trustBonus = Math.min(150, this.services.reduce((total, service) => {
          return (service.is_verified ? service.match_percent : 0) + total;
        }, 50));
      }
    },
    async savePassport() {
      // attempt to verify the passport
      try {
        if (document.challenge) {
          // request signature
          let signature = false;

          // attempt the signature
          try {
            signature = await web3.eth.personal.sign(document.challenge, selectedAccount);
          } catch {
            // clear state
            this.reset();
            // set error
            this.verificationError = 'There was an error; please sign the requested message';

            // if there was an error in the sig - don't post to verify
            return false;
          }

          // if we have sig, attempt to save the passports details into the backend
          const response = await apiCall(`/api/v2/profile/${document.contxt.github_handle}/passport/verify`, {
            'eth_address': selectedAccount,
            'signature': signature,
            'did': this.did
          });

          // display error state if sig was bad
          if (response.error) {
            // Bad signature error
            this.verificationError = response.error;
          } else {
            // notify success (temp)
            _alert('Your Passport\'s Trust Bonus has been saved!', 'success', 6000);
          }

          // mark verified if no errors are returned
          this.passportVerified = !response.error;
        }
      } catch (err) {
        // clear state but not the stamps (if the problem was in passing the state to gitcoin then we want to know that here)
        this.reset();
        // set error state
        this.verificationError = 'There was an error; please try again later';
      }
    }
  }
});

if (document.getElementById('gc-trust-manager-app')) {
  const TrustManager = new Vue({
    delimiters: [ '[[', ']]' ],
    el: '#gc-trust-manager-app',
    data: { }
  });
}

$(document).ready(function() {
  if (!window.scrollY) {
    // scroll to the start of the trust requirements
    document.getElementById('gc-trust-manager-app').scrollIntoView({
      behavior: 'smooth'
    });
  }
});
