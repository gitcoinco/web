Vue.mixin({
  data: function() {
    const isMobile = (/Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i).test(navigator.userAgent);

    return {
      isMobile
    };
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
  props: [ 'user', 'size', 'id', 'issueDetails', 'hideClose', 'backdrop', 'keyboard' ],
  template: `<div class="vue-modal modal fade" :id="id" :data-backdrop="propBackdrop" :data-keyboard="propKeyboard" tabindex="-1" role="dialog" aria-labelledby="userModalLabel" aria-hidden="true">
        <div class="modal-dialog modal-dialog-centered" :class="size" role="document">
          <div class="modal-content">
            <div class="modal-header border-0">
              <slot name="top"></slot>
              <button type="button" class="close" data-dismiss="modal" v-show="showClose" aria-label="Close">
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
  computed: {
    showClose() {
      if (!this.hideClose) {
        return true;
      }

      return false;
    },
    propKeyboard() {
      if (!this.keyboard) {
        return true;
      }

      return this.keyboard;
    },
    propBackdrop() {
      if (!this.backdrop) {
        return true;
      }

      return this.backdrop;

    }
  },
  methods: {
    closeModal() {
      this.jqEl.bootstrapModal('hide');
    },
    openModal() {
      this.jqEl.bootstrapModal('show');
    }
  }

});


Vue.component('select2', {
  props: [ 'options', 'value', 'placeholder', 'inputlength', 'sorter' ],
  template: '#select2-template',
  mounted: function() {
    let vm = this;
    let select2Options = {
      data: vm.options,
      placeholder: vm.placeholder !== null ? vm.placeholder : 'filter here',
      minimumInputLength: vm.inputlength !== null ? vm.inputlength : 1
    };

    if (vm.sorter) {
      select2Options['sorter'] = vm.sorter;
    }

    $(vm.$el).select2(select2Options)
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
  props: [ 'string', 'size' ],
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

    if (vm.size) {
      vm.qrcode = new QRCode(vm.jqEl[0], {
        text: vm.string,
        width: vm.size,
        height: vm.size
      });

    } else {
      vm.qrcode = new QRCode(vm.jqEl[0], vm.string);
    }
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
        _alert({message: gettext(error.message)}, 'danger');
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


Vue.component('events', {
  delimiters: [ '[[', ']]' ],
  props: [],
  data: function() {
    return {
      events: []
    };
  },
  methods: {
    nth: function(d) {
      if (d > 3 && d < 21)
        return 'th';
      switch (d % 10) {
        case 1: return 'st';
        case 2: return 'nd';
        case 3: return 'rd';
        default: return 'th';
      }
    },
    fetchEvents: async function() {
      const response = await fetchData(`/api/v0.1/hackathon/${document.hackathonObj.id}/events/`, 'GET');

      this.$set(this, 'events', response.events.events);
    },
    formatDate: function(event) {
      const monthNames = [
        'January', 'February', 'March', 'April', 'May', 'June',
        'July', 'August', 'September', 'October', 'November', 'December'
      ];
      const date = event.date_start.split('/');
      const time = event.date_start_time;
      const newDate = new Date(`${date[2]}-${date[0]}-${date[1]}T${time}`);
      const month = monthNames[newDate.getMonth()];
      const day = newDate.getDay();
      const hours = newDate.getHours();
      const ampm = event.date_start_ampm.toLowerCase();

      return `${month} ${day}${this.nth(newDate.getDay())}, ${hours} ${ampm}  ET`;
    },
    eventTag: function(event) {
      const text = event.eventname;

      if (text.includes('formation')) {
        return 'formation';
      } else if (text.includes('pitch')) {
        return 'pitch';
      } else if (text.includes('check')) {
        return 'check';
      } else if (text.includes('office')) {
        return 'office';
      } else if (text.includes('demo')) {
        return 'demo';
      }

      return 'workshop';
    }
  },
  mounted() {
    this.fetchEvents();
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
  methods: {
    projectModal() {
      let project = this.$props.project;

      projectModal(project.bounty.pk, project.pk);
    }
  },
  template: `<div class="card card-user border-0">
    <div class="card card-project">
      <button v-on:click="projectModal" class="position-absolute btn btn-success btn-sm m-2" style="left: 0.5rem; top: 3rem" id="edit-btn" v-bind:class="{ 'd-none': !edit }">edit</button>
      <img v-if="project.grant_obj" class="position-absolute" style="left: 1rem" src="${static_url}v2/images/grants/grants-tag.svg" alt="grant_tag"/>
      <img v-if="project.badge" class="position-absolute card-badge" width="50" :src="profile.badge" alt="badge" />
      <div class="card-bg rounded-top">
        <div v-if="project.winner" class="ribbon ribbon-top-right"><span>winner</span></div>
        <img v-if="project.logo" class="card-project-logo m-auto rounded shadow" height="87" width="87" :src="project.logo" alt="Hackathon logo" />
        <img v-else class="card-project-logo m-auto rounded shadow" height="87" width="87" :src="project.bounty.avatar_url" alt="Bounty Logo" />
      </div>
      <div class="card-body">
        <h5 class="card-title font-weight-bold text-left" v-html="project.name"></h5>
        <div class="my-2">
          <p class="text-left text-muted font-smaller-1">
            [[ project.summary | truncate(500) ]]
          </p>
          <div class="text-left">
            <a :href="project.url_project_page" target="_blank" class="btn btn-sm btn-primary font-smaller-2">View Project</a>
            <a :href="project.bounty.url" class="btn btn-sm btn-outline-primary font-smaller-2">View Bounty</a>
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
    <a :href="profile_url" class="d-flex nav-link nav-line px-0 mr-0">
      <b-img :src="avatar_url" class="profile-header__avatar mr-2"></b-img>
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
      <b-button v-if="follow" @click="followTribe(profile.handle, $event)" variant="success" class="btn font-smaller-5">following</b-button>
      <b-button v-else @click="followTribe(profile.handle, $event)" variant="primary" class="btn font-smaller-5">follow</b-button>
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


Vue.component('copy-clipboard', {
  props: ['string'],
  template: '<button @click="copy()" type="button"><slot>Copy</slot></button>',
  data() {
    return {

    };
  },
  methods: {
    copy() {
      if (!navigator.clipboard) {
        _alert('Could not copy text to clipboard', 'danger', 5000);
      } else {
        navigator.clipboard.writeText(this.string).then(function() {
          _alert('Text copied to clipboard', 'success', 4000);
        }, function(err) {
          _alert('Could not copy text to clipboard', 'danger', 5000);
        });
      }
    }
  }
});


Vue.component('render-quill', {
  props: ['delta'],
  template: '<div>{{this.renderHtml}}</div>',
  data() {
    return {
      jqEl: null,
      renderHtml: ''

    };
  },
  methods: {
    transform: function() {
      let vm = this;

      if (!vm.delta) {
        return;
      }

      vm.jqEl = this.$el;
      const quill = new Quill(vm.jqEl);

      quill.enable(false);
      vm.renderHtml = quill.setContents(JSON.parse(vm.delta));
    }

  },
  mounted() {
    this.transform();
  },
  watch: {
    delta: function() {
      return this.transform();
    }
  }
});


Vue.component('countdown', {
  props: [ 'startdate', 'enddate' ],
  template: `
    <div>
      <slot :time="time">{{time.days}}d {{time.hours}}h {{time.minutes}}m {{time.seconds}}s </slot>
    </div>`,
  data() {
    return {
      time: {},
      start: '',
      end: '',
      timeinterval: undefined
    };
  },
  methods: {
    initializeClock() {
      let vm = this;

      vm.updateClock();
      vm.timeinterval = setInterval(vm.updateClock, 1000);
      return vm.time;
    },
    updateClock() {
      let vm = this;
      const now = new Date().getTime();
      const distance = vm.start - now;
      const passTime = vm.end - now;
      let t;

      if (distance < 0 && passTime < 0) {
        vm.$set(vm.time, 'statusType', 'expired');
        clearInterval(this.timeinterval);
        return;
      } else if (distance < 0 && passTime > 0) {
        t = this.getTimeRemaining(passTime);
        vm.$set(vm.time, 'statusType', 'running');
      } else if (distance > 0 && passTime > 0) {
        t = this.getTimeRemaining(distance);
        vm.$set(vm.time, 'statusType', 'upcoming');
      }

      this.$set(vm.time, 'days', t.days);
      this.$set(vm.time, 'hours', ('0' + t.hours).slice(-2));
      this.$set(vm.time, 'minutes', ('0' + t.minutes).slice(-2));
      this.$set(vm.time, 'seconds', ('0' + t.seconds).slice(-2));

    },

    getTimeRemaining(dist) {
      const seconds = Math.floor((dist / 1000) % 60);
      const minutes = Math.floor((dist / 1000 / 60) % 60);
      const hours = Math.floor((dist / (1000 * 60 * 60)) % 24);
      const days = Math.floor(dist / (1000 * 60 * 60 * 24));

      return {
        days,
        hours,
        minutes,
        seconds
      };
    }
  },
  mounted() {
    this.start = new Date(this.startdate).getTime();
    this.end = new Date(this.enddate).getTime();
    this.initializeClock();
  }
});

Vue.component('activity-card', {
  template: '#activity-card',
  delimiters: [ '[[', ']]' ],
  props: [ 'data', 'index' ],
  data: function() {
    return {
      csrf: $("input[name='csrfmiddlewaretoken']").val() || '',
      github_handle: document.contxt.github_handle || '',
    };
  },
  methods: {
    fetchComments: async function(activityId) {
      let vm = this;
      if (!vm.data.comments.length || Object.keys(vm.data.comments[0]).length) {
        return;
      }
      let url = `/api/v0.1/activities/${activityId}/?fields=pk,comments&expand=comments`;

      const res = await fetch(url);
      const json = await res.json();


      vm.$set(vm.data, 'comments', json.comments);
      // vm.activities.map((activity, index) => {
      //   if (activity.includes(activityId))

      //     // activity.comments = json.comments;
      // });



    },
    postComment: async function() {
      let vm = this;
      let url = `/api/v0.1/activity/${vm.data.pk}`;
      let dataComment = {
        'method': 'comment',
        'comment': vm.data.newComment,
        'csrfmiddlewaretoken': vm.csrf
      }

      const res = await fetch(url, {
        method: 'post',
        body: dataComment
      });
      const json = await res.json();
      if (json) {
        vm.data.comments.push(json);

      }
    },
    editComment: async function(commentId) {
      let vm = this;
      let url = `/api/v0.1/comment/${commentId}`;
      const res = await fetch(url, {
        method: 'post',
        body: vm.data.comment
      });
      const json = await res.json();
      if (json) {
        vm.data.comments.push(json);

      }
    },
    deleteComment: function(commentId) {
      if (!confirm('Are you sure you want to delete this?')) {
        return;
      }
    },
    isOwner: function(commentIndex) {
      let vm = this;
      return document.contxt.github_handle == vm.data.comments[commentIndex].profile.handle;

    }
  },
  computed: {
    isCommentOwner() {
      if (!document.contxt.github_handle) {
        return;
      }
      return this.data.comments.reduce((acc, item) => {
        acc[item.id] = item.profile.handle == document.contxt.github_handle;
        console.log(acc)
        return acc;
      }, {});
    },


  }

})
