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


Vue.component('project-directory', {
  delimiters: [ '[[', ']]' ],
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
  data: () => ({
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
  }),
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
