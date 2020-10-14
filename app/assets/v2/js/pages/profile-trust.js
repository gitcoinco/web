let hasGeneratedBrightIdQRCode = false;

let brightIDCalls = [];

let show_brightid_connect_modal = function(brightid_uuid) {
  const brightIdLink = `https://app.brightid.org/link-verification/http:%2f%2fnode.brightid.org/Gitcoin/${brightid_uuid}`;
  const brightIdAppLink = `brightid://link-verification/http:%2f%2fnode.brightid.org/Gitcoin/${brightid_uuid}`;

  const content = $.parseHTML(
    `<div id="connect_brightid_modal" class="modal fade" tabindex="-1" role="dialog" aria-hidden="true">
        <div class="modal-dialog">
          <div class="modal-content px-4 py-3">
            <div class="col-12">
              <button type="button" class="close" data-dismiss="modal" aria-label="Close">
                <span aria-hidden="true">&times;</span>
              </button>
            </div>
            <div class="col-12 pt-2 pb-2 text-center">
              <img src="/static/v2/images/project_logos/brightid.png" alt="BrightID Logo" width="100">
              <h2 class="font-title mt-2">Connect With BrightID</h2>
            </div>
            <div class="col-12 pt-2">
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
              <p>
                <strong>Step 2</strong>: Connect BrightID to Gitcoin by scanning this QR code
                from the BrightID app, or <a href="${brightIdLink}">clicking here</a> from your mobile device.
                <div style="display: flex; justify-content: center; text-align: center;" id="qrcode"></div>
              </p>
              <div class="col-12 my-4 text-center">
                <a href="" class="btn btn-gc-blue px-5 mb-2 mx-2">Done Connecting</a>
              </div>
            </div>
          </div>
        </div>
      </div>`);

  $(content).appendTo('body');
  $('#connect_brightid_modal').bootstrapModal('show');

  // avoid duplicate QR Codes if user presses button multiple times
  if (!hasGeneratedBrightIdQRCode) {
    const element = document.getElementById('qrcode');
    const qrCodeData = {
      text: brightIdAppLink,
      width: 175,
      height: 175
    };

    new QRCode(element, qrCodeData); // eslint-disable-line

    hasGeneratedBrightIdQRCode = true;
  }
};

let show_brightid_verify_modal = function(brightid_uuid) {
  let callsMarkup = '';

  brightIDCalls = calendarData;

  function dateFormatter(date) {
    let options = {hour: 'numeric', minute: 'numeric', dayPeriod: 'short'};

    return new Intl.DateTimeFormat('en-US', options).format(new Date(date));
  }

  for (let index = 0; index < brightIDCalls.length; index++) {
    const call = brightIDCalls[index];
    const callDate = new Date(parseFloat(call.date) * 1000);

    let callsDate = call.dates.map((date) => {
      return `<span>${dateFormatter(date.timeStart)}</span> - <span>${dateFormatter(date.timeEnd)}</span>`;
    }).join(' <b>&</b> ');

    callsMarkup = `${callsMarkup}
        <div class="row mb-3">
          <div class="col-md-8">
            <strong class="d-block">${call.when}</strong>
            <div class="font-caption">
              At ${callsDate}
            </div>
          </div>

          <div class="col-md-4 my-auto">
            <a href="${call.link}" target="_blank" class="btn btn-sm btn-block btn-gc-blue px-4 font-caption font-weight-bold">Register <br> on ${call.platform}</a>
          </div>
        </div>
      `;
  }

  const content = $.parseHTML(
    `<div id="verify_brightid_modal" class="modal fade" tabindex="-1" role="dialog" aria-hidden="true">
        <div class="modal-dialog">
          <div class="modal-content px-4 py-3">
            <div class="col-12">
              <button type="button" class="close" data-dismiss="modal" aria-label="Close">
                <span aria-hidden="true">&times;</span>
              </button>
            </div>
            <div class="col-12 pt-2 pb-2 text-center">
              <img src="/static/v2/images/project_logos/brightid.png" alt="BrightID Logo" width="100">
              <h2 class="font-title mt-2">Verify Your BrightID</h2>
            </div>
            <div class="col-12 pt-2">
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
                ${callsMarkup}
              </p>
            </div>
          </div>
        </div>
      </div>`);

  $(content).appendTo('body');
  $('#verify_brightid_modal').bootstrapModal('show');
};

Vue.component('twitter-verify-modal', {
  delimiters: [ '[[', ']]' ],
  data: function() {
    return {
      showValidation: false,
      validationStep: 'send-tweet',
      tweetText: '',
      twitterHandle: '',
      validationError: ''
    };
  },
  computed: {
    encodedTweetText: function() {
      return encodeURIComponent(this.tweetText);
    },
    tweetIntentURL: function() {
      return `https://twitter.com/intent/tweet?text=${this.encodedTweetText}`;
    }
  },
  mounted: function() {
    this.tweetText = verifyTweetText; // Global from tab_trust.html <script> tag

    $(document).on('click', '#verify-twitter-link', function(event) {
      event.preventDefault();
      this.showValidation = true;
    }.bind(this));
  },
  template: `<b-modal id="twitter-modal" @hide="dismissVerification()" :visible="showValidation" center hide-header hide-footer>
                <template v-slot:default="{ hide }">
                  <div class="mx-5 mt-5 mb-4 text-center">
                    <div class="mb-3">
                      <h1 class="font-bigger-4 font-weight-bold">Verify your Twitter account</h1>
                    </div>
                    <div v-if="validationStep === 'send-tweet'">
                      <p class="mb-4 font-subheader text-left">
                        We want to verify your Twitter account. To do so, you must first send a standardized
                        Tweet from your account, then we'll validate it's there.
                      </p>
                      <p class="mb-4 font-subheader text-left">
                        The Tweet should say:
                      </p>
                      <p class="mb-4 font-subheader text-left">
                        <em>[[tweetText]]</em>
                      </p>
                      <div class="mt-2 mb-2">
                        <a :href="tweetIntentURL" @click="clickedSendTweet" role="button" style="font-size: 1.3em" class="button button--primary mb-2" target="_blank">
                          Send Tweet
                        </a>
                      </div>
                      <a href="" @click="clickedAlreadySent">
                        I have already Tweeted this
                      </a>
                    </div>
                    <div v-if="validationStep === 'validate-tweet' || validationStep == 'perform-validation'">
                      <p class="mb-4">
                        Now we'll validate that you've sent the tweet. Enter your Twitter handle and press validate.
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
                      <b-button @click="clickedValidate" :disabled="validationStep === 'perform-validation'" class="btn-gc-blue mt-3 mb-2" size="lg">
                        <b-spinner v-if="validationStep === 'perform-validation'" type="grow"></b-spinner>
                        Validate
                      </b-button>
                      <br />
                      <a href="" v-if="validationError !== ''" @click="clickedGoBack">
                        Go Back
                      </a>
                    </div>
                    <div v-if="validationStep === 'validation-complete'">
                      Your Twitter verification was successful. Thank you for helping make Gitcoin more sybil resistant!
                      <a href="" class="btn btn-gc-blue px-5 mt-3 mb-2 mx-2" role="button" style="font-size: 1.3em">Done</a>
                    </div>
                  </div>
                </template>
            </b-modal>`,
  methods: {
    dismissVerification() {
      this.showValidation = false;
    },
    clickedSendTweet(event) {
      this.validationStep = 'validate-tweet';
    },
    clickedAlreadySent(event) {
      event.preventDefault();
      this.validationStep = 'validate-tweet';
    },
    clickedGoBack(event) {
      event.preventDefault();
      this.validationStep = 'send-tweet';
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

      this.validationStep = 'perform-validation';

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
          this.validationStep = 'validation-complete';
        } else {
          this.validationError = response.msg;
          this.validationStep = 'validate-tweet';
        }

      }).catch((_error) => {
        this.validationError = 'There was an error; please try again later';
        this.validationStep = 'validate-tweet';
      });
    }
  }
});

// TODO: This component consists primarily of code taken from the SMS verification flow in the cart.
// This approach is not DRY, and after Grants Round 7 completes, the cart should be refactored to include
// this as a shared component, rather than duplicating the code.
Vue.component('sms-verify-modal', {
  delimiters: [ '[[', ']]' ],
  data: function() {
    return {
      csrf: $("input[name='csrfmiddlewaretoken']").val(),
      validationStep: 'intro',
      showValidation: false,
      phone: '',
      validNumber: false,
      errorMessage: '',
      verified: document.verified,
      code: '',
      timePassed: 0,
      timeInterval: 0,
      display_email_option: false,
      countDownActive: false
    };
  },
  mounted: function() {
    $(document).on('click', '#verify-sms-link', function(event) {
      event.preventDefault();
      this.showValidation = true;
    }.bind(this));
  },
  template: `<b-modal id="sms-modal" @hide="dismissVerification()" :visible="showValidation" center hide-header hide-footer>
              <template v-slot:default="{ hide }">
                <div class="mx-5 mt-5 mb-4 text-center" v-if="validationStep == 'intro'">
                  <div class="mb-3">
                    <h1 class="font-bigger-4 font-weight-bold">Verify your phone number</h1>
                  </div>
                  <br />
                  <p class="mb-4 font-subheader text-left">We'd like to verify your phone number to get your contribution matched. Phone number verification is optional.</p>
                  <br />
                  <p class="mb-4 font-subheader text-left">Verifying increases your trust level and impact of your contributions. You can still contribute to grants without
                  verifying your phone number, but your contribution impact will be reduced.</p>
                  <br />
                  <p class="mb-4 font-subheader text-left">Gitcoin does NOT store your phone number.</p>
                  <br />
                  <p class="mb-4 font-subheader text-left">read more about <a target="_blank" rel="noopener noreferrer" class="gc-text-blue font-smaller-1"
                    href="https://twitter.com/owocki/status/1271088915982675974">why we are asking for your phone number</a> or how Gitcoin <a target="_blank" rel="noopener noreferrer" class="gc-text-blue font-smaller-1"
                      href="https://twitter.com/owocki/status/1271088915982675974">preserves your privacy.</a></p>
                  <b-button @click="validationStep='requestVerification'" class="btn-gc-blue mb-2" size="lg">Verify
                  Phone Number</b-button>
                  <div class="mb-1 font-subheader text-center">
                    <a id="verify_offline" href="#">
                    <br />
                    Verify Offline or</a>  <a href="#" @click="dismissVerification()" variant="link">Skip</a>
                    <div id='verify_offline_target' style="display:none">
                      <strong>Verify Offline</strong>
                      <br />
                      <a href="mailto:kyc@gitcoin.co">Email Gitcoin</a> or <a href="https://keybase.io/gitcoin_verify">Message Gitcoin on Keybase</a>, and we will verify your information within 1-2 business days.
                      <br />
                      IMPORTANT: Be sure to include (1) your gitcoin username (2) proof of ownership of a SMS number.
                    </div>
                  </div>
                </div>
                <div class="mx-5 my-5 text-center" v-if="validationStep == 'requestVerification'">
                  <div class="mb-3">
                    <h1 class="font-bigger-4 font-weight-bold">Verify your phone number</h1>
                  </div>
                  <p class="mb-5 font-subheader">We will send you a verification code.</p>
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
                  <b-button @click="requestVerification()" class="btn-gc-blue mt-5 mb-2" size="lg">Send verification
                    code</b-button>
                  <br />
                  <b-button @click="hide()" variant="link">Cancel</b-button>
                </div>
                <div class="mx-5 my-5 text-center" v-if="validationStep == 'verifyNumber'">
                  <div class="mb-3">
                    <h1 class="font-bigger-4 font-weight-bold">Verify your phone number</h1>
                  </div>
                  <p class="mb-5 font-subheader">Enter the verification code sent to your number.</p>

                  <input class="form-control" type="number" required v-model="code">
                  <div v-if="timeInterval > timePassed">
                    <span class="label-warning">Wait [[ timeInterval - timePassed ]] second before request another
                      code</span>
                  </div>
                  <div v-if="errorMessage">
                    <span class="label-warning">[[ errorMessage ]]</span>
                  </div>
                  <b-button @click="validateCode()" class="btn-gc-blue mt-5" size="lg">Submit</b-button>
                  <br />
                  <b-button @click="startVerification()" variant="link">Change number</b-button>
                  <b-button @click="resendCode()" variant="link">Resend Code</b-button>
                    <b-button @click="resendCode('email')" variant="link" v-if="display_email_option">Send email</b-button>
                </div>
              </template>
            </b-modal>`,
  methods: {
    dismissVerification() {
      localStorage.setItem('dismiss-sms-validation', true);
      this.showValidation = false;
    },
    // VALIDATE
    validateCode() {
      const vm = this;

      if (vm.code) {
        const verificationRequest = fetchData('/sms/validate/', 'POST', {
          code: vm.code,
          phone: vm.phone
        }, {'X-CSRFToken': vm.csrf});

        $.when(verificationRequest).then(response => {
          vm.verificationEnabled = false;
          vm.verified = true;
          vm.validationStep = 'verifyNumber';
          vm.showValidation = false;
          _alert('You have been verified. <a href="" style="color: white; text-decoration: underline;">Refresh Page</a>.', 'success');
        }).catch((e) => {
          vm.errorMessage = e.responseJSON.msg;
        });
      }
    },
    startVerification() {
      this.phone = '';
      this.validationStep = 'requestVerification';
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
        const verificationRequest = fetchData('/sms/request', 'POST', {
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
          vm.errorMessage = e.responseJSON.msg;
        });
      }
    },
    // REQUEST VERIFICATION
    requestVerification(event) {
      const e164 = this.phone.replace(/\s/g, '');
      const vm = this;

      if (vm.validNumber) {
        const verificationRequest = fetchData('/sms/request', 'POST', {
          phone: e164
        }, {'X-CSRFToken': vm.csrf});

        vm.errorMessage = '';

        $.when(verificationRequest).then(response => {
          vm.validationStep = 'verifyNumber';
          this.timePassed = 0;
          this.timeInterval = 60;
          this.countdown();
          this.display_email_option = response.allow_email;
        }).catch((e) => {
          vm.errorMessage = e.responseJSON.msg;
        });
      }
    },
    isValidNumber(validation) {
      console.log(validation);
      this.validNumber = validation.isValid;
    }
  }
});

$(document).ready(function() {
  $(document).on('keyup', 'input[name=telephone]', function(e) {
    var number = $(this).val();

    if (number[0] != '+') {
      number = '+' + number;
      $(this).val(number);
    }
  });


  $(document).on('click', '#verify_offline', function(e) {
    $(this).remove();
    $('#verify_offline_target').css('display', 'block');
  });
});

if (document.getElementById('gc-trust-verify-modal')) {

  const smsVerificationApp = new Vue({
    delimiters: [ '[[', ']]' ],
    el: '#gc-trust-verify-modal',
    data: { }
  });
}