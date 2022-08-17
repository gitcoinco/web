Vue.component('v-select', VueSelect.VueSelect);
Vue.use(VueQuillEditor);

const step1Errors = [ 'grant_tags', 'tag_eligibility_reason', 'has_external_funding' ];
const step2Errors = [ 'title', 'description', 'reference_url', 'twitter_handle_1' ];
const step3Errors = ['chainId'];
const errorsByStep = [ step1Errors, step2Errors, step3Errors ];

Vue.mixin({
  data() {
    return {
      step: 1,
      description: '',
      richDescription: ''
    };
  },
  methods: {
    quilUpdated({ quill, text }) {
      this.description = text;
      this.richDescription = JSON.stringify(quill.getContents());
    },
    showQuickStart: function() {

      fetch('/grants/quickstart')
        .then(function(response) {
          return response.text();
        }).then(function(html) {
          let parser = new DOMParser();
          let doc = parser.parseFromString(html, 'text/html');

          doc.querySelector('.btn-closeguide').dataset.dismiss = 'modal';

          let docArticle = doc.querySelector('.content').innerHTML;
          const content = $.parseHTML(
            `<div id="gitcoin_updates" class="modal fade" tabindex="-1" role="dialog" aria-hidden="true">
              <div class="modal-dialog modal-xl" style="max-width:95%">
                <div class="modal-content px-4 py-3">
                  <div class="col-12">
                    <button type="button" class="close" data-dismiss="modal" aria-label="Close">
                      <span aria-hidden="true">&times;</span>
                    </button>
                  </div>
                  ${docArticle}
                  <div class="col-12 my-4 d-flex justify-content-around">
                    <button type="button" class="btn btn-primary" data-dismiss="modal" aria-label="Close">Close</button>
                  </div>
                </div>
              </div>
            </div>`);

          $(content).appendTo('body');
          $('#gitcoin_updates').bootstrapModal('show');
          setupTabs('#grant-quickstart-tabs');
        });

      $(document, '#gitcoin_updates').on('hidden.bs.modal', function(e) {
        $('#gitcoin_updates').remove();
        $('#gitcoin_updates').bootstrapModal('dispose');
      });
    },
    userSearch(search, loading) {
      let vm = this;

      if (search.length < 3) {
        return;
      }
      loading(true);
      vm.getUser(loading, search);

    },
    getUser: async function(loading, search, selected) {
      let vm = this;
      let myHeaders = new Headers();
      let url = `/api/v0.1/users_search/?token=${currentProfile.githubToken}&term=${escape(search)}&suppress_non_gitcoiners=true`;

      myHeaders.append('X-Requested-With', 'XMLHttpRequest');
      return new Promise(resolve => {

        fetch(url, {
          credentials: 'include',
          headers: myHeaders
        }).then(res => {
          res.json().then(json => {
            vm.$set(vm, 'usersOptions', json);
            if (selected) {
              // TODO: BUG -> Make append
              vm.$set(vm.form, 'team_members', vm.usersOptions[0].text);
            }
            resolve();
          });
          if (loading) {
            loading(false);
          }
        });
      });
    },
    validateTwitterHandle: (input) => input && !(/^@?[a-zA-Z0-9_]{2,15}$/).test(input),
    checkForm: function(e) {
      let vm = this;

      vm.errors = {};
      if (!vm.form.title.length) {
        vm.$set(vm.errors, 'title', 'Please enter the title');
      }
      if (!vm.form.reference_url.length) {
        vm.$set(vm.errors, 'reference_url', 'Please enter link to the project');
      }
      if (!vm.form.twitter_handle_1.length) {
        vm.$set(vm.errors, 'twitter_handle_1', 'Please enter twitter handle of your project');
      }
      if (this.validateTwitterHandle(vm.form.twitter_handle_1)) {
        vm.$set(vm.errors, 'twitter_handle_1', 'Please enter a valid twitter handle of your project e.g @humanfund');
      }
      if (this.validateTwitterHandle(vm.form.twitter_handle_2)) {
        vm.$set(vm.errors, 'twitter_handle_2', 'Please enter your twitter handle e.g @georgecostanza');
      }

      // payout address validation based on chain
      if (!vm.chainId) {
        vm.$set(vm.errors, 'chainId', 'Please select an option');
      } else if (vm.chainId == 'eth') {
        if (!vm.form.eth_payout_address) {
          vm.$set(vm.errors, 'eth_payout_address', 'Please enter ETH address');
        } else if (vm.form.eth_payout_address.trim().endsWith('.eth')) {
          vm.$set(vm.errors, 'eth_payout_address', 'ENS is not supported. Please enter ETH address');
        } else if (!Web3.utils.isAddress(vm.form.eth_payout_address)) {
          vm.$set(vm.errors, 'eth_payout_address', 'Please enter a valid ETH address');
        }
      } else if (
        vm.chainId == 'zcash' &&
        (!vm.form.zcash_payout_address || !vm.form.zcash_payout_address.toLowerCase().startsWith('t'))
      ) {
        vm.$set(vm.errors, 'zcash_payout_address', 'Please enter transparent ZCash address');
      } else if (vm.chainId == 'celo' && !vm.form.celo_payout_address) {
        vm.$set(vm.errors, 'celo_payout_address', 'Please enter CELO address');
      } else if (vm.chainId == 'zilliqa' && !vm.form.zil_payout_address) {
        vm.$set(vm.errors, 'zil_payout_address', 'Please enter Zilliqa address');
      } else if (vm.chainId == 'harmony' && !vm.form.harmony_payout_address) {
        vm.$set(vm.errors, 'harmony_payout_address', 'Please enter Harmony address');
      } else if (vm.chainId == 'binance' && !vm.form.binance_payout_address) {
        vm.$set(vm.errors, 'binance_payout_address', 'Please enter Binance address');
      } else if (vm.chainId == 'polkadot' && !vm.form.polkadot_payout_address) {
        vm.$set(vm.errors, 'polkadot_payout_address', 'Please enter Polkadot address');
      } else if (vm.chainId == 'kusama' && !vm.form.kusama_payout_address) {
        vm.$set(vm.errors, 'kusama_payout_address', 'Please enter Kusama address');
      } else if (vm.chainId == 'rsk' && !vm.form.rsk_payout_address) {
        vm.$set(vm.errors, 'rsk_payout_address', 'Please enter RSK address');
      } else if (vm.chainId == 'algorand' && !vm.form.algorand_payout_address) {
        vm.$set(vm.errors, 'algorand_payout_address', 'Please enter Algorand address');
      } else if (vm.chainId == 'cosmos' && !vm.form.cosmos_payout_address) {
        vm.$set(vm.errors, 'cosmos_payout_address', 'Please enter Cosmos address');
      }

      if (!vm.form.grant_type) {
        vm.$set(vm.errors, 'grant_type', 'Please select the grant category');
      }
      if (!vm.form.grant_tags.length > 0) {
        vm.$set(vm.errors, 'grant_tags', 'Please select one or more grant tag');
      }
      if (!vm.form.tag_eligibility_reason.length) {
        vm.$set(vm.errors, 'tag_eligibility_reason', 'Please enter eligibility tag reasoning');
      }
      if (vm.richDescription.length < 10) {
        vm.$set(vm.errors, 'description', 'Please enter description for the grant');
      }
      if (!vm.form.has_external_funding) {
        vm.$set(vm.errors, 'has_external_funding', 'Please select if grant has external funding');
      }
      const errorKeys = Object.keys(vm.errors);


      if (errorKeys.length) {
        // find the the first step that has errors and redirect to it
        const errorsByPage = errorsByStep.map((stepErrors, i) => {
          // if current errors are found in this step return step
          return errorKeys.filter((error) => stepErrors.includes(error)).length ? (i + 1) : 100;
        });
        // only redirect if on confirm step

        if (vm.step === vm.currentSteps.length) {
          // set step to the first step that has an error
          vm.step = Math.min(...errorsByPage);
        }

        return false; // there are errors the user must correct
      }

      return true;
    },
    submitForm: async function() {
      let vm = this;
      let form = vm.form;

      // Exit if form is not valid
      if (!vm.checkForm())
        return;

      if (form.reference_url.startsWith('www.')) {
        form.reference_url = 'https://' + form.reference_url;
      }

      const params = {
        'title': form.title,
        'reference_url': form.reference_url,
        'logo': vm.logo,
        'description': vm.description,
        'description_rich': vm.richDescription,
        'team_members[]': form.team_members,
        'handle1': form.twitter_handle_1,
        'handle2': form.twitter_handle_2,
        'github_project_url': form.github_project_url,
        'eth_payout_address': form.eth_payout_address,
        'zcash_payout_address': form.zcash_payout_address,
        'celo_payout_address': form.celo_payout_address,
        'zil_payout_address': form.zil_payout_address,
        'harmony_payout_address': form.harmony_payout_address,
        'binance_payout_address': form.binance_payout_address,
        'polkadot_payout_address': form.polkadot_payout_address,
        'kusama_payout_address': form.kusama_payout_address,
        'rsk_payout_address': form.rsk_payout_address,
        'algorand_payout_address': form.algorand_payout_address,
        'cosmos_payout_address': form.cosmos_payout_address,
        'grant_type': form.grant_type,
        'tags[]': form.grant_tags,
        'tag_eligibility_reason': form.tag_eligibility_reason,
        'network': form.network,
        'region': form.region,
        'has_external_funding': form.has_external_funding
      };

      console.log(params);
      vm.submitted = true;
      vm.submitGrant(params);

    },
    submitGrant(data) {
      let vm = this;

      if (typeof ga !== 'undefined') {
        ga('send', 'event', 'Create Grant', 'click', 'Grant Creator');
      }

      const headers = {
        'X-CSRFToken': $("input[name='csrfmiddlewaretoken']").val()
      };

      let apiUrlGrant = '/grants/new';

      if (vm.queryParams.get('related_hackathon_project_id')) {
        apiUrlGrant += `?related_hackathon_project_id=${vm.queryParams.get('related_hackathon_project_id')}`;
      }
      $.ajax({
        type: 'post',
        url: apiUrlGrant,
        processData: false,
        contentType: false,
        data: getFormData(data),
        headers: headers,
        success: response => {
          MauticEvent.createEvent({
            'alias': 'products',
            'data': [
              {
                'name': 'product',
                'attributes': {
                  'product': 'grants',
                  'persona': 'grants-creator',
                  'action': 'create'
                }
              }
            ]
          });
          if (response.status == 200) {
            window.location = response.url;
            localStorage['grant_state'] = 'created';
          } else {
            vm.submitted = false;
            _alert('Unable to create grant. Please try again', 'danger');
            console.error(`error: grant creation failed with status: ${response.status} and message: ${response.message}`);
          }
        },
        error: err => {
          vm.submitted = false;
          _alert('Unable to create grant. Please try again', 'danger');
          console.error(`error: grant creation failed with msg ${err}`);
        }
      });
    },
    resetAddress() {
      let vm = this;
      let form = vm.form;

      form.eth_payout_address = '';
      form.celo_payout_address = '';
      form.zcash_payout_address = '';
      form.zil_payout_address = '';
      form.harmony_payout_address = '';
      form.binance_payout_address = '';
      form.polkadot_payout_address = '';
      form.kusama_payout_address = '';
      form.rsk_payout_address = '';
      form.algorand_payout_address = '';
      form.cosmos_payout_address = '';
    },
    onFileChange(e) {
      let vm = this;

      if (!e.target) {
        return;
      }

      const file = e.target.files[0];

      if (!file) {
        return;
      }

      let imgCompress = new Compressor(file, {
        quality: 0.6,
        maxWidth: 2000,
        success(result) {
          vm.logoPreview = URL.createObjectURL(result);
          vm.logo = new File([result], result.name, { lastModified: result.lastModified });
          $('#preview').css('width', '100%');
          $('#js-drop span').hide();
          $('#js-drop input').css('visible', 'invisible');
          $('#js-drop').css('padding', 0);
        },
        error(err) {
          _alert(err.message, 'danger');
        }
      });
    },
    handleTwitterUsername(event) {
      const inputField = event.target;
      const matchResult = inputField.value.match(/https:\/\/twitter.com\/(\w{4,15})/);

      const extracted = matchResult ? `@${matchResult[1]}` : inputField.value;

      this.$set(this.form, inputField.id, extracted);
    },
    updateNav: function(direction) {
      if (direction === 1) {
        if (this.step === this.currentSteps.length) {
          this.submitForm();
          return;
        }
        this.step += direction;
      } else if (this.step > 1) {
        this.step += direction;
      }
    }
  },
  watch: {
    deep: true,
    teamMembers: {
      handler(newVal, oldVal) {
        let team_members_id;

        team_members_id = newVal.reduce((oldItem, newItem)=> {
          oldItem.push(newItem.id);
          return oldItem;
        }, []);
        return this.$set(this.form, 'team_members', team_members_id);

      }

    },
    form: {
      deep: true,
      handler(newVal, oldVal) {
        if (this.dirty && this.submitted) {
          this.checkForm();
        }
        this.dirty = true;
      }
    }
  }
});

const grant_regions = [
  { 'name': 'north_america', 'label': 'North America'},
  { 'name': 'oceania', 'label': 'Oceania'},
  { 'name': 'latin_america', 'label': 'Latin America'},
  { 'name': 'europe', 'label': 'Europe'},
  { 'name': 'africa', 'label': 'Africa'},
  { 'name': 'middle_east', 'label': 'Middle East'},
  { 'name': 'india', 'label': 'India'},
  { 'name': 'east_asia', 'label': 'East Asia'},
  { 'name': 'southeast_asia', 'label': 'Southeast Asia'}
];

const grant_chains = [
  { 'name': 'eth', 'label': 'Ethereum'},
  { 'name': 'zcash', 'label': 'ZCash'},
  { 'name': 'celo', 'label': 'Celo'},
  { 'name': 'zilliqa', 'label': 'Zilliqa'},
  { 'name': 'harmony', 'label': 'Harmony'},
  { 'name': 'binance', 'label': 'Binance'},
  { 'name': 'polkadot', 'label': 'Polkadot'},
  { 'name': 'kusama', 'label': 'Kusama'},
  { 'name': 'algorand', 'label': 'Algorand'},
  { 'name': 'rsk', 'label': 'RSK'},
  { 'name': 'cosmos', 'label': 'Cosmos'}
];

if (document.contxt.is_staff) {
  const staff_chains = [
  ];

  grant_chains.push(...staff_chains);
}

const externalFundingOptions = [
  {'key': 'yes', 'value': 'Yes, this project has raised external funding.'},
  {'key': 'no', 'value': 'No, this project has not raised external funding.'}
];

if (document.getElementById('gc-new-grant')) {
  appFormBounty = new Vue({
    delimiters: [ '[[', ']]' ],
    el: '#gc-new-grant',
    components: {
      'vue-select': 'vue-select'
    },
    data() {
      return {
        chainId: '',
        grant_tags: document.grant_tags,
        grant_regions: grant_regions,
        grant_chains: grant_chains,
        externalFundingOptions: externalFundingOptions,
        usersOptions: [],
        network: 'mainnet',
        logo: null,
        logoPreview: null,
        teamMembers: [],
        submitted: false,
        errors: {},
        form: {
          title: '',
          reference_url: '',
          description_rich: '',
          team_members: [],
          region: null,
          twitter_handle_1: '',
          twitter_handle_2: '',
          github_project_url: '',
          eth_payout_address: '',
          zcash_payout_address: '',
          celo_payout_address: '',
          zil_payout_address: '',
          harmony_payout_address: '',
          binance_payout_address: '',
          polkadot_payout_address: '',
          kusama_payout_address: '',
          rsk_payout_address: '',
          algorand_payout_address: '',
          cosmos_payout_address: '',
          grant_type: 'gr12',
          grant_tags: [],
          tag_eligibility_reason: '',
          network: 'mainnet'
        },
        editorOptionPrio: {
          modules: {
            toolbar: [
              [ 'bold', 'italic', 'underline' ],
              [{ 'align': [] }],
              [{ 'list': 'ordered'}, { 'list': 'bullet' }],
              [ 'link', 'code-block' ],
              ['clean']
            ]
          },
          theme: 'snow',
          placeholder: 'Give a detailed description about your Grant'
        }
      };
    },
    computed: {
      disableConfirm() {
        return this.submitted && this.step === this.currentSteps.length && Object.keys(this.errors).length === 0;
      },
      grantTagOptions() {
        const sorted_tags = this.grant_tags.sort((a, b) => a.id - b.id);
        const next_id = sorted_tags[sorted_tags.length - 1].id + 1;
        const all_tags = this.grant_tags.sort((a, b) => b.is_eligibility_tag - a.is_eligibility_tag);
        const first_discovery = (tag) => tag.is_eligibility_tag === 0;

        all_tags.unshift({
          id: 0,
          name: 'eligibility tags'.toUpperCase(),
          is_eligibility_tag: 'label'
        });

        all_tags.splice(all_tags.findIndex(first_discovery), 0, {
          id: next_id,
          name: 'discovery tags'.toUpperCase(),
          is_eligibility_tag: 'label'
        });

        return all_tags;
      },
      queryParams() {
        return new URLSearchParams(window.location.search);
      },
      clean() {
        return value => {
          value = decodeURIComponent(value);
          if ((/<[a-zA-Z\\\/]+>/).test(value)) {
            // if it matches a tag, reset the value to empty
            value = '';
          }
          const arrayCheckRegex = /\[.+\]/;

          if (arrayCheckRegex.test(value)) {
            // check if array is passed in query params and return it as an array instead of default string.
            // i.e change "[1, 2]" to [1, 2]
            value = value.substr(1, value.length - 2);
            value = value.split(',');
            value = value.map(item => {
              if (!isNaN(item)) {
                return +item;
              }
              return item;
            });
          }
          return value;
        };
      },
      currentSteps() {
        const steps = [
          {
            text: 'Eligibility & Discovery',
            active: false
          },
          {
            text: 'Grant Details',
            active: false
          },
          {
            text: 'Owner Information',
            active: false
          },
          {
            text: 'Review Grant',
            active: false
          }
        ];

        if (this.step == 100) {
          this.step = steps.length;
        }

        steps[this.step - 1].active = true;
        return steps;
      }
    },
    mounted() {
      const writeToRoot = ['chainId'];
      const writeToBody = [
        'title',
        'description_rich',
        'reference_url',
        'twitter_handle_1',
        'twitter_handle_2',
        'github_project_url',
        'eth_payout_address',
        'grant_type',
        'team_members',
        'grant_tags',
        'tag_eligibility_reason'
      ];

      for (const key of writeToRoot) {
        if (this.queryParams && this.queryParams.has(key)) {
          this[key] = this.clean(this.queryParams.get(key));
        }
      }
      for (const key of writeToBody) {
        if (this.queryParams && this.queryParams.has(key)) {
          this.form[key] = this.clean(this.queryParams.get(key));
        }
      }
    }
  });
}
