Vue.component('v-select', VueSelect.VueSelect);


Vue.mixin({
  methods: {
    clearForm: function() {
      let vm = this;

      vm.form = {
        why: '',
        amount: 0,
        stage: '',
        grant_types: [],
        grant_tags: [],
        grant_collections: [],
        anonymous: false,
        comment: '',
        tx_id: ''
      };

      vm.errors = {};
    },
    transfer_web3: function(params) {
      let vm = this;

      const amount = params.amount;
      const decimals = 18;
      const to = '0xde21F729137C5Af1b01d73aF1dC21eFfa2B8a0d6';
      // const token_addr = "0x6B175474E89094C44Da98b954EedeAC495271d0F";
      const token_addr = (document.web3network == 'mainnet') ?
        '0x6B175474E89094C44Da98b954EedeAC495271d0F' :
        '0x5592EC0cfb4dbc12D3aB100b257153436a1f0FEa'

      ;
      const amountInWei = amount * 1.0 * Math.pow(10, decimals);
      const amountAsString = new web3.utils.BN(BigInt(amountInWei)).toString();

      const token_contract = new web3.eth.Contract(token_abi, token_addr);

      return token_contract.methods.transfer(to, web3.utils.toHex(amountAsString))
        .send({from: selectedAccount},
          (error, tx_id) => {
            if (error) {
              _alert('Transaction Failed. To fund the matching pool please visit this Grant.', 'danger');
              document.location.href = 'https://gitcoin.co/grants/12/gitcoin-grants-official-matching-pool-fund';
              console.error(`error: unable to pay pledge due to : ${error}`);
              return;
            }
            params['tx_id'] = tx_id;
            console.log(params);
            vm.submitted = true;
            vm.createMatchingPledge(params);

          }
        );
    },
    checkForm: function(e) {
      let vm = this;

      vm.submitted = true;
      vm.errors = {};
      if (!vm.form.why.length) {
        vm.$set(vm.errors, 'why', 'Please select why you want to create a match pledge');
      }
      if (!vm.form.amount) {
        vm.$set(vm.errors, 'amount', 'Please enter amount you would want to pledge');
      }
      if (!vm.form.stage) {
        vm.$set(vm.errors, 'stage', 'Please select the stage of funding');
      }

      if (!vm.grants_to_fund) {
        vm.$set(vm.errors, 'grants_to_fund', 'Please select one of the options');
      } else if (vm.grants_to_fund == 'types' && !vm.form.grant_types.length > 0) {
        vm.$set(vm.errors, 'grant_types', 'Please select the grant types');
      } else if (vm.grants_to_fund == 'collections' && !vm.form.grant_collections.length > 0) {
        vm.$set(vm.errors, 'grant_collections', 'Please select the collections');
      }


      if (Object.keys(vm.errors).length) {
        return false; // there are errors the user must correct
      }
      vm.submitted = false;
      return true; // no errors, continue to create match pledge
    },
    submitForm: async function(event) {
      event.preventDefault();
      let vm = this;
      let form = vm.form;

      // Exit if form is not valid
      if (!vm.checkForm(event))
        return;

      if (vm.grants_to_fund == 'types') {
        vm.form.grant_collections = [];
      } else if (vm.grants_to_fund == 'collections') {
        vm.form.grant_types = [];
        vm.form.grant_tags = [];
      }

      const params = {
        'why': form.why,
        'amount': form.amount,
        'stage': form.stage,
        'grant_types[]': form.grant_types.join(),
        'grant_tags[]': form.grant_tags.join(),
        'grant_collections[]': form.grant_collections.join(),
        'anonymous': form.anonymous,
        'comment': form.comment
      };

      vm.submitted = true;
      vm.createMatchingPledge(params);

    },
    async createMatchingPledge(data) {
      let vm = this;

      if (typeof ga !== 'undefined') {
        ga('send', 'event', 'Create Match Pledge', 'click', 'Grant Match Pledge Creator');
      }


      try {
        const url = '/grants/v1/api/matching-pledge/create';

        const headers = {
          'X-CSRFToken': $("input[name='csrfmiddlewaretoken']").val()
        };

        response = await fetchData(url, 'POST', data, headers);

        if (response.status == 200) {
          MauticEvent.createEvent({
            'alias': 'products',
            'data': [
              {
                'name': 'product',
                'attributes': {
                  'product': 'grants',
                  'persona': 'grants-pledger',
                  'action': 'submit'
                }
              }
            ]
          });
          _alert('Match Pledge Request Recorded.  To fund the matching pool please visit this Grant.', 'success');
          vm.clearForm();
          document.location.href = 'https://gitcoin.co/grants/12/gitcoin-grants-official-matching-pool-fund';
        } else {
          vm.submitted = false;
          _alert('Unable to create matching pledge. Please try again', 'danger');
          console.error(`error: match pledge creation failed with status: ${response.status} and message: ${response.message}`);
        }

      } catch (err) {
        vm.submitted = false;
        _alert('Unable to create matching pledge. Please try again', 'danger');
        console.error(`error: match pledge creation failed with msg ${err}`);
      }
    }
  },
  watch: {
    deep: true,
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

if (document.getElementById('gc-new-match')) {

  const why_options = [
    'to see an ecosystem grow',
    'to give back',
    'to support a marketing campaign',
    'all of the above',
    'other'
  ];
  const stage_options = [
    {'key': 'ready', 'val': 'I am ready to transfer DAI'},
    {'key': 'details', 'val': 'Not ready to transfer DAI'}
  ];

  appFormBounty = new Vue({
    delimiters: [ '[[', ']]' ],
    el: '#gc-new-match',
    components: {
      'vue-select': 'vue-select'
    },
    data() {
      return {
        grants_to_fund: 'types',
        grant_types: document.grant_types,
        grant_collections: document.grant_collections,
        grant_tags: document.grant_tags,
        why_options: why_options,
        stage_options: stage_options,
        network: 'mainnet',
        submitted: false,
        errors: {},
        form: {
          why: '',
          amount: 0,
          stage: '',
          grant_types: [],
          grant_tags: [],
          grant_collections: [],
          anonymous: false,
          comment: '',
          tx_id: ''
        }
      };
    }
  });
}
