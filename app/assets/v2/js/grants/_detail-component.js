
let isStaff = document.contxt.is_staff || false;

let userCode = typeof user_code !== 'undefined'? user_code : undefined;
let verificationTweet = typeof verification_tweet !== 'undefined'? verification_tweet : undefined;

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
      if (typeof showSideCart != 'undefined') {showSideCart()}

    },
    removeFromCart: function() {
      let vm = this;

      vm.$set(vm.grant, 'isInCart', false);
      CartData.removeIdFromCart(vm.grant.id);
      if (typeof showSideCart != 'undefined') {showSideCart()}

    },
    editGrantModal: function() {
      let vm = this;
      vm.grant.description_rich_edited = vm.grant.description_rich;
      vm.editor.updateContents(JSON.parse(vm.grant.description_rich));
      vm.logoPreview = vm.grant.logo_url;

      vm.$root.$emit('bv::toggle::collapse', 'sidebar-grant-edit');
    },
    saveGrant: function(event) {
      event.preventDefault();
      let vm = this;

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
        'team_members[]': JSON.stringify(vm.grant.team_members),
        'handle1': vm.grant.twitter_handle_1,
        'handle2': vm.grant.twitter_handle_2,
        'eth_payout_address': vm.grant.eth_payout_address,
        'zcash_payout_address': vm.grant.zcash_payout_address,
        'region': vm.grant.region?.name || undefined
      };
      if (vm.logo) {
        data.logo = vm.logo;
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
            vm.grant.description_rich = JSON.stringify(vm.$refs.myQuillEditor.quill.getContents());
            vm.grant.description = vm.$refs.myQuillEditor.quill.getText();
            vm.$root.$emit('bv::toggle::collapse', 'sidebar-grant-edit');
            _alert('Updated grant.', 'success');

            if (typeof ga !== 'undefined') {
              ga('send', 'event', 'Edit Grant', 'click', 'Grant Editor');
            }
          } else {
            // vm.submitted = false;
            _alert('Unable to create grant. Please try again', 'error');
            console.error(`error: grant creation failed with status: ${response.status} and message: ${response.message}`);
          }
        },
        error: err => {
          // vm.submitted = false;
          _alert('Unable to create grant. Please try again', 'error');
          console.error(`error: grant creation failed with msg ${err}`);
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
        return response;
      });

    },
    checkGrantData: function() {
      return;
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
    onEditorBlur(quill) {
      console.log('editor blur!', quill);
    },
    onEditorFocus(quill) {
      console.log('editor focus!', quill);
    },
    onEditorReady(quill, html, text) {
      console.log('editor ready!', quill, html, text);
    },
    onEditorChange({ quill, html, text }) {
      console.log('editor change!', quill, html, text);
      this.content = html;
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
              vm.$set(vm.form, 'team_members', vm.usersOptions[0].text);
            }
            resolve();
          });
          if (loading) {
            loading(false);
          }
        });
      });
    },
    onFileChange(e) {
      console.log(e)
      let vm = this;

      if (!e.target) return;
      const file = e.target.files[0];
      console.log(file)

      if (!file) {
        return;
      }
      vm.imgTransition = true;
      new Compressor(file, {
        quality: 0.6,
        maxWidth: 2000,
        success(result) {
          vm.logoPreview = URL.createObjectURL(result);
          vm.logo = new File([result], result.name, { lastModified: result.lastModified })
          vm.imgTransition = false;
        },
        error(err) {
          vm.imgTransition = false;
          console.log(err.message);
        },
      });
    },
    async twitterVerification() {
      let vm = this;

      if (!vm.grant.twitter_handle_1 || vm.grant.twitter_handle_1 == ''){
        _alert('Please add a twitter account to your grant!', 'error', 5000);
        return;
      }

      const response = await fetchData(`/grants/v1/api/${vm.grant.id}/verify`);

      if (!response.ok) {
        _alert(response.msg, 'error');
        return;
      }
      if (response.verified) {
        _alert('Congratulations, your grant is now verified!', 'success', 5000)
        vm.grant.verified = true
        vm.$refs['twitterVerification'].hide()
      }

      if (!response.has_text) {
        _alert(`Unable to verify tweet from ${vm.grant.twitter_handle_1}.  Is the twitter post live?  Was it sent from ${vm.grant.twitter_handle_1}?`, 'error', 5000)
        return;
      }

      if (!response.has_code) {
        _alert(`Missing emoji code "${user_code}", please don't remove this unique code before validate your grant.`, 'error', 5000)
        return;
      }

    },
    tweetVerification() {
      let vm = this;
      const tweetContent =`https://twitter.com/intent/tweet?text=${encodeURI(vm.verification_tweet)}%20${encodeURI(vm.user_code)}`
      window.open(tweetContent, '_blank')
    }
  },
  computed: {
    teamFormatted: {
      get() {
        return this.grant.team_members.map((user)=> {
          console.log(user)
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
        this.grant.team_members = value
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
    }

  }
});


Vue.component('grant-details', {
  delimiters: [ '[[', ']]' ],

  props: ['grant'],
  template: '#template-grant-details',
  data() {
    return {
      user_code: userCode,
      verification_tweet: verificationTweet,
      imgTransition: false,
      isStaff: isStaff,
      logo: null,
      logoPreview: null,
      // grant: {},
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

    vm.grantInCart();
  }

})





const getFormData = object => {
  const formData = new FormData();

  Object.keys(object).forEach(key => formData.append(key, object[key]));
  return formData;
};
