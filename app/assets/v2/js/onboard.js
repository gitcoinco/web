/* eslint quotes: ["error", "single", { "allowTemplateLiterals": true }] */

let step = 1;
let orgs = document.contxt.orgs;
let tasks = document.contxt.onboard_tasks;
let optoutOnboard = sessionStorage.optoutOnboard;

Vue.component('v-select', VueSelect.VueSelect);

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
        optoutOnboard: optoutOnboard,
        data: {
          bio: '',
          skillsSelected: [],
          jobSelected: [],
          interestsSelected: [],
          userOptions: [],
          orgSelected: '',
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
        tasks: tasks
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

        vm.$refs['onboard-modal'].$el.scrollTo(0, 0);
      },
      submitData() {
        let vm = this;
        const apiUrlPersona = '/api/v1/onboard_save/';
        const postPersonaData = fetchData(apiUrlPersona, 'POST', vm.data);

        $.when(postPersonaData).then((response) => {

          if (vm.step === 3 && vm.orgSelected) {
            document.location.href = `/${vm.orgSelected}`;
          }
          this.profileWidget();
          this.$refs['onboard-modal'].closeModal();

          dataLayer.push({
            'event': 'send',
            'category': 'onboard',
            'action': 'saved-profile-onboard'
          });

          if (typeof ga !== 'undefined') {
            ga('send', 'event', 'Saved profile onboard', 'click', 'Person');
          }
        }).catch((err) => {
          console.log(err);
          _alert('Unable to save your profile. Please login again', 'error');
        });
      },
      fetchOnboardData(profileHandle) {
        let vm = this;
        let handle = profileHandle || document.contxt.github_handle;
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
              loading(false);

              resolve();
            });
            if (loading) {
              loading(false);
            }
          });
        });
      },
      profileWidget: function() {
        let vm = this;
        let target = document.getElementById('profile-completion');
        let step = 1;
        let isComplete = vm.data.interestsSelected && vm.data.bio && vm.data.userOptions.length;

        if (vm.data.interestsSelected.length && vm.data.bio) {
          step = 2;
        }

        if (target) {
          target.innerHTML = `
          <div class="p-3">
            <div>
              <div class="profile-widget">
                <div class="bar-view ${vm.data.userOptions.length ? 'complete' : ''} " data-step="3">
                  <span class="bar-dot"></span>
                  <span class="step-label">Interests</span>
                </div>
                <div class="bar-view ${vm.data.interestsSelected.length ? 'complete' : ''}" data-step="2">
                  <span class="bar-dot"></span>
                  <span class="step-label">Profile</span>
                </div>
                <div class="bar-view complete" data-step="1">
                  <span class="bar-dot"></span>
                  <span class="step-label">Signup</span>
                </div>
              </div>
            </div>

            <ul class="list-unstyled my-3 font-body">
              ${vm.tasks.length ? vm.tasks.map((task, index) => `
                <li class="d-flex align-items-center justify-content-between">
                  <a class="" id="task-${index}" href="${task.link}">
                  <i class="fa fa-check-circle"></i> ${task.title}
                  </a>
                </li>
              `).join(' ') : ''}
            </ul>
            <div class="text-center">
              <button class="btn btn-sm btn-primary" onClick="popOnboard(${step})">${isComplete ? 'Edit' : 'Complete'} Profile</button>
            </div>
          </div>`;
        }
      }

    },
    mounted() {
      // if (
      //   document.contxt.github_handle &&
      //   !document.contxt.persona_is_funder &&
      //   !document.contxt.persona_is_hunter &&
      //   !optoutOnboard
      // ) {
      //   // show_persona_modal();
      //   this.$refs['onboard-modal'].openModal();
      //   this.$refs['onboard-modal'].jqEl.on('hidden.bs.modal', function(e) {
      //     sessionStorage.optoutOnboard = true;
      //   });
      // }
      this.fetchOnboardData();
    }
  });
}
