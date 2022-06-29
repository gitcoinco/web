// Helper to formulate csrfmiddlewaretoken authenticated POST requests
const apiCall = (url, givenPayload) => {

  return new Promise((resolve, reject) => {
    const csrfmiddlewaretoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    const headers = { 'X-CSRFToken': csrfmiddlewaretoken, 'content_type': 'application/json' };
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

Vue.component('trust-bonus-passport', {
  delimiters: [ '[[', ']]' ],
  props: {
    visible: {
      type: Boolean,
      required: false,
      'default': false
    },
    isUnlinkPending: {
      type: Boolean,
      required: false,
      'default': false
    },
    stampVerifications: {
      type: Array,
      required: false,
      'default': () => []
    },
    did: {
      type: String,
      required: true,
      'default': null
    },
    unlinkErrorMsg: {
      type: String,
      required: true,
      'default': null
    },
    unlinkSuccessMsg: {
      type: String,
      required: true,
      'default': null
    }
  },
  model: {
    prop: 'visible',
    event: 'change'
  },
  
  template: `<b-modal id="trust-bonus-passport" ref="passport-modal" v-model="modalShow" size="md" body-class="p-3" center hide-header>
  <h4>Passport Details</h4>
  <template v-if="address">
    <span class="text-muted">Your Passport is currently connected with the following information:</span>
    <br>
    <span class="text-muted">Wallet: [[address]]</span>
    <hr>
    <template v-if="stampVerifications.length > 0">
      <ul class="list-unstyled">
        <li class="mb-3" v-for="stamp in stampVerifications">
          <div class="text-muted" v-if="stamp.is_verified">
            [[stamp.provider]]
            <br>
            [[stamp.match_percent * 100]]%
          </div>
          <div class="text-muted" v-else>
          [[stamp.provider]]
          <br>
          <div class="d-flex flex-row justify-content-between">
            <div>0%</div>
            <div class="text-danger pl-3">[[stamp.errors[0] || "Not verified"]]</div>
          </div>
        </div>
        </li>
      </ul>
    </template>
    <template v-else>
      <span class="text-muted">You don't appear to have any stamps in your passport!</span>
    </template>
  </template>
  <template v-else>
    <span class="text-muted">Your account is currently not linked to any passport</span>
  </template>

  <div v-if="unlinkErrorMsg" class="d-flex px-0 pt-3 my-auto">
    <i class="fa-shield-virus fas mt-1 px-1" style="color: #d03e63"></i>
    <div class="d-inline ml-2 my-auto">
      <span style="color: #d03e63"><div class="font-smaller-2" @click="handleErrorClick" v-html="unlinkErrorMsg"></div></span>
    </div>
  </div>
  <div v-if="unlinkSuccessMsg" class="d-flex px-0 pt-3 my-auto">
    <i class="fa-shield-virus fas mt-1 px-1" style="color: #059669"></i>
    <div class="d-inline ml-2 my-auto">
      <span style="color: #059669"><div class="font-smaller-2" v-html="unlinkSuccessMsg"></div></span>
    </div>
  </div>

  <div v-if="isUnlinkPending" class="ml-2 mt-3 py-2">
    <div class="spinner-border spinner-border-sm"></div>
    Unlinking Passport ...
  </div>

  <template slot="modal-footer">
    <b-button size="nd" variant="light" @click="close">
      Close
    </b-button>
    <b-button v-if="address" size="md" variant="primary" @click="unlink">
      Unlink
    </b-button>
  </template>
</b-modal>
`,

  data() {
    return {
      // modalShow: this.visible
    };
  },

  computed: {
    modalShow: {
      set(newValue) {
        console.log('geri change:', newValue);
        this.$emit('change', newValue);
      },
      get() {
        return this.visible;
      }
    },
    address: function() {
      if (this.did) {
        let parts = this.did.split(':');

        return parts[parts.length - 1];
      }
      return null;
    }
  },

  methods: {
    close() {
      this.$bvModal.hide('trust-bonus-passport');
    },

    unlink() {
      this.$emit('unlink');
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
      step: 1,
      passport: document.is_passport_connected ? {} : undefined,
      passportVerified: document.is_passport_connected && (document.trust_bonus_status ? document.trust_bonus_status.indexOf('Error:') === -1 : false),
      passportUrl: 'https://passport.gitcoin.co/',
      rawPassport: undefined,
      trustBonus: (document.trust_bonus * 100) || 50,
      trustBonusStatus: document.trust_bonus_status,
      isTrustBonusRefreshInProggress: false,
      loading: false,
      verificationError: false,
      saveSuccessMsg: document.trust_bonus_status === 'pending_celery' ? 'Your Passport has been submitted.' : false,
      roundStartDate: parseMonthDay(document.round_start_date),
      roundEndDate: parseMonthDay(document.round_end_date),
      services: document.services || [],
      modalShow: false,
      modalName: false,
      pyVerificationError: false,
      passportDetailsShow: false,
      confirmUnlinkPassportShow: false,
      stampVerifications: document.passport_trust_bonus_stamp_validation,
      passportDid: document.passport_did,
      unlinkSuccessMsg: false,
      unlinkErrorMsg: false,
      isUnlinkPending: false
    };
  },
  async mounted() {
    // await DIDKits bindings
    this.DIDKit = (await DIDKit);

    // check for initial error state
    this.pyVerificationError = this.trustBonusStatus != null ? this.trustBonusStatus.indexOf('Error:') !== -1 : false;
    window.DD_LOGS && DD_LOGS.logger.info(`Initial trustBonusStatus for '${document.contxt.github_handle}': '${this.trustBonusStatus}'`);

    // error message attachment
    this.visitGitcoinPassport = `</br>Visit <a target="_blank" rel="noopener noreferrer" href="${this.passportUrl}" class="link cursor-pointer">Gitcoin Passport</a> to create your Passport and get started.`;

    // on account change/connect etc... (get Passport state for wallet -- if verified, ensure that the passport connect button has been clicked first)
    document.addEventListener('dataWalletReady', () => ((!this.pyVerificationError && !this.passportVerified) || this.loading) && this.connectPassport(true));

    // on wallet disconnect (clear Passport state)
    document.addEventListener('walletDisconnect', () => (!this.passportVerified ? this.reset(true) : false));

    // start watching for trust bonus status updates, in case the calculation is still pending
    if (this.trustBonusStatus === 'pending_celery') {
      this.refreshTrustBonus();
    } else if (this.pyVerificationError) {
      // clear all state
      this.reset(true);
      this.verificationError = this.trustBonusStatus;
    }
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
      this.$bvModal.show('trust-bonus-passport');
    },
    showPassportDetails(e) {
      this.unlinkSuccessMsg = false;
      this.unlinkErrorMsg = false;
      this.passportDetailsShow = true;
      e.preventDefault();
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
    async passportActionHandlerConnect(forceRefresh) {
      window.DD_LOGS && DD_LOGS.logger.info(`handle '${document.contxt.github_handle}' - action connect`);

      // We can call the same handler to step through each operation...
      // connect and read the passport...
      await this.connectPassport();
      // when forceRefreshing we want to go straight to scoring
      if (forceRefresh) {
        // move to step 2 to immediately score the passport
        await this.passportActionHandlerRefresh();
      }
    },
    async passportActionHandlerRefresh() {
      window.DD_LOGS && DD_LOGS.logger.info(`handle '${document.contxt.github_handle}' - action refresh`);
      await this.verifyPassport().then(() => {
        // move to step 3 (saving)
        this.step = 3;
        // store passport into state after verifying content to avoid displaying the scoring until ready
        this.passport = this.rawPassport;
      });
    },
    async passportActionHandlerSave() {
      window.DD_LOGS && DD_LOGS.logger.info(`handle '${document.contxt.github_handle}' - action save`);
      await this.savePassport();
    },
    async handleErrorClick(e) {
      window.DD_LOGS && DD_LOGS.logger.info(`handle '${document.contxt.github_handle}' - action error click`);
      const clickedElId = e.target.id;

      if (clickedElId === 'save-passport') {
        await this.savePassport();
      }
    },
    async refreshTrustBonus() {
      // if we have sig, attempt to save the passports details into the backend
      const url = `/api/v2/profile/${document.contxt.github_handle}/passport/trust_bonus`;

      const _getTrustBonus = () => {
        const getTrustBonusRequest = fetchData(url, 'GET');

        $.when(getTrustBonusRequest).then(response => {
          this.trustBonusStatus = response.passport_trust_bonus_status;
          this.pyVerificationError = this.trustBonusStatus.indexOf('Error:') !== -1;

          if (response.passport_trust_bonus_status === 'pending_celery') {
            _refreshTrustBonus();
          } else if (response.passport_trust_bonus_status === 'saved') {
            this.trustBonus = (parseFloat(response.passport_trust_bonus) * 100) || 50;
            this.isTrustBonusRefreshInProggress = false;
            this.saveSuccessMsg = false;
            this.stampVerifications = response.passport_trust_bonus_stamp_validation;
            this.passportDid = response.passport_did;
          } else {
            this.isTrustBonusRefreshInProggress = false;
            this.saveSuccessMsg = false;

            if (this.pyVerificationError) {
              this.verificationError = this.trustBonusStatus;
            }
          }
          // check for error state
          if (this.pyVerificationError) {
            this.step = 1;
            // clear all state
            this.reset(true);
          }
        }).catch((error) => {
          window.DD_LOGS && DD_LOGS.logger.error(`Error when refreshing trust bonus, handle: '${document.contxt.github_handle}' did: ${this.did}. Error: ${error}`);
          _refreshTrustBonus();
        });
      };

      const _refreshTrustBonus = () => {
        setTimeout(_getTrustBonus, 5000);
      };

      if (!this.isTrustBonusRefreshInProggress) {
        this.isTrustBonusRefreshInProggress = true;
        _refreshTrustBonus();
      }
    },
    /*
     * The ignoreErrors attribute is intended to be used when calling this function automatically on page
     * load and not expecting this to trigger an error.
     */
    async connectPassport(ignoreErrors) {
      DD_LOGS.logger.info(`Connecting passport for ${document.contxt.github_handle}`);

      // enter loading state
      this.loading = true;
      // clear error state
      this.verificationError = false;
      this.saveSuccessMsg = false;

      // clear all state
      this.reset(true);

      // ensure selected account is known
      if (!selectedAccount) {
        if (!web3Modal) {
          // set-up call to onConnect on walletReady events
          const ret = await needWalletConnection();

          // will setup wallet and emit walletReady event
          let ret1 = await initWallet();

          window.DD_LOGS && DD_LOGS.logger.info(`Connecting passport for ${document.contxt.github_handle} - skip, no web3`);
          this.loading = false;
          return;
        }

        // call onConnect directly after first load to force web3Modal to display every time its called
        const ret = await onConnect();

        window.DD_LOGS && DD_LOGS.logger.info(`Connecting passport for ${document.contxt.github_handle} - skip, no selected account`);
        this.loading = false;
        return;
      }

      window.DD_LOGS && DD_LOGS.logger.info(`Connecting passport for handle ${document.contxt.github_handle} and address ${selectedAccount}`);

      try {
        // read the genesis from the selectedAccount (pulls the associated stream index)
        const genesis = await this.reader.getGenesis(selectedAccount);

        // grab all the streams at once to reduce the required number of reqs
        const streams = genesis && genesis.streams;

        // if loaded then the user has a ceramicAccount
        if (streams && Object.keys(streams).length > 0) {
          // reset py error
          this.pyVerificationError = false;

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
            window.DD_LOGS && DD_LOGS.logger.info(`There is no Passport associated with this wallet, did: ${this.did}`);
            this.verificationError = ignoreErrors ? false : `There is no Passport associated with this wallet. ${this.visitGitcoinPassport}`;
          }
        } else {
          // error if no ceramic account found
          window.DD_LOGS && DD_LOGS.logger.info(`There is no Ceramic Account associated with this wallet, address: ${selectedAccount}`);
          this.verificationError = ignoreErrors ? false : `There is no Ceramic Account associated with this wallet. ${this.visitGitcoinPassport}`;
        }
      } catch (error) {
        window.DD_LOGS && DD_LOGS.logger.error(`Error when connecting passport, account: '${selectedAccount}'. Error: ${error}`);
      } finally {
        // done with loading state
        this.loading = false;
      }

      window.DD_LOGS && DD_LOGS.logger.info(`DONE - Connecting passport for ${selectedAccount}`);
    },
    async verifyPassport() {
      // pull the raw passport...
      const passport = this.rawPassport;

      // enter loading
      this.loading = true;

      // reset errors
      this.verificationError = undefined;

      // Filter the stamps, include only those with valid (not undefined) credentialSubject (credentialSubject has been undefined on rare occasions)
      const stamps = (passport && passport.stamps) ? passport.stamps.filter((stamp) => stamp.credential && stamp.credential.credentialSubject) : undefined;

      // check for a passport and then its validity
      if (passport && stamps) {
        try {
          // check if the stamps are unique to this user...
          const stampHashes = await apiCall(`/api/v2/profile/${document.contxt.github_handle}/passport/stamp/check`, {
            'did': this.did,
            'stamp_hashes': stamps.map((stamp) => {
              return stamp.credential.credentialSubject.hash;
            })
          });

          // perform checks on issuer, expiry, owner, VC validity and stamp_hash validity
          await Promise.all(stamps.map(async(stamp) => {
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

        } catch (error) {
          console.error('Error checking passport: ', error);
          window.DD_LOGS && DD_LOGS.logger.error(`Error checking passport, handle: '${document.contxt.github_handle}' did: ${this.did}. Error: ${error}`);
          this.verificationError = 'Oh, we had a technical error while scoring. Please give it another try.';
          throw error;
        } finally {
          this.loading = false;
        }
      } else {
        window.DD_LOGS && DD_LOGS.logger.info(`Error checking passport, handle: '${document.contxt.github_handle}' did: ${this.did}. Passport is empty or has no stamps.`);
        this.verificationError = `The Passport associated with this wallet is empty. ${this.visitGitcoinPassport}`;
        this.loading = false;
        throw 'Passport is empty!';
      }
    },
    async savePassport() {
      // enter loading
      this.loading = true;
      this.saveSuccessMsg = false;

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
            this.verificationError = 'In order to verify your Passport, the wallet message requires a signature.</br><a id="save-passport" class="link cursor-pointer">Click here</a> to verify ownership of your wallet and submit to Gitcoin.';
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
            // _alert('Your Passport\'s Trust Bonus has been saved!', 'success', 6000);
            this.saveSuccessMsg = 'Your Passport has been submitted.';
            this.trustBonusStatus = 'pending_celery';
            this.refreshTrustBonus();
          }
        }
      } catch (error) {
        window.DD_LOGS && DD_LOGS.logger.error(`Error submitting passport for trust bonus calculation, handle: '${document.contxt.github_handle}' did: ${this.did}. Error: ${error}`);
        // clear state but not the stamps (if the problem was in passing the state to gitcoin then we want to know that here)
        this.reset();
        // set error state
        this.verificationError = 'There was an error; please try again later';
      }

      // stop loading
      this.loading = false;
    },
    async showConfirmUnlinkPassport() {
      this.confirmUnlinkPassportShow = true;
    },
    async confirmUnlinkPassport() {
      this.confirmUnlinkPassportShow = false;
      this.unlinkPassport();
    },
    async unlinkPassport() {
      // enter loading
      this.loading = true;
      this.saveSuccessMsg = false;
      this.unlinkSuccessMsg = false;
      this.unlinkErrorMsg = false;
      this.isUnlinkPending = true;

      // attempt to verify the passport
      try {
        if (document.challenge) {
          // clear error state
          this.verificationError = undefined;

          // if we have sig, attempt to save the passports details into the backend
          const response = await apiCall(`/api/v2/profile/${document.contxt.github_handle}/passport/unlink`, {});
          
          this.isUnlinkPending = false;

          // display error state if sig was bad
          if (response.error) {
            // Bad signature error
            this.unlinkErrorMsg = response.error;
          } else {
            // mark as verified
            this.passportVerified = true;
            // notify success (temp)
            this.unlinkSuccessMsg = 'Your Passport has been unlinked.';
            this.trustBonusStatus = 'saved';
            this.stampVerifications = [];
            this.passportDid = null;
            this.trustBonus = 50;
          }
        }
      } catch (error) {
        window.DD_LOGS && DD_LOGS.logger.error(`Error submitting passport for trust bonus calculation, handle: '${document.contxt.github_handle}' did: ${this.did}. Error: ${error}`);
        // clear state but not the stamps (if the problem was in passing the state to gitcoin then we want to know that here)
        this.reset();
        // set error state
        this.unlinkErrorMsg = 'There was an error; please try again later';
        this.isUnlinkPending = false;
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
    data: {}
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
