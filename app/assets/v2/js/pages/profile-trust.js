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

// Create the trust-bonus view
Vue.component('active-trust-manager', {
  delimiters: [ '[[', ']]' ],
  data() {
    return {
      IAMIssuer: document.iam_issuer,
      DIDKit: undefined,
      reader: new PassportReader(document.ceramic_url, 1),
      did: undefined,
      step: 1,
      passport: document.is_passport_connected ? {} : undefined,
      passportVerified: document.is_passport_connected,
      passportUrl: 'https://passport.gitcoin.co/',
      rawPassport: undefined,
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

    // error message attachment
    this.visitGitcoinPassport = `</br></br>Visit <a target="_blank" rel="noopener noreferrer" href="${this.passportUrl}" class="link cursor-pointer">Gitcoin Passport</a> to create your Passport and get started.`;

    // on account change/connect etc... (get Passport state for wallet -- if verified, ensure that the passport connect button has been clicked first)
    document.addEventListener('dataWalletReady', () => (!this.passportVerified || this.loading) && this.connectPassport());
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
      this.modalShow = this.modalName = false;
    },
    reset(fullReset) {
      // reset the step
      this.step = 1;
      // this is set after we savePassport() if no verifications failed
      this.passportVerified = false;

      if (fullReset) {
        // clear current user state
        this.did = false;
        this.passport = false;
        this.rawPassport = false;

        // clear the stamps
        this.services.forEach((service) => {
          this.serviceDict[service.ref].is_verified = false;
        });
      }
    },
    async passportActionHandler(forceRefresh) {
      // We can call the same handler to step through each operation...
      if (this.step === 1 || this.passportVerified || forceRefresh) {
        // connect and read the passport...
        await this.connectPassport();
        // when forceRefreshing we want to go straight to scoring
        if (forceRefresh) {
          // move to step 2 to immediately score the passport
          await this.passportActionHandler();
        }
      } else if (this.step === 2) {
        // verify the passports content (this recreates the trust bonus score based on the discovered stamps)
        await this.verifyPassport().then(() => {
          // move to step 3 (saving)
          this.step = 3;
          // store passport into state after verifying content to avoid displaying the scoring until ready
          this.passport = this.rawPassport;
        });
      } else if (this.step === 3) {
        // post a * save request to gitcoin (* note that gitcoin will enqueue the save request and changes may not be reflected immediately)
        await this.savePassport();
      }
    },
    async handleErrorClick(e) {
      const clickedElId = e.target.id;

      if (clickedElId === 'save-passport') {
        await this.savePassport();
      }
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
        return await onConnect();
      }

      // read the genesis from the selectedAccount (pulls the associated stream index)
      const genesis = await this.reader.getGenesis(selectedAccount);

      // grab all the streams at once to reduce the required number of reqs
      const streams = genesis && genesis.streams;

      // if loaded then the user has a ceramicAccount
      if (streams && Object.keys(streams).length > 0) {
        // get the selectedAccounts ceramic DID
        this.did = genesis.did;

        // read passport from reader each refresh to ensure we catch any newly created streams/updated stamps
        const passport = await this.reader.getPassport(selectedAccount, streams);

        // if we find a passport verify it and create a trust_bonus score
        if (passport) {
          // move to step 2
          this.step = 2;
          // store the passport so that we can verify its content in step-2 (before saving to this.passport)
          this.rawPassport = passport;
        } else {
          // error if no passport found
          this.verificationError = `There is no Passport associated with this wallet. ${this.visitGitcoinPassport}`;
        }
      } else {
        // error if no ceramic account found
        this.verificationError = `There is no Ceramic Account associated with this wallet. ${this.visitGitcoinPassport}`;
      }

      // done with loading state
      this.loading = false;
    },
    async verifyPassport() {
      // pull the raw passport...
      const passport = this.rawPassport;

      // enter loading
      this.loading = true;

      // check for a passport and then its validity
      if (passport) {
        // check if the stamps are unique to this user...
        const stampHashes = await apiCall(`/api/v2/profile/${document.contxt.github_handle}/passport/stamp/check`, {
          'did': this.did,
          'stamp_hashes': passport.stamps.map((stamp) => {
            return stamp.credential.credentialSubject.hash;
          })
        });

        // perform checks on issuer, expiry, owner, VC validity and stamp_hash validity
        await Promise.all(passport.stamps.map(async(stamp) => {
          if (stamp && Object.keys(stamp).length > 0) {
            // set the service against provider and issuer
            const serviceDictId = `${this.IAMIssuer}#${stamp.provider}`;
            // validate the contents of the stamp collection
            const expiryCheck = new Date(stamp.credential.expirationDate) > new Date();
            const issuerCheck = stamp.credential.issuer === this.IAMIssuer;
            const hashCheck = stampHashes.checks[stamp.credential.credentialSubject.hash] === true;
            const providerCheck = stamp.provider === stamp.credential.credentialSubject.provider;
            const ownerCheck = selectedAccount.toLowerCase() == stamp.credential.credentialSubject.id.replace('did:pkh:eip155:1:', '').toLowerCase();

            // check exists and has valid expiry / issuer / hash / owner...
            if (this.serviceDict[serviceDictId] && stamp.credential && expiryCheck && issuerCheck && hashCheck && providerCheck && ownerCheck) {
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
          }
        }));

        // set the new trustBonus score
        this.trustBonus = Math.min(150, this.services.reduce((total, service) => {
          return (service.is_verified ? service.match_percent : 0) + total;
        }, 50));
      }

      // stop loading
      this.loading = false;
    },
    async savePassport() {
      // enter loading
      this.loading = true;

      // attempt to verify the passport
      try {
        if (document.challenge) {
          // request signature
          let signature = false;

          // clear error state
          this.verificationError = undefined;

          // attempt the signature
          try {
            // get the signature for the document-wide provided challenge (set in dashboard/views.py::get_profile_tab::trust)
            signature = await web3.eth.personal.sign(document.challenge, selectedAccount);
          } catch {
            // set error - * note that #save-passport does not have an event handler - it is caught by `this.handleErrorClick(e)` as the event bubbles
            this.verificationError = 'In order to verify your Passport, the wallet message requires a signature.</br></br><a id="save-passport" class="link cursor-pointer">Click here</a> to verify ownership of your wallet and submit to Gitcoin.';
            // stop loading
            this.loading = false;

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
            // mark as verified
            this.passportVerified = true;
            // notify success (temp)
            _alert('Your Passport\'s Trust Bonus has been saved!', 'success', 6000);
          }
        }
      } catch (err) {
        // clear state but not the stamps (if the problem was in passing the state to gitcoin then we want to know that here)
        this.reset();
        // set error state
        this.verificationError = 'There was an error; please try again later';
      }

      // stop loading
      this.loading = false;
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
