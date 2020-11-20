Vue.component('v-select', VueSelect.VueSelect);
Vue.use(VueQuillEditor);

Vue.mixin({
  methods: {
    fetchGrantDetails: function(id) {
      let vm = this;

      if (!id) {
        id = grantDetails.grant_id;
      }

      let url = `/grants/v1/api/grant/${id}/`;
      // var getdata = fetchData (url, 'GET');

      // $.when(getdata).then(function(response) {
      //   vm.grant = response.grants;
      // })
      return new Promise(resolve => {

        fetch(url).then(function(res)  {
          return res.json();


        }).then(function(json) {
          json.grants.team_members = vm.formatTeam(json.grants.team_members);
          vm.grant = json.grants
          vm.grantInCart();

          // vm.grant.description_rich_copy = JSON.parse(vm.grant.description_rich)
          // vm.grant.description_rich_copy = vm.editor.getContents(vm.grant.description_rich)
          vm.grant.description_rich_edited = vm.grant.description_rich
          // vm.grant.description_rich_copy = vm.editor.container.innerHTML
          console.log(vm.editor)
          // let html = vm.editor.updateContents(JSON.parse(vm.grant.description_rich_copy))
      // console.log(vm.editor.setContents(html))

        vm.editor.updateContents(JSON.parse(vm.grant.description_rich))
          // var contents = quill.getContents();
          // vm.grant.description_rich = vm.editor.updateContents(JSON.parse(vm.grant.description_rich))

    //       var tempCont = document.createElement("div");
    // (new Quill(tempCont)).setContents(vm.grant.description_rich);
    // console.log(tempCont)
    // return tempCont.getElementsByClassName("ql-editor")[0].innerHTML;
          // console.log(vm.editor.getContents(JSON.parse(vm.grant.description_rich))  )

          // if (vm.grant.metadata.related[0].length) {
          //   vm.fetchRelated(String(vm.grant.metadata.related[0]))
          // }

          resolve()
        }).catch(console.error)
      })


    },
    formatTeam: function(teamMembers) {
      return teamMembers.map((user)=> {
        let newTeam = {};
        newTeam["id"] = user.pk;
        newTeam["avatar_url"] = `/dynamic/avatar/${user.fields.handle}`;
        newTeam["text"] = user.fields.handle;
        return newTeam;
      });

    },
    fetchRelated: function() {
      let vm = this;
      let ids;

      if (!vm.grant.metadata.related.length || vm.relatedGrants.length) {
        return;
      }

      ids = vm.grant.metadata.related.map(arr => {return arr[0];});
      idsString = String(ids);

      let url = `http://localhost:8000/grants/v1/api/grants?pks=${idsString}`
      fetch(url).then(function(res)  {
        return res.json();
      }).then(function(json) {
        vm.relatedGrants = json.grants;

      }).catch(console.error)
    },
    grantInCart: function() {
      let vm = this;
      let inCart = CartData.cartContainsGrantWithId(vm.grant.id);
      console.log(inCart, vm.grant.id)

      vm.$set(vm.grant, 'isInCart', inCart);
      return vm.grant.isInCart;
    },
    addToCart: async function() {
      let vm = this;
      const grantCartPayloadURL = `/grants/v1/api/${vm.grant.id}/cart_payload`;
      const response = await fetchData(grantCartPayloadURL, 'GET');

      vm.$set(vm.grant, 'isInCart', true);
      CartData.addToCart(response.grant);
    },
    removeFromCart: function() {
      let vm = this;
      console.log('removeFromCart')
      vm.$set(vm.grant, 'isInCart', false);
      CartData.removeIdFromCart(vm.grant.id);
    },
    editGrantModal: function() {
      let vm = this;
      vm.$root.$emit('bv::toggle::collapse', 'sidebar-backdrop')
    },
    saveGrant: function(event) {
      event.preventDefault();
      let vm = this;

      vm.$root.$emit('bv::toggle::collapse', 'sidebar-backdrop')

      if (typeof ga !== 'undefined') {
        ga('send', 'event', 'Edit Grant', 'click', 'Grant Editor');
      }

      const headers = {
        'X-CSRFToken': $("input[name='csrfmiddlewaretoken']").val()
      };

      const apiUrlGrant = `/grants/v1/api/grant/edit/${vm.grant.id}/`;
      let data = {
        'title': vm.grant.title,
        'reference_url': vm.grant.reference_url,
        // 'logo': vm.logo,
        'description': vm.$refs.myQuillEditor.quill.getText(),
        'description_rich': JSON.stringify(vm.$refs.myQuillEditor.quill.getContents()),
        'github_project_url': vm.grant.github_project_url,
        'team_members[]': JSON.stringify(vm.grant.team_members),
        'handle1': vm.grant.twitter_handle_1,
        'handle2': vm.grant.twitter_handle_2,
        'eth_payout_address': vm.grant.eth_payout_address,
        'zcash_payout_address': vm.grant.zcash_payout_address,
        'region': vm.grant.region.name,


      };

      vm.grant.description_rich=JSON.stringify(vm.$refs.myQuillEditor.quill.getContents())
      vm.grant.description=vm.$refs.myQuillEditor.quill.getText()

      $.ajax({
        type: 'post',
        url: apiUrlGrant,
        processData: false,
        contentType: false,
        data: getFormData(data),
        headers: headers,
        success: response => {
          if (response.status == 200) {

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
    checkGrantData: function() {},
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
      console.log('editor blur!', quill)
    },
    onEditorFocus(quill) {
      console.log('editor focus!', quill)
    },
    onEditorReady(quill, html, text) {
      console.log('editor ready!', quill, html, text)

      // this.grant.description_rich = html
    },
    onEditorChange({ quill, html, text }) {
      console.log('editor change!', quill, html, text)
      this.content = html
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
  },
  computed: {
    // teamUsers: function() {

    //   let vm = this;

    //   if (!vm.grant.team_members) {
    //     return;
    //   }


    //   team_members_id = vm.grant.team_members.map((user)=> {
    //     console.log(user)
    //     let newTeam = {};
    //     newTeam["id"] = user.pk;
    //     newTeam["avatar_url"] = `/dynamic/avatar/${user.fields.handle}`;
    //     newTeam["text"] = user.fields.handle;



    //     return newTeam;
    //   });
    //   console.log(team_members_id)
    //   return this.$set(this.grant, 'team_members', team_members_id);
    //   // return team_members_id;

    // },
    editor() {
      return this.$refs.myQuillEditor.quill
    },
    filteredMsg: function() {
      let msgs = [
        '💪 keep up the great work',
        '👍 i appreciate you',
        '🙌 Great Job',
        '😍 love the mission of your project'
      ]
      if (!this.grant?.metadata?.wall_of_love) {
        return;
      }
      console.log(Object.keys(this.grant.metadata).length > 0 )
      console.log(msgs)
      return this.grant?.metadata?.wall_of_love.filter((msg) => {
        if(msgs.includes(msg[0])) {
          return msg;
        }
      });
    },
    itemsForList() {
      if (this.grant.metadata && !Object.keys(this.grant.metadata).length) {
        return
      }
      this.rows = this.grant?.metadata?.wall_of_love.length || 0;
      return this.grant?.metadata?.wall_of_love.slice(
        (this.currentPage - 1) * this.perPage,
        this.currentPage * this.perPage,
      );
    }

  },

});


if (document.getElementById('gc-grant-detail')) {
  appGrantDetails = new Vue({
    delimiters: [ '[[', ']]' ],
    el: '#gc-grant-detail',
    components: {
      'vue-select': 'vue-select'
    },
    data() {
      return {
        grant: {},
        relatedGrants: [],
        rows: 0,
        perPage: 4,
        currentPage: 1,
        openEdit: false,
        errors: {},
        usersOptions: [],
        editorOptionPrio: {
          modules: {
            toolbar: [
              [ 'bold', 'italic', 'underline' ],
              [{ 'align': [] }],
              [{ 'list': 'ordered'}, { 'list': 'bullet' }],
              [ 'link', 'code-block', 'image', 'video' ],
              ['clean']
            ]
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
      console.log('mount')
      console.log('this is Quill instance:', this.editor)
     this.fetchGrantDetails();

    },
  });
}


const getFormData = object => {
  const formData = new FormData();

  Object.keys(object).forEach(key => formData.append(key, object[key]));
  return formData;
};
