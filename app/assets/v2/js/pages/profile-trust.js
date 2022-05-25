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

Vue.component('active-trust-manager', {
  delimiters: [ '[[', ']]' ],
  data() {
    return {
      reader: new PassportReader('https://ceramic.staging.dpopp.gitcoin.co', 1),
      issuer: 'did:key:z6Mkmhp2sE9s4AxFrKUXQjcNxbDV7WTM8xdh1FDNmNDtogdw',
      DIDKit: undefined,
      did: undefined,
      accounts: undefined,
      // TODO geri: following to lines would get the trust bonus from the BE
      // trust_bonus: document.trust_bonus,
      // passport: document.passport,
      passport: null,
      passportVerified: document.is_passport_connected,
      passportVerifiedLocally: false,
      loading: false,
      verificationError: false,
      round_start_date: parseMonthDay(document.round_start_date),
      round_end_date: parseMonthDay(document.round_end_date),
      services: document.services || [],
      visibleModal: 'none'
    };
  },
  async mounted() {
    // await DIDKits bindings
    this.DIDKit = (await DIDKit);

    // on account change/connect etc...
    document.addEventListener('dataWalletReady', () => this.connectPassportListener());
    // on wallet disconnect (clear Passport state)
    document.addEventListener('walletDisconnect', () => this.reset(true));
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
    },
    hideModal() {
      this.visibleModal = 'none';
    },
    reset(clearStamps) {
      this.did = false;
      this.accounts = false;
      this.passport = false;
      this.passportVerified = false;
      this.passportVerifiedLocally = false;

      this.verificationError = false;

      if (clearStamps) {
        this.services.forEach((service) => {
          this.serviceDict[service.ref].is_verified = false;
        });
      }
    },
    async connectPassportListener() {
      this.connectPassport();
    },
    async connectPassport() {
      // ensure selected account is known
      if (!selectedAccount) {
        // global wallet setup requirements - initiates web3 modal and then onConnect will emit dataWalletReady
        needWalletConnection();
        initWallet();

        return;
      }

      // enter loading state
      this.loading = true;

      // clear all state
      this.reset(true);

      console.log('TODO trust-bonus selectedAccount', selectedAccount);

      // get the selectedAccounts ceramic DID
      this.did = await this.reader.getDID(selectedAccount);

      // if loaded then the user has a ceramicAccount
      if (this.did) {
        // grab all the streams at once to reduce the required number of reqs
        const genesis = await this.reader._tulons.getGenesisHash(this.did);
        const streams = await this.reader._tulons.getGenesisStreams(genesis);

        // extract all accounts who have control of the passport
        this.accounts = await this.reader.getAccounts(this.did, streams);
        // extract passport from reader each refresh to ensure we catch any newly created streams
        this.passport = await this.reader.getPassport(this.did, streams);

        console.log('TODO trust-bonus  this.passport', this.passport);

        // check the validity of the Passport updating the score (@TODO - have the verification check hashes in the dupes table)
        this.passportVerifiedLocally = await this.verifyPassport();
      }

      // done with loading state
      this.loading = false;
    },
    async verifyPassport() {
      // check for a passport and then its validity
      if (this.passport) {
        // get a boolean for if the given passport would verify if presented to the back-end for verification
        return (await Promise.all(this.passport.stamps.map(async(stamp) => {
          // set the service against provider and issuer
          const serviceDictId = `${this.issuer}#${stamp.provider}`;
          // validate the contents of the stamp collection
          const ignore_expiry_check = true;
          const ignore_issuer_check = true;
          const ignore_owner_check = false;
          const ignore_hash_check = true;
          const expiry_check = ignore_expiry_check || new Date(stamp.credential.expirationDate) > new Date();
          const issuer_check = ignore_issuer_check || stamp.credential.issuer === this.issuer;
          const owner_check = ignore_owner_check || this.accounts.indexOf(
            stamp.credential.credentialSubject.id.replace('did:ethr:', '').replace('#' + stamp.provider, '').toLowerCase()
          ) !== -1;

          // @TODO - need to check the hash against the dupes store - collect roots and request all checks at once?
          const hash_check = ignore_hash_check && stamp.credential.credentialSubject.root;

          // check exists and has valid expiry / issuer / owner...
          if (stamp && this.serviceDict[serviceDictId] && stamp.credential && expiry_check && issuer_check && owner_check && hash_check) {
            // verify with DIDKits verifyCredential()
            const verified = JSON.parse(await this.DIDKit.verifyCredential(
              JSON.stringify(stamp.credential),
              `{"proofPurpose":"${stamp.credential.proof.proofPurpose}"}`
            ));

            // if no errors then this is a valid VerifiableCredential issued by the known issuer and unique to our store
            this.serviceDict[serviceDictId].is_verified = verified.errors.length === 0;
          }

          // collect array of true/false to check validity of every issued stamp (if stamp isn't recognised then it should be ignored (always true))
          return !this.serviceDict[serviceDictId] ? true : this.serviceDict[serviceDictId].is_verified;
        }))).reduce((isVerified, verified) => !isVerified ? false : verified, true);
      }

      // not verified if we don't have a Passport
      return false;
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
            // set error state
            this.verificationError = 'There was an error; please sign the requested message';
            // clear all state
            this.reset(true);
          }

          // if we have sig, attempt to save the passports details into the backend
          const response = await apiCall(`/api/v2/profile/${document.contxt.github_handle}/dpopp/verify`, {
            'eth_address': selectedAccount,
            'signature': signature,
            'did': this.did
          });

          // @TODO: rather than saving - set and forget - saving will be enqueued and the act of submitting should set `passportVerified=true`

          // merge the response with state
          this.services.forEach((service) => {
            const provider = service.ref.split('#')[1];

            // check if the stamp was verified by the server and update local state to match
            this.serviceDict[service.ref].is_verified = response.passport.stamps[provider] ? response.passport.stamps[provider].is_verified : false;
          });

          // notify success (temp)
          _alert('Your dPoPP Trust Bonus has been saved!', 'success', 6000);
          // mark verified
          this.passportVerified = true;
        }
      } catch (err) {
        // set error state
        this.verificationError = 'There was an error; please try again later';
        // clear state but not the stamps (if the problem was in passing the state to gitcoin then we want to know that here)
        this.reset();
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
