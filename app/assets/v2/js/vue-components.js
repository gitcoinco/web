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
  methods: {},
  mounted() {

  }
});


Vue.component('project-directory', {
  delimiters: [ '[[', ']]' ],
  props: ['tribe'],
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

      let searchParams = new URLSearchParams(vm.params);

      let apiUrlProjects = `/api/v0.1/projects_fetch/?${searchParams.toString()}`;

      var getProjects = fetchData(apiUrlProjects, 'GET');

      $.when(getProjects).then(function(response) {
        vm.hackathonProjects = [];
        response.data.forEach(function(item) {
          vm.hackathonProjects.push(item);
        });

        vm.projectsNumPages = response.num_pages;
        vm.projectsHasNext = response.has_next;
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
      sponsor: this.tribe || null,
      hackathonSponsors: document.hackathonSponsors || [],
      hackathonProjects: document.hackathonProjects || [],
      projectsPage: 1,
      hackathonId: document.hackathon_id || null,
      projectsNumPages: 0,
      projectsHasNext: false,
      numProjects: 0,
      media_url,
      searchTerm: null,
      bottom: false,
      params: {},
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
    window.addEventListener('scroll', () => {
      this.bottom = this.bottomVisible();
    }, false);
  },
  beforeDestroy() {
    window.removeEventListener('scroll', () => {
      this.bottom = this.bottomVisible();
    });
  }
});


Vue.component('suggested-profiles', {
  props: ['profiles'],
  template: `<div class="townsquare_nav-list my-2 tribe">
      <div id="suggested-tribes">
        <ul class="nav d-inline-block font-body col-4 col-sm-11 pr-2" style="padding-right: 0">
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
    <li class="nav-item d-flex justify-content-between align-items-center my-2">
      <a :href="profile_url" class="d-flex nav-link nav-line pr-0 mr-0">
        <img :src="avatar_url" class="nav_avatar mr-4" />
        <span class="font-caption">
          <span class="nav-title font-weight-semibold pt-0 mb-0 text-capitalize">{{profile.name}}</span><br>
          <p class="mb-0">
            <i class="fas fa-user font-smaller-4 mr-1"></i>
            <span class="font-weight-semibold">{{follower_count}}</span> followers
          </p>
        </span>
      </a>
      <a class="follow_tribe btn btn-sm btn-gc-pink font-weight-bold font-smaller-6 px-3" href="#" @click="followTribe(profile.handle, $event)" v-if="follow">
        following
      </a>
      <a class="follow_tribe btn btn-sm btn-gc-blue font-weight-bold font-smaller-6 px-3" href="#" @click="followTribe(profile.handle, $event)" v-else>
        follow
      </a>
    </li>`
});
