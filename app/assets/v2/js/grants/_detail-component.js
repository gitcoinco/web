
let isStaff = document.contxt.is_staff || false;

let userCode = typeof user_code !== 'undefined' ? user_code : undefined;
let verificationTweet = typeof verification_tweet !== 'undefined' ? verification_tweet : undefined;

Vue.component('v-select', VueSelect.VueSelect);
Vue.use(VueQuillEditor);
Quill.register('modules/ImageExtend', ImageExtend);


Vue.mixin({
  methods: {
    grantInCart: function() {
      let vm = this;
      let inCart = CartData.cartContainsGrantWithId(vm.grant.id);

      vm.$set(vm.grant, 'isInCart', inCart);
      return vm.grant.isInCart;
    },
    addToCart: async function() {
      let vm = this;
      const grantCartPayloadURL = `/grants/v1/api/${vm.grant.id}/cart_payload`;
      const response = await fetchData(grantCartPayloadURL, 'GET');

      vm.$set(vm.grant, 'isInCart', true);
      CartData.addToCart(response.grant);
      if (typeof showSideCart != 'undefined') {
        showSideCart();
      }

    },
    removeFromCart: function() {
      let vm = this;

      vm.$set(vm.grant, 'isInCart', false);
      CartData.removeIdFromCart(vm.grant.id);
      if (typeof showSideCart != 'undefined') {
        showSideCart();
      }

    },
    editGrantModal: function() {
      let vm = this;

      vm.logoPreview = vm.grant.logo_url;

      vm.$root.$emit('bv::toggle::collapse', 'sidebar-grant-edit');
    },
    saveGrant: function(event) {
      event.preventDefault();
      let vm = this;

      if (!vm.checkForm(event))
        return;

      const headers = {
        'X-CSRFToken': $("input[name='csrfmiddlewaretoken']").val()
      };

      const apiUrlGrant = `/grants/v1/api/grant/edit/${vm.grant.id}/`;
      let data = {
        'title': vm.grant.title,
        'reference_url': vm.grant.reference_url,
        'description': vm.$refs.myQuillEditor.quill.getText(),
        'description_rich': JSON.stringify(vm.$refs.myQuillEditor.quill.getContents()),
        'github_project_url': vm.grant.github_project_url,
        'team_members[]': JSON.stringify(vm.teamFormatted),
        'handle1': vm.grant.twitter_handle_1,
        'handle2': vm.grant.twitter_handle_2,
        'eth_payout_address': vm.grant.admin_address,
        'zcash_payout_address': vm.grant.zcash_payout_address,
        'region': vm.grant.region?.name || undefined
      };

      if (vm.logo) {
        data.logo = vm.logo;
      }

      if (vm.logoBackground) {
        data.image_css = `background-color: ${vm.logoBackground};`;
      }

      $.ajax({
        type: 'post',
        url: apiUrlGrant,
        processData: false,
        contentType: false,
        data: getFormData(data),
        headers: headers,
        success: response => {
          if (response.status == 200) {
            vm.grant.logo_url = vm.logoPreview;
            vm.grant.last_update = new Date();
            vm.grant.description_rich = JSON.stringify(vm.$refs.myQuillEditor.quill.getContents());
            vm.grant.description = vm.$refs.myQuillEditor.quill.getText();
            vm.grant.image_css = `background-color: ${vm.logoBackground};`;
            vm.$root.$emit('bv::toggle::collapse', 'sidebar-grant-edit');
            _alert('Updated grant.', 'success');

            if (typeof ga !== 'undefined') {
              ga('send', 'event', 'Edit Grant', 'click', 'Grant Editor');
            }
          } else {
            // vm.submitted = false;
            _alert('Unable to edit grant. Please try again', 'error');
            console.error(`error: grant edit failed with status: ${response.status} and message: ${response.message}`);
          }
        },
        error: err => {
          // vm.submitted = false;
          _alert('Unable to edit grant. Please try again', 'error');
          console.error(`error: grant edit failed with msg ${err}`);
        }
      });

    },
    cancelGrant: function(event) {
      event.preventDefault();

      let vm = this;

      let cancel = window.prompt('Please write "CONFIRM" to cancel the grant.');

      if (cancel !== 'CONFIRM') {
        return;
      }

      if (typeof ga !== 'undefined') {
        ga('send', 'event', 'Cancel Grant', 'click', 'Grant Cancel');
      }

      const cancelUrl = `/grants/v1/api/grant/${vm.grant.id}/cancel`;
      var cancelGrant = fetchData(cancelUrl, 'POST');

      $.when(cancelGrant).then(function(response) {
        vm.grant.active = false;
        vm.$root.$emit('bv::toggle::collapse', 'sidebar-grant-edit');
        _alert('Grant cancelled', 'success');
        return response;
      });

    },
    toggleFollowingGrant: async function(grantId) {
      let vm = this;

      const favoriteUrl = `/grants/${grantId}/favorite`;
      let response = await fetchData(favoriteUrl, 'POST');

      if (response.action === 'follow') {
        vm.grant.favorite = true;
      } else {
        vm.grant.favorite = false;
      }

      return true;
    },
    flag: function() {
      let vm = this;


      const comment = prompt('What is your reason for flagging this Grant?');

      if (!comment) {
        return;
      }

      if (!document.contxt.github_handle) {
        _alert({ message: gettext('Please login.') }, 'error', 1000);
        return;
      }

      const data = {
        'csrfmiddlewaretoken': $('input[name=csrfmiddlewaretoken]').val(),
        'comment': comment
      };

      $.ajax({
        type: 'post',
        url: `/grants/flag/${vm.grant.id}`,
        data,
        success: function(json) {
          _alert({ message: gettext('Your flag has been sent to Gitcoin.') }, 'success', 1000);
        },
        error: function() {
          _alert({ message: gettext('Your report failed to save Please try again.') }, 'error', 1000);
        }
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
              // vm.$set(vm.form, 'team_members', vm.usersOptions[0].text);
            }
            resolve();
          });
          if (loading) {
            loading(false);
          }
        });
      });
    },
    changeColor() {
      let vm = this;

      vm.grant.image_css = `background-color: ${vm.logoBackground};`;
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
      vm.imgTransition = true;
      let imgCompress = new Compressor(file, {
        quality: 0.6,
        maxWidth: 2000,
        success(result) {
          vm.logoPreview = URL.createObjectURL(result);
          vm.logo = new File([result], result.name, { lastModified: result.lastModified });
          vm.imgTransition = false;
        },
        error(err) {
          vm.imgTransition = false;
          console.log(err.message);
        }
      });
    },
    async twitterVerification() {
      let vm = this;

      if (!vm.grant.twitter_handle_1 || vm.grant.twitter_handle_1 == '') {
        _alert('Please add a twitter account to your grant!', 'error', 5000);
        return;
      }

      const response = await fetchData(`/grants/v1/api/${vm.grant.id}/verify`);

      if (!response.ok) {
        _alert(response.msg, 'error');
        return;
      }
      if (response.verified) {
        _alert('Congratulations, your grant is now verified!', 'success', 5000);
        vm.grant.verified = true;
        vm.$refs['twitterVerification'].hide();
      }

      if (!response.has_text) {
        _alert(`Unable to verify tweet from ${vm.grant.twitter_handle_1}.  Is the twitter post live?  Was it sent from ${vm.grant.twitter_handle_1}?`, 'error', 5000);
        return;
      }

      if (!response.has_code) {
        _alert(`Missing emoji code "${user_code}", please don't remove this unique code before validate your grant.`, 'error', 5000);
        return;
      }

    },
    isTwitterUrl(input) {
      const twitter_re = /^https?:\/\/(www\.)?twitter\.com\/(#!\/)?([^/]+)(\/\w+)*$/;
      const twitter_match = input.match(twitter_re);

      if (twitter_match) {
        return twitter_match[3];
      }
    },
    transformTwitterHandle1() {
      const match_twitter = this.isTwitterUrl(this.grant.twitter_handle_1);

      if (match_twitter) {
        this.grant.twitter_handle_1 = match_twitter;
      }
    },
    transformTwitterHandle2() {
      const match_twitter = this.isTwitterUrl(this.grant.twitter_handle_2);

      if (match_twitter) {
        this.grant.twitter_handle_2 = match_twitter;
      }
    },
    tweetVerification() {
      let vm = this;
      const tweetContent = `https://twitter.com/intent/tweet?text=${encodeURIComponent(vm.verification_tweet)}%20${encodeURIComponent(vm.user_code)}`;

      window.open(tweetContent, '_blank');
    },
    checkForm: function(e) {
      let vm = this;

      vm.submitted = true;
      vm.errors = {};
      if (!vm.grant.title.length) {
        vm.$set(vm.errors, 'title', 'Please enter the title');
      }
      if (!vm.grant.reference_url.length) {
        vm.$set(vm.errors, 'reference_url', 'Please enter link to the project');
      }
      if (!vm.grant.twitter_handle_1.length) {
        vm.$set(vm.errors, 'twitter_handle_1', 'Please enter twitter handle of your project');
      }
      if (vm.grant.twitter_handle_1 && !(/^@?[a-zA-Z0-9_]{1,15}$/).test(vm.grant.twitter_handle_1)) {
        vm.$set(vm.errors, 'twitter_handle_1', 'Please enter a valid twitter handle of your project e.g humanfund');
      }
      if (vm.grant.twitter_handle_2 && !(/^@?[a-zA-Z0-9_]{1,15}$/).test(vm.grant.twitter_handle_2)) {
        vm.$set(vm.errors, 'twitter_handle_2', 'Please enter your twitter handle e.g georgecostanza');
      }
      if (vm.grant.description_rich_edited.length < 10) {
        vm.$set(vm.errors, 'description', 'Please enter description for the grant');
      }

      if (!vm.$refs.formEditGrant.reportValidity()) {
        return false;
      }

      if (Object.keys(vm.errors).length) {
        return false; // there are errors the user must correct
      }
      vm.submitted = false;
      return true; // no errors, continue to create grant
    }
  },
  computed: {
    teamFormatted: {
      get() {
        return this.grant.team_members.map((user)=> {
          if (!user?.fields) {
            return user;
          }
          let newTeam = {};

          newTeam['id'] = user.pk;
          newTeam['avatar_url'] = `/dynamic/avatar/${user.fields.handle}`;
          newTeam['text'] = user.fields.handle;
          return newTeam;
        });

      },
      set(value) {
        this.grant.team_members = value;
      }
    },
    editor() {
      if (!this.$refs.myQuillEditor) {
        return;
      }
      return this.$refs.myQuillEditor.quill;
    },
    filteredMsg: function() {
      let msgs = [
        '💪 keep up the great work',
        '👍 i appreciate you',
        '🙌 Great Job',
        '😍 love the mission of your project'
      ];

      if (!this.grant?.metadata?.wall_of_love) {
        return;
      }

      return this.grant?.metadata?.wall_of_love.filter((msg) => {
        if (msgs.includes(msg[0])) {
          return msg;
        }
      });
    },
    itemsForList() {
      if (this.grant.metadata && !Object.keys(this.grant.metadata).length) {
        return;
      }
      this.rows = this.grant?.metadata?.wall_of_love.length || 0;
      return this.grant?.metadata?.wall_of_love.slice(
        (this.currentPage - 1) * this.perPage,
        this.currentPage * this.perPage
      );
    },
    isUserLogged() {
      let vm = this;

      if (document.contxt.github_handle) {
        return true;
      }
    }
  }
});


Vue.component('grant-details', {
  delimiters: [ '[[', ']]' ],

  props: {
    grant: {
      type: Object
    },
    fullview: {
      type: Boolean,
      'default': true
    }
  },
  template: '#template-grant-details',
  data() {
    return {
      dirty: false,
      submitted: false,
      user_code: userCode,
      verification_tweet: verificationTweet,
      imgTransition: false,
      isStaff: isStaff,
      logo: null,
      logoPreview: null,
      logoBackground: null,
      relatedGrants: [],
      rows: 0,
      perPage: 4,
      currentPage: 1,
      openEdit: false,
      errors: {},
      usersOptions: [],
      editorOptionPrio: {
        modules: {
          toolbar: {
            container: [
              [ 'bold', 'italic', 'underline' ],
              [{ 'align': [] }],
              [{ 'list': 'ordered'}, { 'list': 'bullet' }],
              [ 'link', 'code-block', 'image', 'video' ],
              ['clean']
            ],
            handlers: {
              'image': function() {
                QuillWatch.emit(this.quill.id);
              }
            }
          },
          ImageExtend: {
            loading: true,
            name: 'img',
            headers: (xhr) => {
              xhr.setRequestHeader('X-CSRFToken', $("input[name='csrfmiddlewaretoken']").val());
            },

            action: '/api/v1/file_upload/',
            response: (res) => {
              return res.url;
            }
          }
        },
        theme: 'snow',
        placeholder: 'Give a detailed desciription about your Grant'
      },
      grantRegions: [
        { 'name': 'north_america', 'label': 'North America'},
        { 'name': 'oceania', 'label': 'Oceania'},
        { 'name': 'latin_america', 'label': 'Latin America'},
        { 'name': 'europe', 'label': 'Europe'},
        { 'name': 'africa', 'label': 'Africa'},
        { 'name': 'middle_east', 'label': 'Middle East'},
        { 'name': 'india', 'label': 'India'},
        { 'name': 'east_asia', 'label': 'East Asia'},
        { 'name': 'southeast_asia', 'label': 'Southeast Asia'}
      ]
    };
  },
  mounted: function() {
    let vm = this;

    vm.grant.description_rich_edited = vm.grant.description_rich;
    if (vm.grant.description_rich_edited) {
      vm.editor.updateContents(JSON.parse(vm.grant.description_rich));
    }
    vm.grantInCart();
  },
  watch: {
    grant: {
      deep: true,
      handler: function(newVal, oldVal) {
        let vm = this;

        if (this.dirty && this.submitted) {
          this.checkForm();
        }
        this.dirty = true;
      }
    }
  }
});

const getFormData = object => {
  const formData = new FormData();

  Object.keys(object).forEach(key => formData.append(key, object[key]));
  return formData;
};
