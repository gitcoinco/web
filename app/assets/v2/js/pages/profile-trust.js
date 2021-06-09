// handle from contxt
const trustHandle = document.contxt.github_handle;

const apiCall = (url, givenPayload) => {

  return new Promise((resolve, reject) => {
    const csrfmiddlewaretoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    const headers = {'X-CSRFToken': csrfmiddlewaretoken};
    const payload = JSON.stringify(Object.assign({
      'gitcoin_handle': this.githubHandle
    }, givenPayload || {}));
    const verificationRequest = fetchData(url, 'POST', payload, headers);

    $.when(verificationRequest).then(response => {
      resolve(response);
    }).catch((err) => {
      reject(err);
    });
  });
};

Vue.component('sms-verify-modal', {
  delimiters: [ '[[', ']]' ],
  data: function() {
    return {
      csrf: $("input[name='csrfmiddlewaretoken']").val(),
      phone: '',
      validNumber: false,
      errorMessage: '',
      verified: document.verified,
      code: '',
      timePassed: 0,
      timeInterval: 0,
      display_email_option: false,
      countDownActive: false,
      forceStep: false,
      awaitingResponse: false
    };
  },
  props: {
    showValidation: {
      type: Boolean,
      required: false,
      'default': false
    },
    validationStep: {
      required: true
    },
    service: {
      type: Object,
      required: true
    }
  },
  computed: {
    step() {
      return this.forceStep || this.validationStep;
    }
  },
  template: `
    <b-modal id="sms-modal" @hide="dismissVerification()" :visible="showValidation" size="lg" body-class="p-0" center hide-header hide-footer>
      <template v-slot:default="{ hide }">
        <div class="modal-content p-0">
          <div class="top rounded-top p-2 text-center" style="background: #ECE9FF;">
            <div class="w-100">
              <button @click="dismissVerification()" type="button" class="close position-absolute mt-2" style="right: 1rem" data-dismiss="modal" aria-label="Close">
                <span aria-hidden="true">&times;</span>
              </button>
            </div>
            <div class="bg-white d-flex mt-4 mx-auto p-1 rounded-circle" style="width: 74px; height: 74px;">
              <i class="fa fa-mobile-alt fa-3x m-auto"></i>
            </div>
            <h3 class="my-4"> [[(step !== 'disconnect' ? 'Verify with' : 'Disconnect from')]] SMS </h3>
          </div>
          <div class="font-smaller-1 line-height-3 spacer-px-4 spacer-px-lg-6 spacer-py-5">
            <div class="mx-5 mb-4 text-center" v-if="step == 'intro'">
              <p class="mb-4 text-left">
                Verify your phone number to increase your trust level by providing extra sybil resistance. The higher your trust level, the more impact your donation will have on the match fund algorithm.
              </p>
              <p class="mb-4 text-left">
                Gitcoin does NOT store your phone number. <a target="_blank" rel="noopener noreferrer" class="gc-text-blue font-smaller-1"
                href="https://twitter.com/owocki/status/1271088915982675974">Read more</a> about why we are asking for account verification, or how Gitcoin <a target="_blank" rel="noopener noreferrer" class="gc-text-blue font-smaller-1"
                href="https://twitter.com/owocki/status/1271088915982675974">preserves your privacy</a>.
              </p>
              <div id='verify_offline_target' class="text-left" style="display:none;">
                <strong>Verify Offline</strong>
                <br />
                <br />
                <a href="mailto:support@gitcoin.co">Email Gitcoin</a>, and we will verify your information within 5-10 business days.
                <br />
                <br />
                IMPORTANT: Be sure to include (1) your gitcoin username (2) proof of ownership of a SMS number.
              </div>
              <div class="mb-1 float-right">
                <b-button @click="forceStep='requestVerification'" variant="primary" class="btn-primary mt-5 mb-2">
                  Connect SMS
                </b-button>
                <br />
                <b-button id="verify_offline" variant="link" class="py-0">Verify Offline</b-button><span id="verify_offline_or"> or </span><b-button @click="dismissVerification()" variant="link" class="py-0">Skip</b-button>
              </div>
            </div>
            <div class="mx-5 my-5 text-center" v-if="step == 'requestVerification'">
              <p class="mb-5">We will send you a verification code.</p>
              <vue-tel-input ref="tel-input" :validCharactersOnly="true" @validate="isValidNumber" v-model="phone"
                :enabledCountryCode="true" :autofocus="true" :required="true" mode="international"
                inputClasses="form-control" placeholder="+1 8827378273"
                :inputOptions="{showDialCode: true}"
              ></vue-tel-input>
              <div v-if="timeInterval > timePassed">
                <span class="label-warning">Wait [[ timeInterval - timePassed ]] second before request another
                  code</span>
              </div>
              <div v-if="errorMessage">
                <span class="label-warning">[[ errorMessage ]]</span>
              </div>
              <div class="float-right">
                <b-button @click="requestVerification()" variant="primary" class="btn-primary mt-5 mb-2">
                  Send verification code
                </b-button>
                <br />
                <b-button @click="hide()" variant="link">Cancel</b-button>
              </div>
            </div>
            <div class="mx-5 my-5 text-center" v-if="step == 'verifyNumber'">
              <div class="mb-3">
                <h1 class="font-bigger-4 font-weight-bold">Verify your phone number</h1>
              </div>
              <p class="mb-5">Enter the verification code sent to your number.</p>
              <input class="form-control" type="number" required v-model="code">
              <div v-if="timeInterval > timePassed">
                <span class="label-warning">Wait [[ timeInterval - timePassed ]] second before request another
                  code</span>
              </div>
              <div v-if="errorMessage">
                <span class="label-warning">[[ errorMessage ]]</span>
              </div>
              <b-button @click="validateCode()" variant="primary" class="btn-primary mt-5">Submit</b-button>
              <br />
              <b-button @click="startVerification()" variant="link">Change number</b-button>
              <b-button @click="resendCode()" variant="link">Resend Code</b-button>
                <b-button @click="resendCode('email')" variant="link" v-if="display_email_option">Send email</b-button>
            </div>

            <div v-if="step === 'validation-complete'">
              <div>
                Your SMS verification was successful. Thank you for helping make Gitcoin more sybil resistant!
              </div>
              <b-button @click="dismissVerification" variant="primary" class="btn-primary mt-5 mb-2 px-4 float-right">
                Done
              </b-button>
            </div>

            <div v-if="step === 'disconnect'">
              <div class="w-100">
                <p>
                  <div>
                    Are you sure you want to disconnect your SMS verification?
                  </div>
                  <b-button @click="disconnectSMS" variant="primary" class="btn btn-primary mt-5 px-5 float-right">
                    <b-spinner small v-if="awaitingResponse" type="grow" class="ml-n4 position-absolute spinner-grow spinner-grow-sm"></b-spinner>
                    Yes, disconnect
                  </b-button>
                </p>
              </div>
            </div>

          </div>
        </div>
      </template>
    </b-modal>`,
  methods: {
    dismissVerification() {
      // localStorage.setItem('dismiss-sms-validation', true);
      this.$emit('modal-dismissed');
      setTimeout(() => {
        this.forceStep = false;
      }, 1000);
    },
    // VALIDATE
    validateCode() {
      const vm = this;

      if (vm.code) {
        const verificationRequest = fetchData(`/api/v0.1/profile/${trustHandle}/verify_user_sms/`, 'POST', {
          code: vm.code,
          phone: vm.phone
        }, {'X-CSRFToken': vm.csrf});

        $.when(verificationRequest).then(response => {
          vm.verificationEnabled = false;
          vm.verified = true;
          vm.service.is_verified = true;
          vm.forceStep = 'validation-complete';
        }).catch((e) => {
          if (e.status == 403) {
            vm.errorMessage = e.responseText;
          } else {
            vm.errorMessage = e.responseJSON.msg;
          }
        });
      }
    },
    startVerification() {
      this.phone = '';
      this.forceStep = 'requestVerification';
      this.validNumber = false;
      this.errorMessage = '';
      this.code = '';
      this.timePassed = 0;
      this.timeInterval = 0;
      this.display_email_option = false;
    },
    countdown() {
      const vm = this;

      if (!vm.countDownActive) {
        vm.countDownActive = true;

        setInterval(() => {
          vm.timePassed += 1;
        }, 1000);
      }
    },
    resendCode(delivery_method) {
      const e164 = this.phone.replace(/\s/g, '');
      const vm = this;

      vm.errorMessage = '';

      if (vm.validNumber) {
        const verificationRequest = fetchData(`/api/v0.1/profile/${trustHandle}/request_user_sms`, 'POST', {
          phone: e164,
          delivery_method: delivery_method || 'sms'
        }, {'X-CSRFToken': vm.csrf});

        vm.errorMessage = '';

        $.when(verificationRequest).then(response => {
          // set the cooldown time to one minute
          this.timePassed = 0;
          this.timeInterval = 60;
          this.countdown();
          this.display_email_option = response.allow_email;
        }).catch((e) => {
          if (e.status == 403) {
            vm.errorMessage = e.responseText;
          } else {
            vm.errorMessage = e.responseJSON.msg;
          }
        });
      }
    },
    // REQUEST VERIFICATION
    requestVerification(event) {
      const e164 = this.phone.replace(/\s/g, '');
      const vm = this;

      if (vm.validNumber) {
        const verificationRequest = fetchData(`/api/v0.1/profile/${trustHandle}/request_user_sms`, 'POST', {
          phone: e164
        }, {'X-CSRFToken': vm.csrf});

        vm.errorMessage = '';

        $.when(verificationRequest).then(response => {
          this.forceStep = 'verifyNumber';
          this.timePassed = 0;
          this.timeInterval = 60;
          this.countdown();
          this.display_email_option = response.allow_email;
        }).catch((e) => {
          if (e.status == 403) {
            vm.errorMessage = e.responseText;
          } else {
            vm.errorMessage = e.responseJSON.msg;
          }
        });
      }
    },
    async disconnectSMS() {
      this.awaitingResponse = true;
      this.forceStep = 'disconnect';
      try {
        const response = await apiCall(`/api/v0.1/profile/${trustHandle}/disconnect_user_sms`);

        if (response.ok) {
          this.service = Object.assign(this.service, response);
        }
      } catch (err) {
        console.log(err);
      } finally {
        this.awaitingResponse = false;
        this.dismissVerification();
        _alert('You have successfully disconnected your SMS verification.', 'success', 3000);
      }
    },
    isValidNumber(validation) {
      console.log(validation);
      this.validNumber = validation.isValid;
    }
  }
});

Vue.component('twitter-verify-modal', {
  delimiters: [ '[[', ']]' ],
  data: function() {
    return {
      tweetText: '',
      twitterHandle: '',
      validationError: '',
      forceStep: false,
      awaitingResponse: false
    };
  },
  props: {
    showValidation: {
      type: Boolean,
      required: false,
      'default': false
    },
    validationStep: {
      required: true
    },
    service: {
      type: Object,
      required: true
    }
  },
  computed: {
    encodedTweetText: function() {
      return encodeURIComponent(this.service.verify_tweet_text);
    },
    tweetIntentURL: function() {
      return `https://twitter.com/intent/tweet?text=${this.encodedTweetText}`;
    },
    step() {
      return this.forceStep || this.validationStep;
    }
  },
  template: `
    <b-modal id="twitter-modal" @hide="dismissVerification()" :visible="showValidation" size="lg" body-class="p-0" center hide-header hide-footer>
      <template v-slot:default="{ hide }">
        <div class="modal-content p-0">
          <div class="top rounded-top p-2 text-center" style="background: #ECE9FF;">
            <div class="w-100">
              <button @click="dismissVerification()" type="button" class="close position-absolute mt-2" style="right: 1rem" data-dismiss="modal" aria-label="Close">
                <span aria-hidden="true">&times;</span>
              </button>
            </div>
            <div class="bg-white d-flex mt-4 mx-auto p-1 rounded-circle" style="width: 74px; height: 74px;">
              <i class="fab fa-twitter fa-3x m-auto" style="color: rgb(0, 172, 237);"></i>
            </div>
            <h3 class="my-4"> [[(step !== 'disconnect' ? 'Verify with' : 'Disconnect from')]] Twitter </h3>
          </div>
          <div class="font-smaller-1 line-height-3 spacer-px-4 spacer-px-lg-6 spacer-py-5">
            <div class="mb-4 text-left">
              <div v-if="step === 'send-tweet'">
                <p class="mb-4 font-subheader text-left">
                  We want to verify your Twitter account. To do so, you must first send a standardized
                  Tweet from your account, then we'll validate it's there.
                </p>
                <p class="mb-4 font-subheader text-left">
                  The Tweet should say:
                </p>
                <p class="mb-4 font-subheader text-left">
                  <em>[[service.verify_tweet_text]]</em>
                </p>
                <div class="float-right text-center">
                  <div class="mt-5 mb-2">
                    <a :href="tweetIntentURL" @click="clickedSendTweet" role="button" class="btn btn-primary mb-2" target="_blank">
                      Send Tweet
                    </a>
                  </div>
                  <a href="" @click="clickedAlreadySent">
                    I have already Tweeted this
                  </a>
                </div>
              </div>
              <div v-if="step === 'validate-tweet' || step == 'perform-validation'">
                <p class="mb-4">
                  Now we'll validate that you've sent the tweet. Enter your Twitter handle and press "Verify Tweet".
                </p>
                <div class="input-group">
                  <div class="input-group-prepend">
                    <span class="input-group-text form-control" id="basic-addon1">@</span>
                  </div>
                  <input type="text" class="form-control" placeholder="handle" aria-label="handle" aria-describedby="basic-addon1" required maxlength="15" v-model="twitterHandle">
                </div>
                <div v-if="validationError !== ''" style="color: red">
                  <small>[[validationError]]</small>
                </div>

                <div class="d-flex justify-content-between mt-5 mb-2">
                  <span class="my-auto">
                    <a href="" v-if="validationError !== ''" @click="clickedGoBack">
                      Go Back
                    </a>
                  </span>
                  <b-button @click="clickedValidate" :disabled="step === 'perform-validation'" variant="primary" class="btn-primary  mt-3 mb-2">
                    <b-spinner small v-if="step === 'perform-validation'" type="grow"></b-spinner>
                    Verify Tweet
                  </b-button>
                </div>

              </div>
              <div v-if="step === 'validation-complete'">
                <div>Your Twitter verification was successful. Thank you for helping make Gitcoin more sybil resistant!</div>
                <b-button @click="dismissVerification" variant="primary" class="btn btn-primary mt-5 px-5 float-right">
                  Done
                </b-button>
              </div>
              <div v-if="step === 'disconnect'">
                <div class="w-100">
                  <p>
                    <div>
                      Are you sure you want to disconnect your Twitter verification?
                    </div>
                    <b-button @click="disconnectTwitter" variant="primary" class="btn btn-primary mt-5 px-5 float-right">
                      <b-spinner small v-if="awaitingResponse" type="grow" class="ml-n4 position-absolute spinner-grow spinner-grow-sm"></b-spinner>
                      Yes, disconnect
                    </b-button>
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </template>
    </b-modal>`,
  methods: {
    dismissVerification() {
      this.$emit('modal-dismissed');
      setTimeout(() => {
        this.forceStep = false;
      }, 1000);
    },
    clickedSendTweet(event) {
      this.forceStep = 'validate-tweet';
    },
    clickedAlreadySent(event) {
      event.preventDefault();
      this.forceStep = 'validate-tweet';
    },
    clickedGoBack(event) {
      event.preventDefault();
      this.forceStep = 'send-tweet';
      this.validationError = '';
    },
    clickedValidate(event) {
      event.preventDefault();

      this.twitterHandle = this.twitterHandle.trim();

      // Strip leading @ if user includes it
      if (this.twitterHandle.startsWith('@')) {
        this.twitterHandle = this.twitterHandle.split('@')[1];
      }

      // Validate handle is 15 word characters
      const isValidHandle = null !== this.twitterHandle.match(/^(\w){1,15}$/);

      if (!isValidHandle) {
        this.validationError = 'Please enter a valid Twitter handle';
        return;
      }

      // Reset after a prior error
      this.validationError = '';

      this.forceStep = 'perform-validation';

      this.verifyTwitter();
    },
    verifyTwitter() {
      const csrfmiddlewaretoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
      const payload = JSON.stringify({
        'twitter_handle': this.twitterHandle
      });
      const headers = {'X-CSRFToken': csrfmiddlewaretoken};

      const verificationRequest = fetchData(`/api/v0.1/profile/${trustHandle}/verify_user_twitter`, 'POST', payload, headers);

      $.when(verificationRequest).then(response => {
        if (response.ok) {
          this.forceStep = 'validation-complete';
          this.service.is_verified = true;
        } else {
          this.validationError = response.msg;
          this.forceStep = 'validate-tweet';
        }

      }).catch((_error) => {
        this.validationError = 'There was an error; please try again later';
        this.forceStep = 'validate-tweet';
      });
    },
    async disconnectTwitter() {
      this.awaitingResponse = true;
      this.forceStep = 'disconnect';
      try {
        const response = await apiCall(`/api/v0.1/profile/${trustHandle}/disconnect_user_twitter`);

        if (response.ok) {
          this.service = Object.assign(this.service, response);
        }
      } catch (err) {
        console.log(err);
      } finally {
        this.awaitingResponse = false;
        this.dismissVerification();
        _alert('You have successfully disconnected from Twitter.', 'success', 3000);
      }
    }
  }
});

Vue.component('poap-verify-modal', {
  delimiters: [ '[[', ']]' ],
  data: function() {
    return {
      hideTemporarily: false,
      ethAddress: '',
      signature: '',
      validationError: '',
      forceStep: false,
      awaitingResponse: false
    };
  },
  props: {
    showValidation: {
      type: Boolean,
      required: false,
      'default': false
    },
    service: {
      type: Object,
      required: true
    },
    validationStep: {
      type: String,
      required: true
    }
  },
  computed: {
    step() {
      return this.forceStep || this.validationStep;
    }
  },
  template: `
    <b-modal id="poap-modal" @hide="dismissVerification()" :visible="showValidation && !hideTemporarily" size="lg" body-class="p-0" center hide-header hide-footer>
      <template v-slot:default="{ hide }">
        <div class="modal-content p-0">
          <div class="top rounded-top p-2 text-center" style="background: #ECE9FF;">
            <div class="w-100">
              <button @click="dismissVerification()" type="button" class="close position-absolute mt-2" style="right: 1rem" data-dismiss="modal" aria-label="Close">
                <span aria-hidden="true">&times;</span>
              </button>
            </div>
            <div class="bg-white d-flex mt-4 mx-auto p-1 rounded-circle" style="width: 74px; height: 74px;">
              <img class="m-auto" src="/static/v2/images/project_logos/poap.svg" alt="POAP Logo" width="45">
            </div>
            <h3 class="my-4"> [[(step !== 'disconnect' ? 'Verify with' : 'Disconnect from')]] POAP </h3>
          </div>
          <div class="font-smaller-1 line-height-3 spacer-px-4 spacer-px-lg-6 spacer-py-5">
            <div v-if="step === 'validate-address'">
              <p class="mb-4 font-subheader text-left">
                POAP is a software system that allows humans to collect badges (in the form of non fungible tokens) every time they participate in an activity,
                whether in person or remotely. <a href="https://www.poap.xyz/#faqs" target="_blank">Learn more.</a>
              </p>
              <p class="mb-4 font-subheader text-left">
                Verify your POAP badges by connecting your ETH wallet below. Then we'll confirm your account holds at least one POAP badge that's been there for at least 15 days.
              </p>
              <div class="mt-5 mb-2">
                <b-button @click="clickedPullEthAddress" variant="primary" class="btn btn-primary mt-5 px-5 float-right">
                  <b-spinner small v-if="awaitingResponse" type="grow" class="ml-n4 position-absolute spinner-grow spinner-grow-sm"></b-spinner>
                  Connect with POAP
                </b-button>
              </div>
            </div>
            <div v-if="step === 'validate-poap' || step == 'perform-validation'">
              <p class="mb-4">
                We'll check for POAP badges held by the following account.
              </p>
              <div class="input-group">
                <input type="text" readonly class="form-control" placeholder="eth-address" aria-label="handle" aria-describedby="basic-addon1" required maxlength="255" v-model="ethAddress">
              </div>
              <div v-if="validationError !== ''" style="color: red;" class="mt-2">
                <small>[[validationError]]</small>
              </div>
              <div>
                <a href="" @click="clickedChangeWallet" :disabled="step === 'perform-validation'" class="mt-2">
                  Change Wallet
                </a>
              </div>
              <div class="d-flex justify-content-between mt-5 mb-2">
                <span class="my-auto">
                  <a href="" v-if="validationError !== ''" @click="clickedGoBack">
                    Go Back
                  </a>
                </span>
                <b-button @click="clickedValidate" :disabled="step === 'perform-validation'" variant="primary" class="btn-primary">
                  <b-spinner small v-if="step === 'perform-validation'" type="grow" ></b-spinner>
                  Verify
                </b-button>
              </div>
            </div>
            <div v-if="step === 'validation-complete'">
              <div>
                Your POAP verification was successful. Thank you for helping make Gitcoin more sybil resistant!
              </div>
              <b-button @click="dismissVerification" variant="primary" class="btn-primary mt-5 mb-2 px-4 float-right">
                Done
              </b-button>
            </div>
            <div v-if="step === 'disconnect'">
              <div class="w-100">
                <p>
                  <div>
                    Are you sure you want to disconnect your POAP verification?
                  </div>
                  <b-button @click="disconnectPOAP" variant="primary" class="btn btn-primary mt-5 px-5 float-right">
                    <b-spinner small v-if="awaitingResponse" type="grow" class="ml-n4 position-absolute spinner-grow spinner-grow-sm"></b-spinner>
                    Yes, disconnect
                  </b-button>
                </p>
              </div>
            </div>
          </div>
        </div>
      </template>
    </b-modal>`,
  methods: {
    dismissVerification() {
      // If we're only hiding the modal to allow wallet selection, don't emit this event, which
      // would prevent it from popping up again after the user completes their selection.
      if (!this.hideTemporarily) {
        this.$emit('modal-dismissed');
        setTimeout(() => {
          this.forceStep = false;
        }, 1000);
      }
    },
    clickedGoBack(event) {
      event.preventDefault();
      this.forceStep = 'validate-address';
      this.ethAddress = '';
      this.validationError = '';
    },
    getEthAddress() {
      const accounts = web3.eth.getAccounts();

      $.when(accounts).then((result) => {
        const ethAddress = result[0];

        this.ethAddress = ethAddress;
        this.forceStep = 'validate-poap';
        // this.showValidation = true;
        this.hideTemporarily = false;
      }).catch((_error) => {
        this.validationError = 'Error getting ethereum accounts';
        this.forceStep = 'validate-address';
        // this.showValidation = true;
        this.hideTemporarily = false;
      });

    },
    generateSignature() {
      // Create a signature using the provided web3 account
      web3.eth.personal.sign('verify_poap_badges', this.ethAddress)
        .then(signature => {
          this.signature = signature;
          this.verifyPOAP();
        }).catch((_error) => {
          this.validationError = 'Error sign message declined';
          this.forceStep = 'validate-poap';
          this.hideTemporarily = false;
        });
    },
    connectWeb3Wallet() {
      // this.showValidation = false;
      this.hideTemporarily = true;
      onConnect().then((result) => {
        this.getEthAddress();
      }).catch((_error) => {
        this.validationError = 'Error connecting ethereum accounts';
        this.forceStep = 'validate-address';
        // this.showValidation = true;
        this.hideTemporarily = false;
      });
    },
    clickedPullEthAddress(event) {
      // Prompt web3 login if not connected
      event.preventDefault();
      if (!provider) {
        this.connectWeb3Wallet();
      } else {
        this.getEthAddress();
      }
    },
    clickedChangeWallet(event) {
      event.preventDefault();
      this.validationError = '';
      this.connectWeb3Wallet();
    },
    clickedValidate(event) {
      event.preventDefault();
      this.validationError = '';
      this.forceStep = 'perform-validation';
      this.generateSignature();
    },
    async verifyPOAP() {
      this.awaitingResponse = true;
      try {
        const response = await apiCall(`/api/v0.1/profile/${trustHandle}/verify_user_poap`, {
          'eth_address': this.ethAddress,
          'signature': this.signature
        });

        if (response.ok) {
          this.forceStep = 'validation-complete';
          this.service.is_verified = true;
        } else {
          this.validationError = response.msg;
          this.forceStep = 'validate-poap';
        }
      } catch (err) {
        console.log(_error);
        this.validationError = 'There was an error; please try again later';
        this.forceStep = 'validate-poap';
      } finally {
        this.awaitingResponse = false;
      }
    },
    async disconnectPOAP() {
      this.awaitingResponse = true;
      this.forceStep = 'disconnect';
      try {
        const response = await apiCall(`/api/v0.1/profile/${trustHandle}/disconnect_user_poap`);

        if (response.ok) {
          this.service = Object.assign(this.service, response);
        }
      } catch (err) {
        console.log(err);
      } finally {
        this.awaitingResponse = false;
        this.dismissVerification();
        _alert('You have successfully disconnected from POAP.', 'success', 3000);
      }
    },
    clickedClose() {
      this.$emit('modal-dismissed');
    }
  }
});

Vue.component('poh-verify-modal', {
  delimiters: [ '[[', ']]' ],
  data: function() {
    return {
      hideTemporarily: false,
      ethAddress: '',
      signature: '',
      validationError: '',
      forceStep: false,
      awaitingResponse: false
    };
  },
  props: {
    showValidation: {
      type: Boolean,
      required: false,
      'default': false
    },
    validationStep: {
      type: String,
      required: true
    },
    service: {
      type: Object,
      required: true
    }
  },
  computed: {
    step() {

      return this.forceStep || this.validationStep;
    }
  },
  template: `
    <b-modal id="poh-modal" @hide="dismissVerification()" :visible="showValidation && !hideTemporarily" size="lg" body-class="p-0" center hide-header hide-footer>
      <template v-slot:default="{ hide }">
        <div class="modal-content p-0">
          <div class="top rounded-top p-2 text-center" style="background: #fceeca;">
            <div class="w-100">
              <button @click="dismissVerification()" type="button" class="close position-absolute mt-2" style="right: 1rem" data-dismiss="modal" aria-label="Close">
                <span aria-hidden="true">&times;</span>
              </button>
            </div>
            <div class="bg-white d-flex mt-4 mx-auto p-1 rounded-circle" style="width: 74px; height: 74px;">
              <img class="m-auto" src="/static/v2/images/project_logos/poh-min.svg" alt="POH Logo">
            </div>
            <h3 class="my-4"> [[(step !== 'disconnect' ? 'Verify with' : 'Disconnect from')]] Proof of Humanity </h3>
          </div>
          <div class="font-smaller-1 line-height-3 spacer-px-4 spacer-px-lg-6 spacer-py-5">
            <div v-if="step === 'validate-address'">
              <p class="mb-4 font-subheader text-left">
                Proof of Humanity is a system combining webs of trust with reverse Turing tests and dispute resolution. Verify and help create a sybil-proof list of humans.
              </p>
              <p class="mb-4 font-subheader text-left">
                To verify, please connect your ETH wallet. Then we'll confirm your account is registered with POH.
              </p>
              <div class="mt-5 mb-2">
                <b-button @click="clickedPullEthAddress" variant="primary" class="btn-primary mb-2 float-right" target="_blank">
                  Connect with POH
                </b-button>
              </div>
            </div>
            <div v-if="step === 'validate-poh' || step == 'perform-validation'">
              <p class="mb-4">
                We'll check for POH registration.
              </p>
              <div class="input-group">
                <input type="text" readonly class="form-control" placeholder="eth-address" aria-label="handle" aria-describedby="basic-addon1" required maxlength="255" v-model="ethAddress">
              </div>
              <div v-if="validationError !== ''" style="color: red;" class="mt-2">
                <small>[[validationError]]</small>
              </div>
              <div>
                <a href="" @click="clickedChangeWallet" :disabled="step === 'perform-validation'" class="mt-2">
                  Change Wallet
                </a>
              </div>
              <div class="d-flex justify-content-between mt-5 mb-2">
                <span class="my-auto">
                  <a href="" v-if="validationError !== ''" @click="clickedGoBack">
                    Go Back
                  </a>
                </span>
                <b-button @click="clickedValidate" :disabled="step === 'perform-validation'" variant="primary" class="btn-primary">
                  <b-spinner small v-if="step === 'perform-validation'" type="grow" ></b-spinner>
                  Verify
                </b-button>
              </div>
            </div>
            <div v-if="step === 'validation-complete'">
              <div>
                Your Proof of Humanity verification was successful. Thank you for helping make Gitcoin mroe sybil resistant!
              </div>
              <b-button @click="dismissVerification" variant="primary" class="btn btn-primary mt-5 px-5 float-right">Done</b-button>
            </div>
            <div v-if="step === 'disconnect'">
              <div class="w-100">
                <p>
                  <div>
                    Are you sure you want to disconnect your POH verification?
                  </div>
                  <b-button @click="disconnectPOH" variant="primary" class="btn btn-primary mt-5 px-5 float-right">
                    <b-spinner small v-if="awaitingResponse" type="grow" class="ml-n4 position-absolute spinner-grow spinner-grow-sm"></b-spinner>
                    Yes, disconnect
                  </b-button>
                </p>
              </div>
            </div>
          </div>
        </div>
      </template>
    </b-modal>`,
  methods: {
    dismissVerification() {
      // If we're only hiding the modal to allow wallet selection, don't emit this event, which
      // would prevent it from popping up again after the user completes their selection.
      if (!this.hideTemporarily) {
        this.$emit('modal-dismissed');
        setTimeout(() => {
          this.forceStep = false;
        }, 1000);
      }
    },
    clickedGoBack(event) {
      event.preventDefault();
      this.forceStep = 'validate-address';
      this.ethAddress = '';
      this.validationError = '';
    },
    getEthAddress() {
      const accounts = web3.eth.getAccounts();

      $.when(accounts)
        .then((result) => {
          const ethAddress = result[0];

          this.ethAddress = ethAddress;
          this.forceStep = 'validate-poh';
          this.hideTemporarily = false;
        })
        .catch((_error) => {
          this.validationError = 'Error getting ethereum accounts';
          this.forceStep = 'validate-address';
          this.hideTemporarily = false;
        });
    },
    generateSignature() {
      web3.eth.personal.sign('verify_poh_registration', this.ethAddress).then((signature) => {
        this.signature = signature;
        this.verifyPOH();
      })
        .catch((_error) => {
          this.validationError = 'Error sign message declined';
          this.forceStep = 'validate-poh';
          this.hideTemporarily = false;
        });
    },
    connectWeb3Wallet() {
      this.hideTemporarily = true;
      onConnect()
        .then((result) => {
          this.getEthAddress();
        })
        .catch((_error) => {
          this.validationError = 'Error connecting ethereum accounts';
          this.forceStep = 'validate-address';
          this.hideTemporarily = false;
        });
    },
    clickedPullEthAddress(event) {
      event.preventDefault();
      if (!provider) {
        this.connectWeb3Wallet();
      } else {
        this.getEthAddress();
      }
    },
    clickedChangeWallet(event) {
      event.preventDefault();
      this.validationError = '';
      this.connectWeb3Wallet();
    },
    clickedValidate(event) {
      event.preventDefault();
      this.validationError = '';
      this.forceStep = 'perform-validation';
      this.generateSignature();
    },
    async verifyPOH() {
      try {
        const response = await apiCall(`/api/v0.1/profile/${trustHandle}/verify_user_poh`, {
          eth_address: this.ethAddress,
          signature: this.signature
        });

        if (response.ok) {
          this.forceStep = 'validation-complete';
          this.service.is_verified = true;
        } else {
          this.validationError = response.msg;
          this.forceStep = 'validate-poh';
        }
      } catch (err) {
        this.validationError = 'There was an error; please try again later';
        this.forceStep = 'validate-poh ';
      }
    },
    async disconnectPOH() {
      this.awaitingResponse = true;
      this.forceStep = 'disconnect';
      try {
        const response = await apiCall(`/api/v0.1/profile/${trustHandle}/disconnect_user_poh`);

        if (response.ok) {
          this.service = Object.assign(this.service, response);
        }
      } catch (err) {
        console.log(err);
      } finally {
        this.awaitingResponse = false;
        this.dismissVerification();
        _alert('You have successfully disconnected from POH.', 'success', 3000);
      }
    }
  }
});

Vue.component('brightid-verify-modal', {
  delimiters: [ '[[', ']]' ],
  data: function() {
    return {
      calls: [],
      verifying: false,
      forceStep: false,
      awaitingResponse: false
    };
  },
  props: {
    showValidation: {
      type: Boolean,
      required: false,
      'default': false
    },
    validationStep: {
      type: String,
      required: true
    },
    brightidUuid: {
      type: String,
      required: true
    },
    service: {
      type: Object,
      required: true
    }
  },
  computed: {
    brightIdLink() {
      return `https://app.brightid.org/link-verification/http:%2f%2fnode.brightid.org/Gitcoin/${this.brightidUuid}`;
    },
    brightIdAppLink() {
      return `brightid://link-verification/http:%2f%2fnode.brightid.org/Gitcoin/${this.brightidUuid}`;
    },
    step() {
      return this.forceStep || this.validationStep;
    }
  },
  template: `
    <b-modal id="brightid-modal" @hide="dismissVerification()" :visible="showValidation" size="lg" body-class="p-0" center hide-header hide-footer>
      <template v-slot:default="{ hide }">
        <div class="modal-content p-0">
          <div class="top rounded-top p-2 text-center" style="background: #FFF0EB;">
            <div class="w-100">
              <button @click="dismissVerification()" type="button" class="close position-absolute mt-2" style="right: 1rem" data-dismiss="modal" aria-label="Close">
                <span aria-hidden="true">&times;</span>
              </button>
            </div>
            <img class="mt-4 rounded-circle bg-white" src="/static/v2/images/project_logos/brightid.png" alt="BrightID Logo" width="74">
            <h3 class="my-4"> [[(step !== 'disconnect' ? 'Verify with' : 'Disconnect from')]] BrightID </h3>
          </div>
          <div class="font-smaller-1 line-height-3 spacer-px-4 spacer-px-lg-6 spacer-py-5">

            <template v-if="step === 'connect-brightid'">
              <div class="w-100">
                <p>
                  BrightID is a digital identity solution that ensures accounts in any application are created by real humans; each user is unique and only has one account.
                  <a href="https://www.brightid.org/" target="_blank">Learn More</a>.
                </p>
                <p>
                  To increase your Trust Bonus using BrightID, you must first get connected. Follow these steps:
                </p>
                <p>
                  <strong>Step 1</strong>: Download the BrightID App on your mobile device<br />
                  <a href="https://apps.apple.com/us/app/brightid/id1428946820">
                    <img src="/static/v2/images/app_stores/apple_app_store.svg" width="100">
                  </a>
                  <a href="https://play.google.com/store/apps/details?id=org.brightid">
                    <img src="/static/v2/images/app_stores/google_play_store.png" width="125">
                  </a>
                </p>
                <div>
                  <strong>Step 2</strong>: Connect BrightID to Gitcoin by scanning this QR code
                  from the BrightID app, or <a :href="brightIdLink">clicking here</a> from your mobile device.
                  <div style="display: flex; justify-content: center; text-align: center;" class="mt-5">
                    <qrcode :string="brightIdAppLink" :size="175"></qrcode>
                  </div>
                </div>
                <hr class="mt-5" />
                <div class="col-12 my-4 text-center">
                  <b-button @click="moveToVerifyBrightid" variant="primary" class="btn btn-primary mt-4 px-5 float-right">
                    Connect BrightID
                  </b-button>
                </div>
              </div>
            </template>

            <template v-else-if="step === 'verify-brightid'">
              <div class="w-100">
                <p>
                  BrightID is a digital identity solution that ensures accounts in any application are created by real humans; each user is unique and only has one account.
                  <a href="https://www.brightid.org/" target="_blank">Learn More</a>.
                </p>
                <p>
                  Now that you've connected your BrightID, you need to get verified by connecting with other real humans.
                </p>
                <p>
                  <strong>Join a Gitcoin + BrightID Verification Party</strong><br />
                  <small class="text-muted">
                    You can learn more about how BrightID works and make connections that will help you get verified on the verifications parties.
                    Register for one of the events.
                  </small>
                  <template v-for="call in service.calls">
                    <div class="row mb-3 mt-3">
                      <div class="col-md-6">
                        <strong class="d-block">[[call.when]]</strong>
                        <div class="font-caption">
                          <template v-for="date in call.dates">
                            At <span>[[formatDate(date.timeStart)]]</span> - <span>[[formatDate(date.timeEnd)]]</span><br />
                          </template>
                        </div>
                      </div>
                      <div class="col-md-6 my-auto">
                        <a :href="call.link" target="_blank" class="btn btn-sm btn-block btn-primary px-4">Register on <br> [[call.platform]]</a>
                      </div>
                    </div>
                  </template>

                  <b-button @click="verifyBrightid" variant="primary" class="btn btn-primary mt-5 px-5 float-right">
                    <b-spinner small v-if="verifying" type="grow" class="ml-n4 position-absolute spinner-grow spinner-grow-sm"></b-spinner>
                    Check Status
                  </b-button>
                </p>
              </div>
            </template>

            <template v-if="step === 'verification-complete'">
              <div class="w-100">
                <p>
                  <div>
                    Your BrightID verification was successful. Thank you for helping make Gitcoin more sybil resistant!
                  </div>
                  <b-button @click="dismissVerification" variant="primary" class="btn btn-primary mt-5 px-5 float-right">Done</b-button>
                </p>
              </div>
            </template>

            <template v-if="step === 'disconnect'">
              <div class="w-100">
                <p>
                  <div>
                    Are you sure you want to disconnect your BrightID verification?
                  </div>
                  <b-button @click="disconnectBrightid" variant="primary" class="btn btn-primary mt-5 px-5 float-right">
                    <b-spinner small v-if="awaitingResponse" type="grow" class="ml-n4 position-absolute spinner-grow spinner-grow-sm"></b-spinner>
                    Yes, disconnect
                  </b-button>
                </p>
              </div>
            </template>
          </div>
        </div>
      </template>
    </b-modal>`,

  methods: {
    dismissVerification() {
      this.$emit('modal-dismissed');
      setTimeout(() => {
        this.forceStep = false;
      }, 1000);
    },
    formatDate(date) {
      let options = {hour: 'numeric', minute: 'numeric', dayPeriod: 'short'};

      return new Intl.DateTimeFormat('en-US', options).format(new Date(date));
    },
    moveToVerifyBrightid() {
      this.forceStep = 'verify-brightid';
    },
    async verifyBrightid() {
      this.verifying = true;
      try {
        const response = await apiCall(`/api/v0.1/profile/${trustHandle}/verify_user_brightid`);

        if (response.ok) {
          this.service._status = response.msg;
          if (this.service._status == 'verified') {
            this.service.is_verified = true;
            this.service.status = false;
            this.forceStep = 'verification-complete';
          } else {
            this.service._state = 'verify-brightid';
            this.service.status = 'Awaiting Verification';
            // alert pending
            _alert('Pending Validation...', 'danger', 2000);
          }
        }
      } catch (err) {
        console.log(err);
      } finally {
        this.verifying = false;
      }
    },
    async disconnectBrightid() {
      this.awaitingResponse = true;
      this.forceStep = 'disconnect';
      try {
        const response = await apiCall(`/api/v0.1/profile/${trustHandle}/disconnect_user_brightid`);

        if (response.ok) {
          this.service = Object.assign(this.service, response);
        }
      } catch (err) {
        console.log(err);
      } finally {
        this.awaitingResponse = false;
        this.dismissVerification();
        _alert('You have successfully disconnected from BrightID.', 'success', 3000);
      }
    }
  }
});

Vue.component('idena-verify-modal-content', {
  template: `
    <div class="font-smaller-1 line-height-3 spacer-px-4 spacer-px-lg-6 spacer-py-5">
      <p>Idena is the first proof-of-person blockchain based on democratic principles. Every node is linked to a cryptoidentity – one single person with equal voting power and mining income.</p>
      <p>To start mining Idena, you need to prove you are a unique human. It does not require the disclosure of any personal data (no KYC). Simply appear online when the validation ceremony starts and solve a series of flip-tests (CAPTCHAs).</p>
      <slot></slot>
    </div>
  `
});

Vue.component('idena-verify-modal', {
  delimiters: [ '[[', ']]' ],
  data: function() {
    return {
      calls: [],
      verifying: false,
      forceStep: false,
      initiated: false,
      awaitingResponse: false
    };
  },
  props: {
    showValidation: {
      type: Boolean,
      required: false,
      'default': false
    },
    validationStep: {
      type: String,
      required: true
    },
    service: {
      type: Object,
      required: true
    }
  },
  computed: {
    step() {
      return this.forceStep || this.validationStep;
    }
  },
  template: `
    <b-modal id="idena-modal" @hide="dismissVerification()" :visible="showValidation" size="lg" body-class="p-0" center hide-header hide-footer>
      <template v-slot:default="{ hide }">
        <div class="modal-content p-0">
          <div class="top rounded-top p-2 text-center" style="background: #ECE9FF;">
            <div class="w-100">
              <button @click="dismissVerification()" type="button" class="close position-absolute mt-2" style="right: 1rem" data-dismiss="modal" aria-label="Close">
                <span aria-hidden="true">&times;</span>
              </button>
            </div>
            <svg class="mt-4" width="74" height="74" viewBox="0 0 74 74" fill="none" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">
              <circle cx="37" cy="37" r="37" fill="url(#pattern0)"/>
              <defs>
                <pattern id="pattern0" patternContentUnits="objectBoundingBox" width="1" height="1">
                <use xlink:href="#image0" transform="translate(-0.0116279) scale(0.00581395)"/>
                </pattern>
                <image id="image0" width="176" height="172" xlink:href="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAALAAAACsCAYAAADboya+AAAK3GlDQ1BJQ0MgUHJvZmlsZQAASImVlwdQU+kWgM+96SGhBRCQEnoTpBNAeg2gIB1EJSQBQokhCajYlcUVXAsqIljRVREFy1LEhliwLYq9L8gioDwXCzbQvAs8wu6+ee/NOzP/Pd+ce/5T/rn/zLkA9DCOSJSFKgNkC6XiyCBfZnxCIpPUDQTQASLQwJXDlYh8IiLCAJNx/Vf5eB+QEX3HeiTWv7//r6LK40u4AEgSxik8CTcb42ZsDXBFYikA7ihmN5ovFY3wXYzVxFiBGPeOcNoYD49wyijjlUd9oiP9MDYGINM4HHEaAM0WszPzuGlYHFoExrZCnkCI8XKMPbnpHB7GWF6Ykp09b4T7MTbH/EUAdDWMWSl/ipn2l/gp8vgcTpqcx/oaFbK/QCLK4iz8P4/mf0t2Vu54DlNs0dLFwZGY1sTO72HmvFA5C1NmhI+zgDfqP8rpucEx48yV+CWOM4/jHyrfmzUjbJxTBYFseRwpO3qc+ZKAqHEWz4uU50oV+/mMM0c8kTc3M0ZuT+ez5fHz06PjxjlPEDtjnCWZUaETPn5yuzg3Ul4/XxjkO5E3UN57tuRP/QrY8r3S9Ohgee+cifr5Qp+JmJJ4eW08vn/AhE+M3F8k9ZXnEmVFyP35WUFyuyQvSr5Xin2cE3sj5GeYwQmJGGcIgyBgQgxkgRTEwIFAEIAQ+FL+AulIM37zRAvFgrR0KdMHu3F8JlvItZnCtLe1twMYub9jn8R7jdF7iWhcm7CtqgLwOCmTyU5N2EJuARxLBqDWTdjMZwMo9wBcOc3NFeeN2fAjDwJQQQnUQAv0wAjMwRrswRncwRsCIATCIRoSYA5wIR2yscrnw2JYAYVQDBtgC5TDLtgLB+EIHIcGOA3n4TJch1twD55AB3TDaxiAjzCEIAgJoSMMRAvRR0wQK8QeYSGeSAAShkQiCUgykoYIkVxkMbIKKUZKkHJkD1KFHENOIueRq0g78gjpRPqQd8hXFIfSUDVUFzVFp6Is1AcNRaPR2WgamoPmowXoOrQMrUQPo/XoefQ6eg/tQF+jgzjAKeA0cAY4axwL54cLxyXiUnFi3FJcEa4UV4mrwTXhWnF3cB24ftwXPBHPwDPx1nh3fDA+Bs/F5+CX4tfiy/EH8fX4i/g7+E78AP47gU7QIVgR3AhsQjwhjTCfUEgoJewn1BEuEe4RugkfiUSiBtGM6EIMJiYQM4iLiGuJO4i1xGZiO7GLOEgikbRIViQPUjiJQ5KSCknbSIdJ50i3Sd2kz2QFsj7ZnhxITiQLySvJpeRD5LPk2+Qe8hBFmWJCcaOEU3iUhZT1lH2UJspNSjdliKpCNaN6UKOpGdQV1DJqDfUS9Sn1vYKCgqGCq8JMBYHCcoUyhaMKVxQ6Fb7QVGmWND9aEi2Xto52gNZMe0R7T6fTTene9ES6lL6OXkW/QH9O/6zIULRRZCvyFJcpVijWK95WfKNEUTJR8lGao5SvVKp0QummUr8yRdlU2U+Zo7xUuUL5pPID5UEVhoqdSrhKtspalUMqV1V6VUmqpqoBqjzVAtW9qhdUuxg4hhHDj8FlrGLsY1xidKsR1czU2GoZasVqR9Ta1AbUVdUd1WPVF6hXqJ9R79DAaZhqsDWyNNZrHNe4r/F1ku4kn0n8SWsm1Uy6PemT5mRNb02+ZpFmreY9za9aTK0ArUytjVoNWs+08dqW2jO152vv1L6k3T9ZbbL7ZO7kosnHJz/WQXUsdSJ1Funs1bmhM6irpxukK9LdpntBt19PQ89bL0Nvs95ZvT59hr6nvkB/s/45/VdMdaYPM4tZxrzIHDDQMQg2yDXYY9BmMGRoZhhjuNKw1vCZEdWIZZRqtNmoxWjAWN94uvFi42rjxyYUE5ZJuslWk1aTT6ZmpnGmq00bTHvNNM3YZvlm1WZPzenmXuY55pXmdy2IFiyLTIsdFrcsUUsny3TLCsubVqiVs5XAaodV+xTCFNcpwimVUx5Y06x9rPOsq607bTRswmxW2jTYvJlqPDVx6saprVO/2zrZZtnus31ip2oXYrfSrsnunb2lPde+wv6uA90h0GGZQ6PDW0crR77jTseHTgyn6U6rnVqcvjm7OIuda5z7XIxdkl22uzxgqbEiWGtZV1wJrr6uy1xPu35xc3aTuh13+8Pd2j3T/ZB77zSzafxp+6Z1eRh6cDz2eHR4Mj2TPXd7dngZeHG8Kr1eeBt587z3e/f4WPhk+Bz2eeNr6yv2rfP95Ofmt8Sv2R/nH+Rf5N8WoBoQE1Ae8DzQMDAtsDpwIMgpaFFQczAhODR4Y/ADti6by65iD4S4hCwJuRhKC40KLQ99EWYZJg5rmo5OD5m+afrTGSYzhDMawiGcHb4p/FmEWUROxKmZxJkRMytmvoy0i1wc2RrFiJobdSjqY7Rv9ProJzHmMbkxLbFKsUmxVbGf4vzjSuI64qfGL4m/nqCdIEhoTCQlxibuTxycFTBry6zuJKekwqT7s81mL5h9dY72nKw5Z+YqzeXMPZFMSI5LPpQ8zAnnVHIGU9gp21MGuH7crdzXPG/eZl4f34Nfwu9J9UgtSe1N80jblNaX7pVemt4v8BOUC95mBGfsyviUGZ55IFOWFZdVm03OTs4+KVQVZgovztObt2Beu8hKVCjqyHHL2ZIzIA4V75cgktmSRqkaNijdyDXP/SG3M88zryLv8/zY+ScWqCwQLrix0HLhmoU9+YH5Py/CL+IuallssHjF4s4lPkv2LEWWpixtWWa0rGBZ9/Kg5QdXUFdkrvh1pe3KkpUfVsWtairQLVhe0PVD0A/VhYqF4sIHq91X7/oR/6Pgx7Y1Dmu2rflexCu6VmxbXFo8vJa79tpPdj+V/SRbl7qubb3z+p0biBuEG+5v9Np4sESlJL+ka9P0TfWbmZuLNn/YMnfL1VLH0l1bqVtzt3aUhZU1bjPetmHbcHl6+b0K34ra7Trb12z/tIO34/ZO7501u3R3Fe/6uluw++GeoD31laaVpXuJe/P2vtwXu6/1Z9bPVfu19xfv/3ZAeKDjYOTBi1UuVVWHdA6tr0arc6v7DicdvnXE/0hjjXXNnlqN2uKjcDT36KtjycfuHw893nKCdaLmF5Nfttcx6orqkfqF9QMN6Q0djQmN7SdDTrY0uTfVnbI5deC0wemKM+pn1p+lni04KzuXf26wWdTcfz7tfFfL3JYnF+Iv3L0482LbpdBLVy4HXr7Q6tN67orHldNX3a6evMa61nDd+Xr9Dacbdb86/VrX5txWf9PlZuMt11tN7dPaz972un3+jv+dy3fZd6/fm3Gv/X7M/YcPkh50POQ97H2U9ejt47zHQ0+WPyU8LXqm/Kz0uc7zyt8sfqvtcO440+nfeeNF1IsnXdyu179Lfh/uLnhJf1nao99T1Wvfe7ovsO/Wq1mvul+LXg/1F/5D5R/b35i/+eUP7z9uDMQPdL8Vv5W9W/te6/2BD44fWgYjBp9/zP449Knos9bng19YX1q/xn3tGZo/TBou+2bxrel76PensmyZTMQRc0ZHARy20NRUgHcHsPk4AYCBzRDUWWPz9aggY/8EowT/icdm8FFxBqjB1Mho5NcMcBRbpssBlLwBRsaiaG9AHRzk618iSXWwH4tFw6ZLwmeZ7L0uAKkJ4JtYJhvaIZN924cV+wigOWdsrh8RPewfY5YUUM3hxwW74e8yNvP/qce/axipwBH+rv8JgdMfq4rPexAAAACKZVhJZk1NACoAAAAIAAQBGgAFAAAAAQAAAD4BGwAFAAAAAQAAAEYBKAADAAAAAQACAACHaQAEAAAAAQAAAE4AAAAAAAAAkAAAAAEAAACQAAAAAQADkoYABwAAABIAAAB4oAIABAAAAAEAAACwoAMABAAAAAEAAACsAAAAAEFTQ0lJAAAAU2NyZWVuc2hvdBa14LkAAAAJcEhZcwAAFiUAABYlAUlSJPAAAAHWaVRYdFhNTDpjb20uYWRvYmUueG1wAAAAAAA8eDp4bXBtZXRhIHhtbG5zOng9ImFkb2JlOm5zOm1ldGEvIiB4OnhtcHRrPSJYTVAgQ29yZSA1LjQuMCI+CiAgIDxyZGY6UkRGIHhtbG5zOnJkZj0iaHR0cDovL3d3dy53My5vcmcvMTk5OS8wMi8yMi1yZGYtc3ludGF4LW5zIyI+CiAgICAgIDxyZGY6RGVzY3JpcHRpb24gcmRmOmFib3V0PSIiCiAgICAgICAgICAgIHhtbG5zOmV4aWY9Imh0dHA6Ly9ucy5hZG9iZS5jb20vZXhpZi8xLjAvIj4KICAgICAgICAgPGV4aWY6UGl4ZWxYRGltZW5zaW9uPjE3NjwvZXhpZjpQaXhlbFhEaW1lbnNpb24+CiAgICAgICAgIDxleGlmOlVzZXJDb21tZW50PlNjcmVlbnNob3Q8L2V4aWY6VXNlckNvbW1lbnQ+CiAgICAgICAgIDxleGlmOlBpeGVsWURpbWVuc2lvbj4xNzI8L2V4aWY6UGl4ZWxZRGltZW5zaW9uPgogICAgICA8L3JkZjpEZXNjcmlwdGlvbj4KICAgPC9yZGY6UkRGPgo8L3g6eG1wbWV0YT4KfSgnWwAAABxpRE9UAAAAAgAAAAAAAABWAAAAKAAAAFYAAABWAAAtY5SklA4AAC0vSURBVHgB7N0FsGS30QVgOczMZIeZGe0wM6PDzMx2mJnRDjMzbpiZeR1mZrx/f11/T8l377x9tvdO/FKjqtl5M5ek1tHp0y1pdrchSluXtQW2qAV2WwN4i/bcutppgTWA10DY0hZYA3hLd9+68msArzGwpS2wBvCW7r515dcAXmNgS1tgDeAt3X3ryq8BvMbAlrbAGsBbuvvWlV8DeI2BLW2BNYC3dPetK78G8BoDW9oCawBv6e5bV34N4DUGtrQF1gDe0t23rvwawGsMbGkLrAG8pbtvXfk1gNcY2NIWWAN4S3ffuvJrAK8xsKUtsAbwlu6+deWbTZ1zlk996lPDNa95zeGGN7zh8K1vfWvxqD/+8Y/DG9/4xuEEJzjBsP/++w9/+ctfFse2b98+3PzmNx+ufvWrDx//+MeH//znP3ns73//+/D5z39+ONvZzjbc6U53Gn71q18tjv3pT38anvrUpw6XutSlhmc+85nD3/72t7zmX//61+B+N7rRjYZLXOISw8Mf/vDhk5/85OD5dd/Fg+OPf//738PPf/7z4SUvecnwhCc8YXjnO985/PCHPxw8e6Piuh/96EfDAx7wgOG6173u8NnPfnan1/T3++tf/zp84xvfGF7zmtfkc9/znvcMv/3tb/tT8m911ravf/3r2d4rX/nKCztVm//5z38Orr/Sla403O52t0s71Y3+8Y9/DPvss89wnvOcZ3j7298+/PnPf17cV19d5zrXGa597Wtnm+sabXv+858/nPGMZxxe+cpXDr///e/rULb57ne/+3DBC14w7bo4sKI/ZgfwBz/4weEyl7nMcJWrXGX44he/uGgWIwDJUY5ylOwIAKzyzW9+M40IjO9///sXQNNBn/jEJ4Y99tgjAfmzn/1sccz9HvnIRw7nO9/5hsc85jEDQCju+9a3vnU46UlPOhz96Ecfjne84w2nOc1pstOf+9zn5qDqwem6D3/4w8O5z33uPNd1ZznLWbJjn/a0pw1f+MIXdgC/QfK9731vuMc97pED8hjHOMZwhStcYfjYxz62qEe1rd6B4je/+c3woQ99aHjIQx6SNjrd6U43nOQkJ8l73PjGN0571SADSgPk1a9+9eDYGc5whsWzjn/846cNf/GLX+TtnfvmN795uNjFLpbE8dOf/rQem+C/853vPHjW61//+myLg+qjry53uctlXb773e8urnHscY973HDyk5982G+//bLedVC7b3nLW6aNtm3bVl+v7H12AGsUIGIDnV8F4DDvkY50pOFJT3pSAq2OYResffGLX3x473vfuwAp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"/>
              </defs>
            </svg>
            <h3 class="my-4"> [[(step !== 'verified' ? 'Verify with' : 'Disconnect from')]] Idena </h3>
          </div>

          <template v-if="step === 'connect'">
            <idena-verify-modal-content>
              <div v-if="initiated && !service.is_verified" class="text-right mt-5">
                <span style="color:orange"><i class="fal fa-exclamation-circle"></i> Pending Validation</span>
              </div>
              <b-button @click="connectIdena" variant="primary" :class="'btn btn-primary px-5 float-right ml-2 ' + (!initiated ? 'mt-5' : 'mt-2')">Verify with Idena</b-button>
              <b-button v-if="initiated" @click="checkApi(service.check_status_url, true)" variant="primary" :class="'btn btn-primary px-5 float-right ' + (!initiated ? 'mt-5' : 'mt-2')">
                <b-spinner small v-if="awaitingResponse" type="grow" class="ml-n4 position-absolute spinner-grow spinner-grow-sm"></b-spinner>
                Check Status
              </b-button>
            </idena-verify-modal-content>
          </template>

          <template v-if="step === 'connected'">
            <idena-verify-modal-content>
              <div class="alert alert-primary mt-5">
                <a href="https://www.idena.io/gitcoin" target="blank">Take part</a> in the Idena validation ceremony [[ service.next_validation ]] GMT
              </div>
              <div v-if="!service.is_verified" class="text-right mt-5">
                <span style="color:orange"><i class="fal fa-exclamation-circle"></i> Pending Validation</span>
              </div>
              <b-button @click="checkApi(service.logout_url)" variant="primary" class="btn btn-primary mt-2 px-5 float-right ml-2">Disconnect</b-button>
              <b-button @click="checkApi(service.check_status_url, true)" variant="primary" class="btn btn-primary mt-2 px-5 float-right">
                <b-spinner small v-if="awaitingResponse" type="grow" class="ml-n4 position-absolute spinner-grow spinner-grow-sm"></b-spinner>
                Check Status
              </b-button>
            </idena-verify-modal-content>
          </template>

          <template v-if="step === 'verified'">
            <idena-verify-modal-content>
              <div class="text-right mt-5">
                Status: [[ service._status ]]
              </div>
              <b-button @click="checkApi(service.logout_url)" variant="primary" class="btn btn-primary mt-2 px-5 float-right ml-2">Disconnect</b-button>
              <b-button @click="checkApi(service.check_status_url, true)" variant="primary" class="btn btn-primary mt-2 px-5 float-right">
                <b-spinner small v-if="awaitingResponse" type="grow" class="ml-n4 position-absolute spinner-grow spinner-grow-sm"></b-spinner>
                Check Status
              </b-button>
            </idena-verify-modal-content>
          </template>

        </div>
      </template>
    </b-modal>`,

  methods: {
    dismissVerification() {
      this.$emit('modal-dismissed');
    },
    connectIdena() {
      // open idena for the rest of the process to take place
      window.open(this.service.login_url, '_blank');
      // assume connected - check properly on close
      this.initiated = true;
    },
    async checkApi(url, checkingStatus) {
      if (checkingStatus) {
        this.awaitingResponse = true;
      }
      try {
        const response = await apiCall(url);

        if (response.ok) {
          this.forceStep = false;
          this.service = Object.assign(this.service, response);
        }
      } catch (err) {
        console.log(err);
      } finally {
        if (!checkingStatus) {
          this.dismissVerification();
        } else if (!this.service.is_verified) {
          _alert('Pending Validation...', 'danger', 2000);
        }
        this.awaitingResponse = false;
        if (url === this.service.logout_url) {
          _alert('You have successfully disconnected from Idena.', 'success', 3000);
        }
      }
    }
  }
});

Vue.component('duniter-verify-modal', {
  delimiters: [ '[[', ']]' ],
  data: function() {
    return {
      validationStep: 'validate-duniter',
      validationError: '',
      publicKey: ''
    };
  },
  computed: {
  },
  props: {
    showValidation: {
      type: Boolean,
      required: false,
      'default': false
    }
  },
  template: `
    <b-modal id="duniter-modal" @hide="dismissVerification()" :visible="showValidation" center hide-header hide-footer>
      <template v-slot:default="{ hide }">
        <div class="mx-5 mt-5 mb-4 text-center">
          <div class="mb-3">
            <h1 class="font-bigger-4 font-weight-bold">Verify your Duniter account</h1>
            <p>
              Duniter is a free software for free currencies: a P2P, <a href="https://en.wikipedia.org/wiki/Web_of_trust">Web of Trust</a> & <a href="https://en.wikipedia.org/wiki/Social_credit">Universal Dividend system.</a>
              <p class="mb-4">
                <a href="https://duniter.org/en/introduction/" target=_blank>Learn more.</a>
              </p>
            </p>
            <div>
              <h2 class="font-bigger-4 font-weight-bold"> You need to have these requirements:</h2>
              <ol>
                <li>Let's check if there is already a record with your account.</li>
                <li>Link to your gitcoin account in your Duniter record </li>
                <li>If you are a qualified Duniter member</li>
              </ol>
            </div>
          </div>
          <div v-if="validationStep === 'validate-duniter' || validationStep == 'perform-validation'">
            <p class="mb-4">
              You fulfill all the requirements, if you just need to click on validate to confirm that your duniter account is valid
            </p>
            <b-button @click="clickedValidate" :disabled="validationStep === 'validate-duniter'" class="btn-gc-blue mt-3 mb-2">
              <b-spinner small v-if="validationStep === 'validate-duniter'" type="grow"></b-spinner>
              Verify
            </b-button>
            <div v-if="validationError !== ''" style="color: red">
              <small>[[validationError]]</small>
            </div>
            <br />
            <a href="" v-if="validationError !== ''" @click="clickedGoBack">
              Go Back
            </a>
          </div>
          <div v-if="validationStep === 'validation-complete'">
            Your Duniter verification was successful. Thank you for helping make Gitcoin more sybil resistant!
            <a href="" class="btn btn-gc-blue px-5 mt-3 mb-2 mx-2" role="button" style="font-size: 1.3em">Done</a>
          </div>
        </div>
      </template>
    </b-modal>`,
  methods: {
    dismissVerification() {
      this.showValidation = false;
    },
    clickedGoBack(event) {
      event.preventDefault();
      this.validationStep = 'validate-duniter';
      this.validationError = '';
    },
    clickedValidate(event) {
      event.preventDefault();

      this.validationError = '';

      this.validationStep = 'perform-validation';
      this.getUserHandle();
      this.verifyDuniter();
    },
    getUserHandle() {
      this.githubHandle = trustHandle;
    },
    verifyDuniter() {
      const csrfmiddlewaretoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
      const headers = {'X-CSRFToken': csrfmiddlewaretoken};
      const payload = JSON.stringify({
        'gitcoin_handle': this.githubHandle
      });
      const verificationRequest = fetchData('/api/v0.1/profile/verify_user_duniter', 'POST', payload, headers);

      $.when(verificationRequest).then(response => {
        if (response.ok) {
          this.validationStep = 'validation-complete';
        } else {
          this.validationError = response.msg;
          this.validationStep = 'validate-duniter';
        }

      }).catch((_error) => {
        this.validationError = 'There was an error; please try again later';
        this.validationStep = 'validate-duniter';
      });
    }
  }
});

Vue.component('active-trust-manager', {
  delimiters: [ '[[', ']]' ],
  data() {
    return {
      visibleModal: 'none',
      console: console,
      round_start_date: parseMonthDay(document.round_start_date),
      round_end_date: parseMonthDay(document.round_end_date),
      roadmap: document.roadmap || [],
      services: document.services || [],
      coming_soon: document.coming_soon || []
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
    }
  }
});

Vue.component('active-trust-row-template', {
  delimiters: [ '[[', ']]' ],
  data() {
    return {};
  },
  props: {
    iconType: {
      type: String, // 'image' or 'markup'
      required: false,
      'default': 'markup'
    },
    iconPath: {
      // path to image file if iconType is 'image'
      type: String,
      required: false
    },
    title: {
      type: String,
      required: true
    },
    matchPercent: {
      type: Number,
      required: true
    },
    isVerified: {
      type: Boolean,
      required: true
    },
    buttonText: {
      type: String,
      required: false,
      'default': 'Verify'
    }
  },
  methods: {
    didClick(event) {
      event.preventDefault();
      this.$emit('verify-button-pressed');
    },
    hasVerifySlot() {
      return !!this.$slots.verify;
    }
  },
  template: `
    <div class="row mb-4 pb-4" style="border-bottom: 1px solid #eee;">
      <div class="col-12 col-md-1 mx-auto text-center">
        <div v-if="iconType === 'markup'">
          <slot name="icon"></slot>
        </div>
        <div v-if="iconType === 'image'">
          <img :src="[[iconPath]]" alt="logo" class="img-fluid">
        </div>
      </div>
      <div class="col-12 col-md-7 mb-3 mb-md-0">
        <div class="font-weight-bold">
          [[title]]
        </div>
        <div>
          <slot name="description"></slot>
        </div>
      </div>
      <div class="col-6 col-md-2 text-center">
        <div class="font-weight-bold">
          +[[matchPercent]]%
        </div>
        <div style="color:grey">
          <small>Grants Match Bonus</small>
        </div>
      </div>
      <div class="col-6 col-md-2">
        <template v-if="hasVerifySlot()">
          <slot name="verify"></slot>
        </template>
        <template v-else>
          <template v-if="isVerified === true">
            <span style="color:limegreen"><i class="fas fa-check"></i> Verified</span>
          </template>
          <template v-else>
            <a @click="didClick" href="" role="button" class="btn btn-primary text-nowrap">[[buttonText]]</a>
          </template>
        </template>
      </div>
    </div>`
});

Vue.component('inactive-trust-row-template', {
  delimiters: [ '[[', ']]' ],
  props: {
    service: {
      type: String,
      required: true
    },
    when: {
      type: String,
      required: true
    }
  },
  template: `
    <!-- MORE ROW -->
    <div class="row mb-4">
      <div class="col-12 col-md-1 mx-auto text-center pt-1">
        <span style="color: #dddddd">
          <i class="fas fa-fingerprint fa-3x" aria-hidden="true"></i>
        </span>
      </div>
      <div class="col-12 col-md-7 mb-3 mb-md-0">
        <div class="font-weight-bold">
          [[ service ]]
        </div>
        <div>
          Tentatively [[when]]
        </div>
      </div>
      <div class="col-6 col-md-2 text-center">
        <div class="font-weight-bold">
          +?%
        </div>
        <div style="color:grey">
          <small>Grants Match Bonus</small>
        </div>
      </div>
      <div class="col-6 col-md-2 text-center">
        <div>
          🚧
        </div>
        <div style="color:grey">
          <small>[[when]]</small>
        </div>
      </div>
    </div>`
});

Vue.component('ens-verify-modal', {
  delimiters: [ '[[', ']]' ],
  data: function() {
    return {
      ethAddress: '',
      static_url: document.contxt.STATIC_URL,
      ensDomain: '',
      validationError: '',
      validationErrorMsg: '',
      url: '',
      forceStep: false,
      verificationEthAddress: '',
      awaitingResponse: false
    };
  },
  props: {
    showValidation: {
      type: Boolean,
      required: false,
      'default': false
    },
    validationStep: {
      required: true
    },
    service: {
      type: Object,
      required: true
    }
  },
  computed: {
    step() {
      return this.forceStep || this.validationStep;
    }
  },
  watch: {
    showValidation: function() {
      if (this.showValidation === true && typeof web3 !== 'undefined' && !this.service.is_verified) {
        this.pullEthAddress();
      }
    }
  },
  template: `
    <b-modal id="ens-modal" @hide="dismissVerification()" :visible="showValidation" size="lg" body-class="p-0" center hide-header hide-footer>
      <template v-slot:default="{ hide }">
        <div class="modal-content p-0">
          <div class="top rounded-top p-2 text-center" style="background: #ECE9FF;">
            <div class="w-100">
              <button @click="dismissVerification()" type="button" class="close position-absolute mt-2" style="right: 1rem" data-dismiss="modal" aria-label="Close">
                <span aria-hidden="true">&times;</span>
              </button>
            </div>
            <div class="bg-white d-flex mt-4 mx-auto p-1 rounded-circle" style="width: 74px; height: 74px;">
              <img class="m-auto" src="/static/v2/images/project_logos/ens.svg" alt="ENS Logo" width="45">
            </div>
            <h3 class="my-4"> [[(step !== 'disconnect' ? 'Verify with' : 'Disconnect from')]] ENS </h3>
          </div>
          <div class="font-smaller-1 line-height-3 spacer-px-4 spacer-px-lg-6 spacer-py-5">

            <div v-if="!service.is_verified && step !== 'disconnect'">
              <div class="mb-3">
                <p>
                  ENS is a name service built on Ethereum. It offers a secure and decentralized way to address resources using human-readable names.
                  <p class="mb-4">
                    <a href="https://ens.domains/about">Learn more.</a>
                  </p>
                </p>
                <div>
                  <div class="mb-4 font-weight-semibold font-subheader">Please complete the following requirements:</div>
                  <ol class="text-left pl-0" style="list-style: none">
                    <li class="mb-3">
                      <span :class="\`mr-2 fas fa-\${step > 1 ? 'check check gc-text-green' : 'times gc-text-pink'}\`"></span>  Setup your address.
                      <input v-model="verificationEthAddress" class="form-control" type="text" @keyup="onchange">
                      <a href="#" @click.prevent.stop="pullEthAddress()">Connect with ENS</a><br>
                    </li>
                    <li class="mb-3"><span :class="\`mr-2 fas fa-\${step > 2 ? 'check gc-text-green' : 'times gc-text-pink'}\`"></span> Your address has an ENS domain associated, [[ ensDomain ? '' : 'you can get one' ]] <a :href="\`https://app.ens.domains/\${ensDomain ? 'name/'+ ensDomain : ''}\`">[[ ensDomain ? ensDomain  : 'here' ]]</a>.</li>
                    <li class="mb-3"><span :class="\`mr-2 fas fa-\${step > 4 ? 'check gc-text-green' : 'times gc-text-pink'}\`"></span> Your address should match with the address associated to the ENS domain.</li>
                  </ol>
                </div>
              </div>
              <div class="mb-4">
                <p class="mb-4" v-if="validationError !== false">
                  [[ validationErrorMsg ]] <a v-if="url" :href="url">[[url]]</a>
                </p>
                <p class="mb-4" v-if="validationError === false">
                  You fulfill all the requirements, just click on verify to confirm that your ENS account is valid
                </p>
                <b-button v-if="validationError === false" @click="verifyENS" variant="primary" class="btn btn-primary px-5 float-right mt-5">
                  <b-spinner small v-if="awaitingResponse" type="grow" class="ml-n4 position-absolute spinner-grow spinner-grow-sm"></b-spinner>
                  Verify
                </b-button>
                <div v-if="validationError & validationErrorMsg !== ''" style="color: red">
                  <small>[[validationErrorMsg]]</small>
                </div>
                <br />
                <a href="" v-if="validationError" @click.f="dismissVerification()">
                  Go Back
                </a>
              </div>
            </div>
            <div v-if="service.is_verified && !validationError && step !== 'disconnect'">
              <div>Your ENS verification was successful. Thank you for helping make Gitcoin more sybil resistant!</div>
              <b-button @click="dismissVerification" variant="primary" class="btn btn-primary mt-5 px-5 float-right">
                Done
              </b-button>
            </div>
            <div v-if="step === 'disconnect'">
              <div class="w-100">
                <p>
                  <div>
                    Are you sure you want to disconnect your ENS verification?
                  </div>
                  <b-button @click="disconnectENS" variant="primary" class="btn btn-primary mt-5 px-5 float-right">
                    <b-spinner small v-if="awaitingResponse" type="grow" class="ml-n4 position-absolute spinner-grow spinner-grow-sm"></b-spinner>
                    Yes, disconnect
                  </b-button>
                </p>
              </div>
            </div>
          </div>
        </div>
      </template>
    </b-modal>`,
  methods: {
    dismissVerification() {
      this.$emit('modal-dismissed');
      setTimeout(() => {
        this.forceStep = false;
      }, 1000);
    },
    verifyENS() {
      const csrfmiddlewaretoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
      const headers = {'X-CSRFToken': csrfmiddlewaretoken};
      const data = {};

      if (typeof web3 !== 'undefined' && web3.utils.isAddress(this.verificationEthAddress)) {
        data['verification_address'] = this.verificationEthAddress;
      }

      const verificationRequest = fetchData(`/api/v0.1/profile/${trustHandle}/verify_user_ens`, 'POST', data, headers);

      this.onResponse(verificationRequest);
    },
    onchange() {
      if (!this.service.is_verified && typeof web3 !== 'undefined' && web3.utils.isAddress(this.verificationEthAddress)) {
        this.checkENSValidation();
      }
    },
    onResponse(verificationRequest) {
      let vm = this;

      $.when(verificationRequest).then(response => {
        vm.validationError = response.error;
        vm.validationErrorMsg = response.msg;
        vm.service.is_verified = response.data.verified;
        vm.forceStep = response.data.step;
        vm.url = response.data.url;
        vm.verificationEthAddress = response.data.address;
        vm.ensDomain = response.data.ens_domain;
      });
    },
    checkENSValidation() {
      let vm = this;
      const csrfmiddlewaretoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
      const headers = {'X-CSRFToken': csrfmiddlewaretoken};
      const data = {};

      if (typeof web3 !== 'undefined' && web3.utils.isAddress(this.verificationEthAddress)) {
        data['verification_address'] = this.verificationEthAddress;
      }

      const verificationRequest = fetchData(`/api/v0.1/profile/${trustHandle}/verify_user_ens`, 'GET', data, headers);

      this.onResponse(verificationRequest);
    },
    getEthAddress() {
      const accounts = web3.eth.getAccounts();

      $.when(accounts).then((result) => {
        this.verificationEthAddress = result[0];
        this.onchange();
        this.showValidation = true;
      }).catch((_error) => {
        this.validationError = 'Error getting ethereum accounts';
        this.showValidation = true;
      });
    },
    connectWeb3Wallet() {
      this.showValidation = false;
      onConnect().then((result) => {
        this.getEthAddress();
      }).catch((_error) => {
        this.validationError = 'Error connecting ethereum accounts';
        this.showValidation = true;
      });
    },
    pullEthAddress() {
      // Prompt web3 login if not connected
      if (!provider) {
        this.connectWeb3Wallet();
      } else {
        this.getEthAddress();
      }
    },
    async disconnectENS() {
      this.awaitingResponse = true;
      this.forceStep = 'disconnect';
      try {
        const response = await apiCall(`/api/v0.1/profile/${trustHandle}/disconnect_user_ens`);

        if (response.ok) {
          this.service = Object.assign(this.service, response);
        }
      } catch (err) {
        console.log(err);
      } finally {
        this.awaitingResponse = false;
        this.dismissVerification();
        _alert('You have successfully disconnected from ENS.', 'success', 3000);
      }
    }
  }
});

Vue.component('google-verify-modal', {
  delimiters: [ '[[', ']]' ],
  data: function() {
    return {
      forceStep: false,
      awaitingResponse: false
    };
  },
  props: {
    showValidation: {
      type: Boolean,
      required: false,
      'default': false
    },
    validationStep: {
      type: String,
      required: true
    },
    service: {
      type: Object,
      required: true
    }
  },
  computed: {
    step() {
      return this.forceStep || this.validationStep;
    }
  },
  template: `
    <b-modal id="google-modal" @hide="dismissVerification()" :visible="showValidation" size="lg" body-class="p-0" center hide-header hide-footer>
      <template v-slot:default="{ hide }">
        <div class="modal-content p-0">
          <div class="top rounded-top p-2 text-center" style="background: #FFF0EB;">
            <div class="w-100">
              <button @click="dismissVerification()" type="button" class="close position-absolute mt-2" style="right: 1rem" data-dismiss="modal" aria-label="Close">
                <span aria-hidden="true">&times;</span>
              </button>
            </div>
            <div class="bg-white d-flex mt-4 mx-auto p-1 rounded-circle" style="width: 74px; height: 74px;">
              <img width="41" height="40" class="m-auto" src="/static/v2/images/project_logos/google.png">
            </div>
            <h3 class="my-4"> [[(step !== 'disconnect' ? 'Verify with' : 'Disconnect from')]] Google </h3>
          </div>
          <div class="font-smaller-1 line-height-3 spacer-px-4 spacer-px-lg-6 spacer-py-5">

            <template v-if="step === 'connect'">
              <p>
                Verify your Google account.
              </p>
              <b-button @click="verifyGoogle" variant="primary" class="btn btn-primary px-5 float-right mt-5">
                <b-spinner small v-if="awaitingResponse" type="grow" class="ml-n4 position-absolute spinner-grow spinner-grow-sm"></b-spinner>
                Connect Google
              </b-button>
            </template>

            <template v-if="step === 'disconnect'">
              <div class="w-100">
                <p>
                  <div>
                    Are you sure you want to disconnect your Google verification?
                  </div>
                  <b-button @click="disconnectGoogle" variant="primary" class="btn btn-primary mt-5 px-5 float-right">
                    <b-spinner small v-if="awaitingResponse" type="grow" class="ml-n4 position-absolute spinner-grow spinner-grow-sm"></b-spinner>
                    Yes, disconnect
                  </b-button>
                </p>
              </div>
            </template>
          </div>
        </div>
      </template>
    </b-modal>`,
  methods: {
    dismissVerification() {
      this.$emit('modal-dismissed');
      setTimeout(() => {
        this.forceStep = false;
      }, 1000);
    },
    verifyGoogle() {
      const form = document.createElement('form');
      const csrf = document.createElement('input');

      form.method = 'POST';
      form.action = `/api/v0.1/profile/${trustHandle}/request_verify_google`;

      csrf.value = document.querySelector('[name=csrfmiddlewaretoken]').value;
      csrf.name = 'csrfmiddlewaretoken';

      form.appendChild(csrf);

      document.body.appendChild(form);

      form.submit();
    },
    async disconnectGoogle() {
      this.awaitingResponse = true;
      this.forceStep = 'disconnect';
      try {
        const response = await apiCall(`/api/v0.1/profile/${trustHandle}/disconnect_user_google`);

        if (response.ok) {
          this.service = Object.assign(this.service, response);
        }
      } catch (err) {
        console.log(err);
      } finally {
        this.awaitingResponse = false;
        this.dismissVerification();
        _alert('You have successfully disconnected from Google.', 'success', 3000);
      }
    }
  }
});

Vue.component('facebook-verify-modal', {
  delimiters: [ '[[', ']]' ],
  data: function() {
    return {
      forceStep: false,
      awaitingResponse: false
    };
  },
  props: {
    showValidation: {
      type: Boolean,
      required: false,
      'default': false
    },
    validationStep: {
      type: String,
      required: true
    },
    service: {
      type: Object,
      required: true
    }
  },
  computed: {
    step() {
      return this.forceStep || this.validationStep;
    }
  },
  template: `
    <b-modal id="facebook-modal" @hide="dismissVerification()" :visible="showValidation" size="lg" body-class="p-0" center hide-header hide-footer>
      <template v-slot:default="{ hide }">
        <div class="modal-content p-0">
          <div class="top rounded-top p-2 text-center" style="background: #FFF0EB;">
            <div class="w-100">
              <button @click="dismissVerification()" type="button" class="close position-absolute mt-2" style="right: 1rem" data-dismiss="modal" aria-label="Close">
                <span aria-hidden="true">&times;</span>
              </button>
            </div>
            <div class="bg-white d-flex mt-4 mx-auto p-1 rounded-circle" style="width: 74px; height: 74px;">
              <i class="fab fa-facebook fa-3x m-auto" style="color: rgb(24, 119, 242);"></i>
            </div>
            <h3 class="my-4"> [[(step !== 'disconnect' ? 'Verify with' : 'Disconnect from')]] Facebook </h3>
          </div>
          <div class="font-smaller-1 line-height-3 spacer-px-4 spacer-px-lg-6 spacer-py-5">
            <template v-if="step === 'connect'">
              <p>
                Verify your Facebook account.
              </p>
              <b-button @click="verifyFacebook" variant="primary" class="btn btn-primary px-5 float-right mt-5">
                <b-spinner small v-if="awaitingResponse" type="grow" class="ml-n4 position-absolute spinner-grow spinner-grow-sm"></b-spinner>
                Connect Facebook
              </b-button>
            </template>

            <template v-if="step === 'disconnect'">
              <div class="w-100">
                <p>
                  <div>
                    Are you sure you want to disconnect your Facebook verification?
                  </div>
                  <b-button @click="disconnectFacebook" variant="primary" class="btn btn-primary mt-5 px-5 float-right">
                    <b-spinner small v-if="awaitingResponse" type="grow" class="ml-n4 position-absolute spinner-grow spinner-grow-sm"></b-spinner>
                    Yes, disconnect
                  </b-button>
                </p>
              </div>
            </template>
          </div>
        </div>
      </template>
    </b-modal>`,

  methods: {
    dismissVerification() {
      this.$emit('modal-dismissed');
      setTimeout(() => {
        this.forceStep = false;
      }, 1000);
    },
    verifyFacebook() {
      const form = document.createElement('form');
      const csrf = document.createElement('input');

      form.method = 'POST';
      form.action = `/api/v0.1/profile/${trustHandle}/request_verify_facebook`;

      csrf.value = document.querySelector('[name=csrfmiddlewaretoken]').value;
      csrf.name = 'csrfmiddlewaretoken';

      form.appendChild(csrf);

      document.body.appendChild(form);

      form.submit();
    },
    async disconnectFacebook() {
      this.awaitingResponse = true;
      this.forceStep = 'disconnect';
      try {
        const response = await apiCall(`/api/v0.1/profile/${trustHandle}/disconnect_user_facebook`);

        if (response.ok) {
          this.service = Object.assign(this.service, response);
        }
      } catch (err) {
        console.log(err);
      } finally {
        this.awaitingResponse = false;
        this.dismissVerification();
        _alert('You have successfully disconnected from Facebook.', 'success', 3000);
      }
    }
  }
});

Vue.component('qd-modal', {
  delimiters: [ '[[', ']]' ],
  data: function() {
    return {
      validationError: '',
      forceStep: false,
      awaitingResponse: false
    };
  },
  props: {
    showValidation: {
      type: Boolean,
      required: false,
      'default': false
    },
    service: {
      type: Object,
      required: true
    }
  },
  computed: {
    step() {
      return this.forceStep || this.validationStep;
    }
  },
  template: `
    <b-modal id="twitter-modal" @hide="dismissVerification()" :visible="showValidation" size="lg" body-class="p-0" center hide-header hide-footer>
      <template v-slot:default="{ hide }">
        <div class="modal-content p-0">
          <div class="top rounded-top p-2 text-center" style="background: #0e0333;">
            <div class="w-100">
              <button @click="dismissVerification()" type="button" class="close position-absolute mt-2 text-white" style="right: 1rem" data-dismiss="modal" aria-label="Close">
                <span aria-hidden="true">&times;</span>
              </button>
            </div>
            <div class="bg-white d-flex mt-4 mx-auto p-1 rounded-circle" style="width: 74px; height: 74px;">
              <img class="m-auto w-100" src="/static/v2/images/quadraticlands/mission/diplomacy.svg" alt="QL Diplomacy Logo">
            </div>
            <h3 class="text-white my-4"> Verify with Quadratic Diplomacy </h3>
          </div>
          <div class="font-smaller-1 line-height-3 spacer-px-4 spacer-px-lg-6 spacer-py-5">
            <div class="mb-4 text-left">
              <p class="mb-4 font-subheader text-left">
                Use your GTC to strengthen Gitcoin Grants!
              </p>
              <p class="mb-4 font-subheader text-left">
                WHY: The Foundation of Gitcoin Grants is Quadratic Funding, which is itself dependant upon sybil & fraud resistence.
              </p>

              <button @click="goToVerification" role="button" class="btn btn-primary mb-2 mt-5 px-5 float-right">
                Verify Now
              </button>
            </div>
          </div>
        </div>
      </template>
    </b-modal>`,
  methods: {
    dismissVerification() {
      this.$emit('modal-dismissed');
      setTimeout(() => {
        this.forceStep = false;
      }, 1000);
    },
    goToVerification() {
      window.open('/quadraticlands/mission/diplomacy', '_blank');
      this.dismissVerification();
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

  $(document).on('keyup', 'input[name=telephone]', function(e) {
    var number = $(this).val();

    if (number[0] != '+') {
      number = '+' + number;
      $(this).val(number);
    }
  });

  $(document).on('click', '#verify_offline', function(e) {
    $(this).remove();
    $('#verify_offline_or').remove();
    $('#verify_offline_target').css('display', 'block');
  });

  jQuery.fn.shake = function(interval, distance, times) {
    interval = typeof interval == 'undefined' ? 100 : interval;
    distance = typeof distance == 'undefined' ? 10 : distance;
    times = typeof times == 'undefined' ? 3 : times;
    var jTarget = $(this);

    jTarget.css('position', 'relative');
    for (var iter = 0; iter < (times + 1); iter++) {
      jTarget.animate({ top: ((iter % 2 == 0 ? distance : distance * -1))}, interval);
    }
    return jTarget.animate({ top: 0}, interval);
  };

  $(document).on('click', '#gen_passport', function(e) {
    e.preventDefault();
    if (document.web3network != 'rinkeby' && document.web3network != 'mainnet') {
      _alert('Please connect your web3 wallet to mainnet + unlock it', 'danger', 1000);
      return;
    }
    const accounts = web3.eth.getAccounts();

    $.when(accounts).then((result) => {
      const ethAddress = result[0];
      let params = {
        'network': document.web3network,
        'coinbase': ethAddress
      };

      $.get('/passport/', params, function(response) {
        let status = response['status'];

        if (status == 'error') {
          _alert(response['msg'], 'danger', 5000);
          return;
        }

        let contract_address = response.contract_address;
        let contract_abi = response.contract_abi;
        let nonce = response.nonce;
        let hash = response.hash;
        let tokenURI = response.tokenURI;
        var passport = new web3.eth.Contract(contract_abi, contract_address);

        var callback = function(err, txid) {
          if (err) {
            _alert(err, 'danger', 5000);
            return;
          }
          let url = 'https://etherscan.io/tx/' + txid;
          var html = `
            <strong>Woo hoo!</strong> - Your passport is being generated.  View the transaction <a href='` + url + `' target=_blank>here</a>.
            <br><br>
            <strong>Whats next?</strong>
            <br>
            1. Please add the token contract address (` + contract_address + `) as a token to your wallet provider.
            <br>
            2. Use the Trust you've built up on Gitcoin across the dWeb!  Learn more at <a target=_blank href=https://proofofpersonhood.com>proofofpersonhood.com</a>
          `;

          $('.modal-body .subbody').html(html);
          $('.modal-dialog').shake();
        };

        passport.methods.createPassport(tokenURI, hash, nonce).send({from: ethAddress}, callback);
      });

    });
  });

  const passportCredential = (() => {

    const _3BOX_SPACE = 'gitcoin';
    const _3BOX_FIELD = 'popp';

    let ethAddress;
    let ethProvider;
    let credential;
    let verifier;

    const params = () => ({
      'network': document.web3network,
      'coinbase': ethAddress
    });

    const downloadLink = () => {
      const str = JSON.stringify(credential, null, 2);
      const encoded = encodeURIComponent(str);

      return `data:application/json;charset=utf-8,${encoded}`;
    };

    const baseContent = () => {
      const formatted = JSON.stringify(credential, null, 2);
      const { issuer, credentialSubject, passport } = credential;

      const value = passport['personhood_score'];
      // substring(12) removes 'did:pkh:eth:'
      const address = credentialSubject['id'].substring(12);

      const style = 'style="margin: 0.5rem;width: 100%;"';
      const href = downloadLink();

      const verifiableCredential = '<a href="https://www.w3.org/TR/vc-data-model/" target="_blank">W3C Verifiable Credential</a>';
      const did = '<a href="https://www.w3.org/TR/did-core/" target="_blank">DID</a>';

      return `
        <p>This is a ${verifiableCredential} that contains your trust bonus signed by the ${did} <strong>${issuer}</strong>.</p>
        <p>Your trust bonus score is <strong>${value}</strong> for the Ethereum address <strong>${address}</strong>.</p>
        <textarea style="width: 100%;margin: 0 0 1rem 0;padding: 1rem;" rows="4" class="text-monospace" readonly>${formatted}</textarea>
        <div style="display: flex;flex-direction: column;">
          <div style="display: flex;">
            <button ${style} type="button" class="btn btn-info" id="vc-copy">Copy</button>
            <a ${style} href="${verifier}" target="_blank" class="btn btn-success">Verify</a>
            <a ${style} href="${href}" class="btn btn-link" download="gitcoin-popp-vc.json"">Download</a>
          </div>
          <button ${style} type="button" class="btn btn-primary" id="vc-3box">Save to 3Box</button>
        </div>
      `;
    };

    const messages = {
      auth: [
        'Authenticate with 3Box',
        'Authenticating with 3Box',
        'Authenticated with 3Box'
      ],
      storage: [
        `Open '${_3BOX_SPACE}' storage space on 3Box`,
        `Opening '${_3BOX_SPACE}' storage space on 3Box`,
        `Opened '${_3BOX_SPACE}' storage space on 3Box`
      ],
      variable: [
        `Save passport credential as '${_3BOX_FIELD}'`,
        `Saving passport credential as '${_3BOX_FIELD}'`,
        `Saved passport credential as '${_3BOX_FIELD}'`
      ]
    };

    const getMessage = (source, state) => {
      if (state === true) {
        return '<s>' + source[2] + '</s> ✓';
      } else if (state === false) {
        return '<strong>' + source[1] + '</strong>';
      }
      return '<em>' + source[0] + '</em>';
    };

    const get3BoxContent = (auth, storage, variable) => {
      let list = '<ul>';

      list += '<li>';
      list += getMessage(messages.auth, auth);
      list += '</li>';

      list += '<li>';
      list += getMessage(messages.storage, storage);
      list += '</li>';

      list += '<li>';
      list += getMessage(messages.variable, variable);
      list += '</li>';

      list += '</ul>';

      return `
        <div>
          <p><strong>3Box integration:</strong> you can save a POPP credential to 3Box.</p>
          ${list}
        </div>
      `;
    };

    const vcPassport = () => {
      if (document.web3network != 'rinkeby' && document.web3network != 'mainnet') {
        _alert('Please connect your web3 wallet to mainnet + unlock it', 'danger', 1000);
        return;
      }

      const accounts = web3.eth.getAccounts();

      $.when(accounts).then((result) => {
        ethAddress = result[0];
        ethProvider = web3.currentProvider;

        $.get('/passport-vc', params(), async function(response) {
          let status = response['status'];

          if (status == 'error') {
            _alert(response['msg'], 'danger', 5000);
            return;
          }

          credential = response.vc;
          verifier = response.verifier;

          $('.modal-body').html(baseContent());
        });
      });
    };

    const vc3Box = async() => {
      const modal = $('.modal-body');
      const base = baseContent();

      modal.html(`${base} <hr /> ${get3BoxContent(false)}`);

      const storageBox = await Box.openBox(ethAddress, ethProvider);

      modal.html(`${base} <hr /> ${get3BoxContent(true, false)}`);

      const storageSpace = await storageBox.openSpace(_3BOX_SPACE);

      await storageSpace.syncDone;

      modal.html(`${base} <hr /> ${get3BoxContent(true, true, false)}`);

      const json = JSON.stringify(credential);

      await storageSpace.public.set(_3BOX_FIELD, json);

      modal.html(`${base} <hr /> ${get3BoxContent(true, true, true)}`);

      _alert('Your passport has been uploaded to 3Box', 'success', 5000);
    };

    const vcCopy = () => {
      const str = JSON.stringify(credential, null, 2);

      navigator.clipboard.writeText(str);
    };

    return { vcPassport, vc3Box, vcCopy };
  })();

  $(document).on('click', '#vc-passport', passportCredential.vcPassport);
  $(document).on('click', '#vc-3box', passportCredential.vc3Box);
  $(document).on('click', '#vc-copy', passportCredential.vcCopy);

});
