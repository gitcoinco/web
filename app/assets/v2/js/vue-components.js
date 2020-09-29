Vue.mixin({
  data: function() {
    const isMobile = (/Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i).test(navigator.userAgent);

    return {
      isMobile,
      chatURL: document.chatURL || 'https://chat.gitcoin.co'
    };
  },
  methods: {
    chatWindow: function(channel) {
      window.chatSidebar.chatWindow(channel);
    }
  }
});

Vue.component('hackathon-sponsor-dashboard', {
  props: [],
  data: function() {
    return {
      isFunder: false,
      funderBounties: []
    };
  },
  methods: {
    fetchBounties: function() {
      let vm = this;
      // fetch bounties
      let apiUrlBounties = '/api/v0.1/user_bounties/';

      let getBounties = fetchData(apiUrlBounties, 'GET');

      $.when(getBounties).then((response) => {
        vm.isFunder = response.is_funder;
        vm.funderBounties = response.data;
      });
    }
  }
});

Vue.component('modal', {
  props: [ 'user', 'size', 'id', 'issueDetails' ],
  template: `<div class="vue-modal modal fade" :id="id" tabindex="-1" role="dialog" aria-labelledby="userModalLabel" aria-hidden="true">
        <div class="modal-dialog modal-dialog-centered" :class="size" role="document">
          <div class="modal-content">
            <div class="modal-header border-0">
              <button type="button" class="close" data-dismiss="modal" aria-label="Close">
                <span aria-hidden="true">×</span>
              </button>
            </div>
            <div class="modal-body pt-0 ">
              <slot name="header"></slot>
              <slot name="body"></slot>
            </div>
            <div class="modal-footer border-0">
              <slot name="footer"></slot>
            </div>
          </div>
        </div>
      </div>`,
  data() {
    return {
      jqEl: null
    };
  },
  mounted() {
    let vm = this;

    vm.jqEl = $(this.$el);
  },
  methods: {
    closeModal() {
      this.jqEl.bootstrapModal('hide');
    }
  }

});


Vue.component('select2', {
  props: [ 'options', 'value', 'placeholder', 'inputlength' ],
  template: '#select2-template',
  mounted: function() {
    let vm = this;

    $(vm.$el).select2({
      data: vm.options,
      placeholder: vm.placeholder !== null ? vm.placeholder : 'filter here',
      minimumInputLength: vm.inputlength !== null ? vm.inputlength : 1})
      .val(vm.value)
      .trigger('change')
      .on('change', function() {
        vm.$emit('input', $(this).val());
      });
  },
  watch: {
    value: function(value) {
      if (value === undefined) {
        $(this.$el).empty().select2({data: this.options});
      } else if ([...value].sort().join(',') !== [...$(this.$el).val()].sort().join(',')) {
        $(this.$el).val(value).trigger('change');
      }
    },
    options: function(options) {
      $(this.$el).empty().select2({data: options});
    }
  },
  destroyed: function() {
    $(this.$el).off().select2('destroy');
  }
});

Vue.component('loading-screen', {
  template: `<div class="rhombus-spinner">
              <div class="rhombus child-1"></div>
              <div class="rhombus child-2"></div>
              <div class="rhombus child-3"></div>
              <div class="rhombus child-4"></div>
              <div class="rhombus child-5"></div>
              <div class="rhombus child-6"></div>
              <div class="rhombus child-7"></div>
              <div class="rhombus child-8"></div>
              <div class="rhombus big"></div>
            </div>`
});


Vue.component('qrcode', {
  props: ['string'],
  template: '<div class="qrcode"></div>',
  data() {
    return {
      jqEl: null,
      qrcode: null
    };
  },
  mounted() {
    let vm = this;

    vm.jqEl = $(this.$el);
    vm.qrcode = new QRCode(vm.jqEl[0], vm.string);
    return vm.qrcode;

    // document.getElementsByClassName("qrcode")[0].innerHTML = qr.createImgTag();
    // var qrcode = new QRCode(document.getElementById("qrcode"), {
    //   text: "http://jindo.dev.naver.com/collie",
    //   width: 128,
    //   height: 128,
    //   colorDark : "#000000",
    //   colorLight : "#ffffff",
    //   correctLevel : QRCode.CorrectLevel.H
    // });
    // qrcode.makeCode("http://naver.com")
  },
  watch: {
    string: function(string) {
      let vm = this;

      return vm.qrcode.makeCode(string);
    }
  },
  computed: {
    // normalizedSize: function () {
    //   console.log(vm.jqEl)
    // return new QRCode(vm.jqEl, "http://jindo.dev.naver.com/collie");
    //   // return this.size.trim().toLowerCase()
    // }
  }
});


Vue.component('tribes-settings', {
  delimiters: [ '[[', ']]' ],
  props: ['tribe'],
  data: function() {
    return {
      editorOptions: {
        priority: {
          modules: {
            toolbar: [
              [ 'bold', 'italic', 'underline' ],
              [{'align': []}],
              [{'list': 'ordered'}, {'list': 'bullet'}],
              [ 'link', 'code-block' ],
              ['clean']
            ]
          },
          theme: 'snow',
          placeholder: 'List out your tribe priorities to let contributors to know what they can request to work on'
        },
        description: {
          modules: {
            toolbar: [
              [ 'bold', 'italic', 'underline' ],
              [{'align': []}],
              [ 'link', 'code-block' ],
              ['clean']
            ]
          },
          theme: 'snow',
          placeholder: 'Describe your tribe so that people can follow you.'
        }
      }
    };
  },
  methods: {}
});

Vue.component('manage-mentors', {
  props: [ 'hackathon_id', 'org_name' ],
  methods: {
    onMentorChange: function(event) {

      this.bountyMentors = $('.mentor-users').select2('data').map(element => {
        return element.id;
      });
    },
    updateBountyMentors: function() {
      let vm = this;
      const url = '/api/v0.1/bounty_mentor/';

      const updateBountyMentor = fetchData(url, 'POST', JSON.stringify({
        bounty_org: vm.org_name,
        hackathon_id: vm.hackathon_id,
        set_default_mentors: true,
        new_default_mentors: vm.bountyMentors
      }), {'X-CSRFToken': vm.csrf, 'Content-Type': 'application/json; charset=utf-8'});

      $.when(updateBountyMentor).then((response) => {
        _alert({message: gettext(response.message)}, 'success');
      }).catch((error) => {
        _alert({message: gettext(error.message)}, 'error');
      });
    }
  },
  mounted() {
    userSearch('.mentor-users', false, undefined, false, false, true, {'select': this.onMentorChange, 'unselect': this.onMentorChange});
    this.bountyMentors = $('.mentor-users').select2('data').map(element => {
      return element.id;
    });

  },
  data: function() {
    return {
      csrf: $("input[name='csrfmiddlewaretoken']").val() || '',
      isFunder: false,
      funderBounties: [],
      bountyMentors: []
    };
  }
});

Vue.component('project-directory', {
  delimiters: [ '[[', ']]' ],
  props: [ 'tribe', 'userId' ],
  methods: {
    fetchProjects: function(newPage) {
      let vm = this;

      vm.isLoading = true;
      vm.noResults = false;

      if (newPage) {
        vm.projectsHasNext = null;
        vm.projectsPage = newPage;
      }

      if (vm.hackathonId) {
        vm.params.hackathon = hackathonId;
      }

      if (vm.sponsor) {
        vm.params.sponsor = vm.sponsor;
      }

      if (vm.searchTerm) {
        vm.params.search = vm.searchTerm;
      } else {
        delete vm.params['search'];
      }

      const searchParams = new URLSearchParams(vm.params);

      const apiUrlProjects = vm.projectsHasNext ? vm.projectsHasNext : `/api/v0.1/projects_fetch/?${searchParams.toString()}`;

      const getProjects = fetchData(apiUrlProjects, 'GET');

      $.when(getProjects).then(function(response) {
        response.results.forEach(function(item) {
          vm.hackathonProjects.push(item);
        });

        vm.userProjects = [];
        if (vm.userId) {
          vm.userProjects = vm.hackathonProjects.filter(
            ({profiles}) => profiles.some(
              ({id}) => id === parseInt(vm.userId, 10)
            )
          );
        }
        vm.projectsHasNext = response.next;

        vm.numProjects = response.count;

        if (vm.hackathonProjects.length) {
          vm.noResults = false;
        } else {
          vm.noResults = true;
        }
        vm.isLoading = false;
      });
    },
    searchProjects: function() {
      let vm = this;

      vm.hackathonProjects = [];

      vm.fetchProjects(1);

    },
    bottomVisible: function() { // TODO: abstract this to the mixin, and have it take a callback which modifies the component state.
      let vm = this;

      const scrollY = window.scrollY;
      const visible = document.documentElement.clientHeight;
      const pageHeight = document.documentElement.scrollHeight - 500;
      const bottomOfPage = visible + scrollY >= pageHeight;

      if (!vm.isLoading && (bottomOfPage || pageHeight < visible)) {
        if (vm.projectsHasNext) {
          vm.fetchProjects();
        }
      }
    }
  },
  data: function() {
    return {
      csrf: $("input[name='csrfmiddlewaretoken']").val() || '',
      sponsor: this.tribe || null,
      hackathonSponsors: document.hackathonSponsors || [],
      hackathonProjects: document.hackathonProjects || [],
      userProjects: document.userProjects || [],
      projectsPage: 1,
      hackathonId: document.hackathon_id || null,
      projectsHasNext: null,
      numProjects: 0,
      media_url,
      searchTerm: null,
      bottom: false,
      params: {
        filters: []
      },
      isFunder: false,
      showModal: false,
      showFilters: true,
      skills: document.keywords || [],
      selectedSkills: [],
      noResults: false,
      isLoading: true,
      hideFilterButton: false
    };
  },
  mounted() {
    this.fetchProjects();
    this.$watch('params', function(newVal, oldVal) {
      this.searchProjects();
    }, {
      deep: true
    });
  },
  created() {
    // this.extractURLFilters();
  },
  beforeMount() {
    if (this.isMobile) {
      this.showFilters = false;
    }
    window.addEventListener('scroll', () => {
      this.bottom = this.bottomVisible();
    }, false);
  },
  beforeDestroy() {
    window.removeEventListener('scroll', () => {
      this.bottom = this.bottomVisible();
    });
  },
  bottomVisible: function() { // TODO: abstract this to the mixin, and have it take a callback which modifies the component state.
    let vm = this;

    const scrollY = window.scrollY;
    const visible = document.documentElement.clientHeight;
    const pageHeight = document.documentElement.scrollHeight - 500;
    const bottomOfPage = visible + scrollY >= pageHeight;

    if (bottomOfPage || pageHeight < visible) {
      if (vm.projectsHasNext) {
        vm.projectsHasNext = false;
        vm.fetchProjects();
      }
    }
  }
});


Vue.component('showcase', {
  delimiters: [ '[[', ']]' ],
  props: [],
  data: function() {
    return {
      csrf: $("input[name='csrfmiddlewaretoken']").val() || '',
      hackathon: document.hackathonObj,
      isEditing: false,
      showcase: document.hackathonObj.showcase,
      top: document.hackathonObj.showcase.top || [{}, {}, {}],
      sponsors: document.hackathonSponsors,
      spotlights: document.hackathonObj.showcase.spotlights || [],
      prizes: document.hackathonObj.showcase.prizes || 0,
      is_staff: document.contxt.is_staff
    };
  },
  filters: {
    'markdownit': function(val) {
      if (!val)
        return '';
      const _markdown = new markdownit({
        linkify: true,
        highlight: function(str, lang) {
          if (lang && hljs.getLanguage(lang)) {
            try {
              return `<pre class="hljs"><code>${hljs.highlight(lang, str, true).value}</code></pre>`;
            } catch (__) {}
          }
          return `<pre class="hljs"><code>${sanitize(_markdown.utils.escapeHtml(str))}</code></pre>`;
        }
      });

      _markdown.renderer.rules.table_open = function() {
        return '<table class="table">';
      };
      ui_body = sanitize(_markdown.render(val));
      return ui_body;
    }
  },
  methods: {
    followTribe: function(handle, event) {
      event.preventDefault();
      let vm = this;

      const url = `/tribe/${handle}/join/`;
      const sendJoin = fetchData(url, 'POST', {}, {'X-CSRFToken': vm.csrf});

      $.when(sendJoin).then((response) => {
        if (response && response.is_member) {
          this.getSponsor(handle).followed = true;
        } else {
          this.getSponsor(handle).followed = false;
        }
      }).fail((error) => {
        console.log(error);
      });
    },
    getSponsor: function(handle) {
      return this.sponsors.filter(sponsor => sponsor.org_name === handle)[0] || {};
    },
    addSpotlight: function() {
      let vm = this;
      let spotlight = {
        sponsor: {},
        content: ''
      };

      if (vm.spotlights.length === 0) {
        vm.spotlights = [spotlight];
      } else {
        vm.spotlights.push(spotlight);
      }
    },
    removeSpotlight: function(index) {
      let vm = this;

      if (index > -1) {
        vm.spotlights.splice(index, 1);
      }
    },
    saveShowcase: function() {
      let vm = this;
      const resource_url = `/api/v0.1/hackathon/${document.hackathonObj.id}/showcase/`;
      const retrieveResources = fetchData(resource_url, 'POST', JSON.stringify({
        content: vm.showcase.content,
        top: vm.top,
        spotlights: vm.spotlights,
        prizes: vm.showcase.prizes
      }), {'X-CSRFToken': vm.csrf});

      vm.isEditing = false;


      $.when(retrieveResources).then((response) => {
        _alert('Showcase info saved', 'success', 1000);
      }).fail((error) => {
        console.log(error);
      });

    }
  },
  mounted() {
    if (!this.showcase.top) {
      this.showcase.top = [];
    }
  }
});

Vue.component('project-card', {
  delimiters: [ '[[', ']]' ],
  data: function() {
    return {
      csrf: $("input[name='csrfmiddlewaretoken']").val() || ''
    };
  },
  props: [ 'project', 'edit', 'is_staff' ],
  computed: {
    project_url: function() {
      let project = this.$props.project;
      let project_name = (project.name || '').replace(/ /g, '-');

      return `/hackathon/${project.hackathon.slug}/projects/${project.pk}/${project_name}`;
    }
  },
  methods: {
    markWinner: function($event, project) {
      let vm = this;

      const url = '/api/v0.1/hackathon_project/set_winner/';
      const markWinner = fetchData(url, 'POST', {
        project_id: project.pk,
        winner: $event ? 1 : 0
      }, {'X-CSRFToken': vm.csrf});

      $.when(markWinner).then(response => {
        if (response.message) {
          alert(response.message);
        }
      }).catch(err => {
        console.log(err);
      });
    },
    projectModal() {
      let project = this.$props.project;

      projectModal(project.bounty.pk, project.pk);
    }
  },
  template: `<div class="card card-user shadow-sm border-0">
    <div class="card card-project">
      <b-form-checkbox v-if="is_staff" switch v-model="project.winner" style="padding:0;float:left;" @change="markWinner($event, project)">mark winner</b-form-checkbox>
      <button v-on:click="projectModal" class="position-absolute btn btn-gc-green btn-sm m-2" id="edit-btn" v-bind:class="{ 'd-none': !edit }">edit</button>
      <img v-if="project.badge" class="position-absolute card-badge" width="50" :src="profile.badge" alt="badge" />
      <div class="card-bg rounded-top">
        <div v-if="project.winner" class="ribbon ribbon-top-right"><span>winner</span></div>
        <img v-if="project.logo" class="card-project-logo m-auto rounded shadow" height="87" width="87" :src="project.logo" alt="Hackathon logo" />
        <img v-else class="card-project-logo m-auto rounded shadow" height="87" width="87" :src="project.bounty.avatar_url" alt="Bounty Logo" />
      </div>
      <div class="card-body">
        <h5 class="card-title font-weight-bold text-left">[[ project.name ]]</h5>
        <div class="my-2">
          <p class="text-left text-muted font-smaller-1">
            [[ project.summary | truncate(500) ]]
          </p>
          <div class="text-left">
            <a :href="project_url" target="_blank" class="btn btn-sm btn-gc-blue font-smaller-2 font-weight-semibold">View Project</a>
            <a :href="project.bounty.url" class="btn btn-sm btn-outline-gc-blue font-smaller-2 font-weight-semibold">View Bounty</a>
            <b-dropdown variant="outline-gc-blue" toggle-class="btn btn-sm" split-class="btn-sm btn btn-gc-blue">
            <template v-slot:button-content>
              <i class='fas fa-comment-dots'></i>
            </template>
            <b-dropdown-item-button @click.prevent="chatWindow('@' +profile.handle);" v-for="profile in project.profiles" aria-describedby="dropdown-header-label" :key="profile.id">
              @ [[ profile.handle ]]
            </b-dropdown-item-button>
            </b-dropdown>
          </div>
        </div>

        <div class="my-3 mb-2 text-left">
          <b class="font-weight-bold font-smaller-3">Team Members</b>
          <div class="mt-1">
              <a v-for="profile in project.profiles" :href="'/profile/' + profile.handle">
                <b-img-lazy :src="profile.avatar_url" :alt="profile.handle" :title="profile.handle" width="30" height="30" class="rounded-circle"></b-img-lazy>
              </a>
          </div>
        </div>

        <div v-if="project.looking_members || project.message" class="my-3 looking-team">
          <h5 v-if="project.looking_members"  class="info-card-title uppercase">Looking for team members</h5>
          <p v-if="project.message" class="info-card-desc">
            [[ project.message ]]
          </p>
        </div>

        <div class="font-smaller-2 mt-4">
          <b class="font-weight-bold">Sponsored by</b>
          <img width="20" :src="project.bounty.avatar_url" :alt="project.bounty.org_name" />
          <a :href="/profile/[[project.bounty.org_name]]">[[ project.bounty.org_name ]]</a>
        </div>
      </div>
    </div>
  </div>`
});

Vue.component('suggested-profiles', {
  props: ['id'],
  data: function() {
    return {
      users: []
    };
  },
  mounted() {
    this.fetchUsers();
  },
  methods: {
    fetchUsers: function() {
      let vm = this;

      vm.isLoading = true;
      vm.noResults = false;

      let apiUrlUsers = `/api/v0.1/users_fetch/?user_filter=all&page=1&tribe=${vm.id}`;

      var getUsers = fetchData(apiUrlUsers, 'GET');

      $.when(getUsers).then(function(response) {
        for (let item = 0; response.data.length > item; item++) {
          if (!response.data[item].is_following) {
            if (response.data[item].handle != document.contxt.github_handle) {
              vm.users.push(response.data[item]);
            }
          }
          if (vm.users.length === 10) {
            break;
          }
        }

        if (vm.users.length) {
          vm.noResults = false;
        } else {
          vm.noResults = true;
        }
        vm.isLoading = false;
      });
    }
  },
  template: `<div class="townsquare_nav-list my-2 tribe">
      <div id="suggested-tribes">
        <ul class="nav d-inline-block font-body col-lg-4 col-lg-11 pr-2" style="padding-right: 0">
            <suggested-profile v-for="profile in users" :key="profile.id" :profile="profile" />
        </ul>
      </div>
    </div>`
});


Vue.component('suggested-profile', {
  props: ['profile'],
  data: function() {
    return {
      follow: this.profile.user_is_following || false
    };
  },
  computed: {
    avatar_url: function() {
      return `/dynamic/avatar/${this.profile.handle}`;
    },
    profile_url: function() {
      return `/profile/${this.profile.handle}`;
    }
  },
  methods: {
    followTribe: function(handle, event) {
      event.preventDefault();
      let vm = this;

      const url = `/tribe/${handle}/join/`;
      const sendJoin = fetchData(url, 'POST', {}, {'X-CSRFToken': vm.csrf});

      $.when(sendJoin).then((response) => {
        if (response && response.is_member) {
          vm.follow = true;
          vm.follower_count += 1;
        } else {
          vm.follow = false;
          vm.follower_count -= 1;
        }
      }).fail((error) => {
        console.log(error);
      });
    }
  },
  template: `
<b-media tag="li" class="row mx-auto mx-md-n1 mb-1">
  <template v-slot:aside>
    <a :href="profile_url" class="d-flex nav-link nav-line pr-0 mr-0">
      <b-img :src="avatar_url" class="nav_avatar"></b-img>
    </a>
  </template>
  <div class="col">
    <span class="row font-caption">
        <a :href="profile_url" class="nav-title font-weight-semibold pt-0 mb-0 text-capitalize text-black">{{profile.name}}</a>
        <p class="mb-0">
          <span class="font-weight-semibold">{{profile.handle}}</span>
        </p>
    </span>
    <p class="row font-caption mb-0 mt-1">
      <b-button v-if="follow" @click="followTribe(profile.handle, $event)" class="btn btn-outline-green font-smaller-5">following</b-button>
      <b-button v-else @click="followTribe(profile.handle, $event)" class="btn btn-gc-blue font-smaller-5">follow</b-button>
    </p>
  </div>
</b-media>
`
});


Vue.component('date-range-picker', {
  template: '#date-range-template',
  props: [ 'date', 'disabled' ],

  data: function() {
    return {
      newDate: this.date
    };
  },
  computed: {
    pickDate() {
      return this.newDate;
    }
  },
  mounted: function() {
    let vm = this;

    this.$nextTick(function() {
      window.$(this.$el).daterangepicker({
        singleDatePicker: true,
        startDate: moment().add(1, 'month'),
        alwaysShowCalendars: false,
        ranges: {
          '1 week': [ moment().add(7, 'days'), moment().add(7, 'days') ],
          '2 weeks': [ moment().add(14, 'days'), moment().add(14, 'days') ],
          '1 month': [ moment().add(1, 'month'), moment().add(1, 'month') ],
          '3 months': [ moment().add(3, 'month'), moment().add(3, 'month') ],
          '1 year': [ moment().add(1, 'year'), moment().add(1, 'year') ]
        },
        'locale': {
          'customRangeLabel': 'Custom',
          'format': 'MM/DD/YYYY'
        }
      }).on('apply.daterangepicker', function(e, picker) {
        vm.$emit('apply-daterangepicker', picker.startDate);
        vm.newDate = picker.startDate.format('MM/DD/YYYY');
      });
    });
  }

});
