Vue.mixin({
  data: function() {
    const isMobile = (/Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i).test(navigator.userAgent);

    return {
      isMobile,
      chatURL: document.chatURL || 'https://chat.gitcoin.co'
    };
  },
  methods: {
    chatWindow: function(channel, dm) {
      dm = dm || channel ? channel.indexOf('@') >= 0 : false;
      channel = channel || 'town-square';
      let vm = this;
      const hackathonTeamSlug = 'hackathons';
      const gitcoinTeamSlug = 'gitcoin';
      const isHackathon = (document.hackathon_id !== null);


      const url = `${vm.chatURL}/${isHackathon ? hackathonTeamSlug : gitcoinTeamSlug}/${dm ? 'messages' : 'channels'}/${dm ? '@' + channel : channel}`;

      window.open(url, 'Loading', 'top=0,left=0,width=400,height=600,status=no,toolbar=no,location=no,menubar=no,titlebar=no');
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
  props: [ 'options', 'value' ],
  template: '#select2-template',
  mounted: function() {
    let vm = this;

    $(this.$el).select2({data: this.options})
      .val(this.value)
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
              [{ 'align': [] }],
              [{ 'list': 'ordered'}, { 'list': 'bullet' }],
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
              [{ 'align': [] }],
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


Vue.component('project-directory', {
  delimiters: [ '[[', ']]' ],
  props: [ 'tribe', 'userId' ],
  methods: {
    fetchProjects: function(newPage) {
      let vm = this;

      vm.isLoading = true;
      vm.noResults = false;

      if (newPage) {
        vm.projectsPage = newPage;
      }

      vm.params.page = vm.projectsPage;

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

      const apiUrlProjects = `/api/v0.1/projects_fetch/?${searchParams.toString()}`;

      const getProjects = fetchData(apiUrlProjects, 'GET');

      $.when(getProjects).then(function(response) {
        vm.hackathonProjects = [];
        response.results.forEach(function(item) {
          vm.hackathonProjects.push(item);
        });

        vm.userProjects = [];
        if (vm.userId) {
          vm.userProjects = vm.hackathonProjects.filter(
            ({ profiles }) => profiles.some(
              ({ id }) => id === parseInt(vm.userId, 10)
            )
          );
        }
        vm.projectsNumPages = response.count;
        vm.projectsHasNext = response.next;

        vm.numProjects = response.count;
        if (vm.projectsHasNext) {
          vm.projectsPage = ++vm.projectsPage;

        } else {
          vm.projectsPage = 1;
        }

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
      projectsNumPages: 0,
      projectsHasNext: false,
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

Vue.component('project-card', {
  delimiters: [ '[[', ']]' ],
  data: function() {
    return {
      csrf: $("input[name='csrfmiddlewaretoken']").val() || ''
    };
  },
  props: [ 'project', 'edit', 'is_staff' ],
  methods: {
    markWinner: function($event, project) {
      let vm = this;

      const url = '/api/v0.1/hackathon_project/set_winner/';
      const markWinner = fetchData(url, 'POST', {project_id: project.pk, winner: $event ? 1 : 0}, {'X-CSRFToken': vm.csrf});

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
            <a :href="project.work_url" target="_blank" class="btn btn-sm btn-gc-blue font-smaller-2 font-weight-semibold">View Project</a>
            <a :href="project.bounty.url" class="btn btn-sm btn-outline-gc-blue font-smaller-2 font-weight-semibold">View Bounty</a>
            <b-dropdown variant="outline-gc-blue" toggle-class="btn btn-sm" split-class="btn-sm btn btn-gc-blue">
            <template v-slot:button-content>
              <i class='fas fa-comment-dots'></i>
            </template>
            <b-dropdown-item-button v-if="project.chat_channel_id" @click.prevent="chatWindow(project.chat_channel_id);" aria-describedby="dropdown-header-label" :key="project.chat_channel_id || project.id">
              Chat With Team
            </b-dropdown-item-button>
            <b-dropdown-item-button @click.prevent="chatWindow(profile.handle, true);" v-for="profile in project.profiles" aria-describedby="dropdown-header-label" :key="profile.id">
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
  props: ['profiles'],
  template: `<div class="townsquare_nav-list my-2 tribe">
      <div id="suggested-tribes">
        <ul class="nav d-inline-block font-body col-lg-4 col-lg-11 pr-2" style="padding-right: 0">
            <suggested-profile v-for="profile in profiles" :key="profile.id" :profile="profile" />
        </ul>
      </div>
    </div>`
});


Vue.component('suggested-profile', {
  props: ['profile'],
  data: function() {
    return {
      follow: this.profile.user_is_following || false,
      follower_count: this.profile.followers_count || 0
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
<b-media tag="li" class="row mx-auto mx-md-n1">
  <template v-slot:aside>
    <a :href="profile_url" class="d-flex nav-link nav-line pr-0 mr-0">
      <b-img :src="avatar_url" class="nav_avatar"></b-img>
    </a>
  </template>
  <div class="row">
    <span class="col-6 col-md-12 col-xl-7 font-caption">
        <a :href="profile_url" class="nav-title font-weight-semibold pt-0 mb-0 text-capitalize text-black">{{profile.name}}</a>
        <p class="mb-0">
          <i class="fas fa-user font-smaller-4 mr-1"></i>
          <span class="font-weight-semibold">{{follower_count}}</span> followers
        </p>
    </span>
    <span class="col-6 col-md-12 col-xl-5 p-0 my-auto text-center">
      <a class="follow_tribe btn btn-sm btn-outline-green font-weight-bold font-smaller-6 px-3" href="#" @click="followTribe(profile.handle, $event)" v-if="follow">
        <i v-bind:class="[follow ? 'fa-user-minus' : 'fa-user-plus', 'fas mr-1']"></i> following
      </a>
      <a class="follow_tribe btn btn-sm btn-gc-blue font-weight-bold font-smaller-6 px-3" href="#" @click="followTribe(profile.handle, $event)" v-else>
        <i v-bind:class="[follow ? 'fa-user-minus' : 'fa-user-plus', 'fas mr-1']"></i> follow
      </a>
    </span>
  </div>
</b-media>
`
});
