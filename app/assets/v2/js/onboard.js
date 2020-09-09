let step = 3;
let orgs = document.contxt.orgs;

Vue.component('v-select', VueSelect.VueSelect);

Vue.mixin({
  methods: {
  },
  computed: {

  }

});


if (document.getElementById('gc-onboard')) {
  var appOnboard = new Vue({
    delimiters: [ '[[', ']]' ],
    el: '#gc-onboard',
    components: {
      'vue-select': 'vue-select'
    },
    data() {
      return {
        step: step,
        isOrg: false,
        bio: '',
        orgs: orgs,
        // totalcharacter:0,
        skills: ['css','php'],
        skillsSelected: [],
        orgSelected: [],
        interests: [
          'Front End Development',
          'Back End Development',
          'Design',
          'Decentralized Finance',
          'Non-Fungibles & Gaming',
          'Infrastructure & Research',
          `DAO's & Governance`,
          'Marketplaces',
          'Token Economics',
          'Community Building',
          'Gamification',
          'Web3',
          'Freelance Jobs',
          'Healthcare'
        ],
        jobSelected: [],
        jobSearchStatus: [
          {
            value: 'AL',
            string: 'I am actively looking for work'
          },
          {
            value: 'PL',
            string: 'I am passively looking and open to hearing new opportunities'
          },
          {
            value: 'N',
            string: 'I am not open to hearing new opportunities'
          }
        ],
        interestsSelected: [],
        // userOptions: [{
        //   product: 'Bounties',
        //   icons: '📖💰💬',
        //   logo:
        // }]
        userOptions: []
      };
    },
    computed: {
      totalcharacter: function() {
        return this.bio.length;
      }
    },
    methods: {
      openModalStep(step) {
        let vm = this;
        vm.step = step;
        vm.$refs['onboard-modal'].openModal();
      },
      submitData() {
        let vm = this;
        const apiUrlPersona = '/api/v1/choose_persona/';
        const postPersonaData = fetchData(apiUrlPersona, 'POST', data);

        $.when(postPersonaData).then((response) => {

        }).catch((err) => {
          console.log(err);
          _alert('Unable to create a bounty. Please try again later', 'error');
        });
      }


    },
    mounted() {
      this.$refs['onboard-modal'].openModal();
    },
    created() {

    }
  });
}
