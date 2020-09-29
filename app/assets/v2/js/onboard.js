let step = 1;
let orgs = document.contxt.orgs;
let tasks = document.contxt.onboard_tasks;

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
        orgs: orgs,
        data: {
          bio: '',
          skillsSelected: [],
          jobSelected: [],
          interestsSelected: [],
          userOptions: [],
          orgSelected: [],
          orgOptions: [],
          email: ''
        },
        skills: [],
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
        tasks : tasks
      };
    },
    computed: {
      totalcharacter: function() {
        return this.data.bio.length;
      }
    },
    methods: {
      openModalStep(step) {
        let vm = this;

        vm.step = step;
        vm.$refs['onboard-modal'].openModal();
      },
      goStep(step) {
        let vm = this;

        vm.step = step;
        vm.scrollToTop();
      },
      scrollToTop() {
        let vm = this;

        vm.$refs["onboard-modal"].$el.scrollTo(0,0);
      },
      submitData() {
        let vm = this;
        const apiUrlPersona = '/api/v1/onboard_save/';
        const postPersonaData = fetchData(apiUrlPersona, 'POST', vm.data);

        $.when(postPersonaData).then((response) => {

          if (vm.step === 3 && vm.orgSelected) {
            document.location.href = `/${vm.orgSelected}`
          }
          this.profileWidget();
          this.$refs['onboard-modal'].closeModal();

        }).catch((err) => {
          console.log(err);
          _alert('Unable to create a bounty. Please try again later', 'error');
        });
      },
      fetchOnboardData(profileHandle) {
        let vm = this;
        let handle = profileHandle || document.contxt.github_handle ;
        const apiUrlSkills = `/api/v0.1/profile/${handle}`;
        const getSkillsData = fetchData(apiUrlSkills, 'GET');

        $.when(getSkillsData).then((response) => {
          if (profileHandle) {
            vm.data.orgOptions = response.userOptions;
            vm.data.email = response.contact_email;
          } else {
            vm.data.skillsSelected = response.keywords;
            vm.data.bio = response.bio;
            vm.data.jobSelected = response.jobSelected;
            vm.data.interestsSelected = response.interestsSelected;
            vm.data.userOptions = response.userOptions;


          }

        }).catch((err) => {
          console.log(err);
          // _alert('Unable to create a bounty. Please try again later', 'error');
        });
      },
      fetchOrgOnboardData(handle) {
        let vm = this;

        vm.fetchOnboardData(handle);

      },
      keywordSearch(search, loading) {
        let vm = this;

        if (search.length < 1) {
          return;
        }

        if (this.timeout) {
          clearTimeout(this.timeout);
        }

        this.timeout = setTimeout(() => {
          loading(true);
          vm.getKeyword(loading, search);
        }, 1000);

      },
      getKeyword: async function(loading, search) {
        let vm = this;
        let myHeaders = new Headers();
        let url = `/api/v0.1/keywords_search/?term=${escape(search)}`;

        myHeaders.append('X-Requested-With', 'XMLHttpRequest');
        return new Promise(resolve => {

          fetch(url, {
            credentials: 'include',
            headers: myHeaders
          }).then(res => {
            res.json().then(json => {
              vm.skills = json;
              resolve();
            });
            if (loading) {
              loading(false);
            }
          });
        });
      },
      profileWidget: function(){
        let vm = this;
        let target = document.getElementById('profile-completion');
        let step = 1;

        console.log(target)
        if (vm.data.interestsSelected && vm.data.bio) {
          step = 2;
        }

        if (target) {
          target.innerHTML = `
          <div class="p-3">
            <div>
            Signup
            Profile
            Interests
            </div>

            <ul class="list-unstyled">
              ${vm.tasks.map((task, index) => `
                <li class="d-flex align-items-center justify-content-between">
                  <a class="" id="task-${index}" href="${task.link}">
                    ${task.title}
                  </a>
                  <i class="fa fa-check-circle" onclick=""></i>
                  <i class="far fa-circle d-none" onclick=""></i>
                </li>
              `).join(' ')}
            </ul>
            <button class="" onClick="popOnboard(${step})">Complete Profile</button>
          </div>`;
        }
      }

    },
    mounted() {
      if (
        document.contxt.github_handle &&
        !document.contxt.persona_is_funder &&
        !document.contxt.persona_is_hunter
      ) {
        // show_persona_modal();
        this.$refs['onboard-modal'].openModal();
      }
      this.fetchOnboardData();
    },
    created() {

    }
  });
}
