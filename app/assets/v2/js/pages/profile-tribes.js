/* eslint-disable no-loop-func */

document.long_poller_live = false;

const loadDynamicScript = (callback, url, id) => {
  const existingScript = document.getElementById(id);

  if (!existingScript) {
    const script = document.createElement('script');

    script.src = url;
    script.id = id;
    document.body.appendChild(script);

    script.onload = () => {
      if (callback)
        callback();
    };
  }

  if (existingScript && callback)
    callback();
};

(function($) {
  // doc ready
  $(() => {
    Vue.use(VueQuillEditor);
    window.tribesApp = new Vue({
      delimiters: [ '[[', ']]' ],
      el: '#tribes-vue-app',
      methods: {
        followTribe: function(tribe, event) {
          event.preventDefault();
          let vm = this;

          const url = `/tribe/${tribe}/join/`;
          const sendJoin = fetchData(url, 'POST', {}, {'X-CSRFToken': vm.csrf});

          $.when(sendJoin).then((response) => {
            if (response && response.is_member) {
              $('[data-jointribe]').each((idx, ele) => {
                $(ele).attr('hidden', true);
              });
              vm.tribe.follower_count++;
              vm.is_on_tribe = true;
            } else {
              vm.tribe.follower_count--;
              vm.is_on_tribe = false;
              $('[data-jointribe]').each((idx, ele) => {
                $(ele).attr('hidden', false);
              });
            }
          }).fail((error) => {
            console.log(error);
          });
        },
        resetPreview: function() {
          this.headerFilePreview = null;
        },
        updateTribe: function() {
          let vm = this;
          const url = `/tribe/${vm.tribe.handle}/save/`;

          let data = new FormData();

          if (vm.$refs.quillEditorDesc) {
            data['tribe_description'] = vm.tribe.tribe_description;
          }

          if (vm.$refs.quillEditorPriority) {
            data.append('tribe_priority', vm.tribe.tribe_priority);
            data.append('priority_html_text', vm.$refs.quillEditorPriority.quill.getText(''));
          }

          if (vm.headerFile) {
            data.append('cover_image', vm.headerFile);
          }

          if (vm.params.publish_to_ts) {
            data.append('publish_to_ts', vm.params.publish_to_ts);
          }
          const sendSave = async(url, data) => {
            return $.ajax({
              type: 'POST',
              url: url,
              processData: false,
              contentType: false,
              data: data,
              headers: {'X-CSRFToken': vm.csrf}
            });
          };

          $.when(sendSave(url, data)).then(function(response) {
            _alert('Tribe has been updated');
            if (vm.headerFile) {
              vm.tribe.tribes_cover_image = vm.headerFilePreview;
              vm.$bvModal.hide('change-tribe-header');
            }
          }).fail(function(error) {

            _alert('Error updating Tribe', 'danger');
            console.error('error: unable to update tribe', error);
          });
        },
        suggestBounty: function() {
          let vm = this;
          const githubUrl = vm.params.suggest.githubUrl;
          const tokenName = tokenAddressToDetails(vm.params.suggest.token)['name'];
          const comment = vm.params.suggest.comment;
          const tribe = vm.tribe.handle;
          const url = '/api/v1/bounty_request/create';
          const amount = vm.params.suggest.amount;

          fetchIssueDetailsFromGithub(githubUrl).then(result => {
            const title = result.title;

            const createBountyRequest = fetchData(
              url,
              'POST',
              {
                'github_url': githubUrl,
                'tribe': tribe,
                'comment': comment,
                'token_name': tokenName,
                'amount': amount,
                'title': title
              },
              {'X-CSRFToken': $("input[name='csrfmiddlewaretoken']").val()}
            );

            $.when(createBountyRequest).then(function(response) {

              if (response.status == 204) {
                _alert('Bounty Request has been created');
                location.reload();
              } else {
                _alert(`Error creating bounty request as ${response.message}`, 'danger');
                console.error(response.message);
              }

            }).fail(function(error) {
              _alert(`Error creating bounty request as ${error}`, 'danger');
              console.error('error: unable to creating bounty request', error);
            });
          }).catch(error => {
            _alert(`Error creating bounty request as ${error}`, 'danger');
            console.error('error: unable to creating bounty request', error);
          });
        },
        rejectBountyRequest: function(idx, bounty_request_id) {
          let vm = this;

          const url = '/api/v1/bounty_request/update';

          const createBountyRequest = fetchData(
            url,
            'POST',
            {
              'bounty_request_id': bounty_request_id,
              'request_status': 'c'
            },
            {'X-CSRFToken': vm.csrf}
          );

          $.when(createBountyRequest).then(function(response) {

            if (response.status === 200) {
              _alert('Bounty Request has been rejected');
              delete vm.tribe.suggested_bounties[idx];
            } else {
              _alert(`Error rejecting bounty request as ${response.message}`, 'danger');
              console.error(response.message);
            }

          }).fail(function(error) {
            _alert(`Error rejecting bounty request. ${error}`, 'danger');
            console.error('error: unable to reject bounty request', error);
          });
        },
        resetBountySuggestion: function() {
          this.params.suggest = {};
        },
        tabChange: function(input) {
          let vm = this;

          document.long_poller_live = false;

          switch (input) {
            default:
            case 0:
              newPathName = 'townsquare';
              document.long_poller_live = true;
              document.run_long_poller(true);
              break;
            case 1:
              newPathName = 'projects';
              break;
            case 2:
              newPathName = 'bounties';
              break;
            case 3:
              newPathName = 'people';
              break;
            case 4:
              newPathName = 'manage';
              break;
          }
          let newUrl = `/${vm.tribe.handle}/${newPathName}${window.location.search}`;

          history.pushState({}, `Tribe - @${vm.tribe.handle}`, newUrl);
        }
      },
      computed: {
        editorDesc() {
          return this.$refs.quillEditorDesc.quill;
        },
        editorPriority() {
          return this.$refs.quillEditorPriority.quill;
        },
        editorComment() {
          return this.$refs.quillEditorComment.quill;
        }
      },
      beforeMount() {
        if (this.isMobile) {
          this.showCoreTeam = false;
        }
      },
      mounted() {
        $(window).on('popstate', function(e) {
          e.preventDefault();
          // we change the url with the panels to ensure if you refresh or get linked here you're being shown what you want
          // this is so that we go back to where we got sent here from, townsquare, etc.
          window.location = document.referrer;
        });
        let vm = this;

        this.$nextTick((e) => {
          vm.isLoading = false;
          $('#preloader').remove();
        });
        this.$watch('headerFile', function(newVal, oldVal) {
          if (checkFileSize(this.headerFile, 4000000) === false) {
            _alert(`Profile Header Image should not exceed ${(4000000 / 1024 / 1024).toFixed(2)} MB`, 'danger');
          } else {
            let reader = new FileReader();

            reader.onload = function(e) {
              vm.headerFilePreview = e.target.result;
              $('#preview').css('width', '100%');
              $('#js-drop span').hide();
              $('#js-drop input').css('visible', 'invisible');
              $('#js-drop').css('padding', 0);
            };
            reader.readAsDataURL(this.headerFile);
          }
        }, {deep: true});
      },
      data: function() {
        return {
          isLoading: true,
          params: {
            suggest: {},
            publish_to_ts: false
          },
          showCoreTeam: true,
          activePanel: document.activePanel,
          tribe: document.currentProfile,
          online: (document.contxt && document.contxt.github_handle),
          tokens: document.tokens,
          csrf: $("input[name='csrfmiddlewaretoken']").val(),
          headerFile: null,
          headerFilePreview: null,
          is_my_org: document.is_my_org || false,
          is_on_tribe: document.is_on_tribe || false,
          is_staff: document.contxt.is_staff || false,
          editorOptionPrio: {
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
          editorOptionDesc: {
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
          },
          editorOptionComment: {
            modules: {
              toolbar: [
                [ 'bold', 'italic', 'underline' ],
                [{ 'align': [] }],
                [ 'link', 'code-block' ],
                ['clean']
              ]
            },
            theme: 'snow',
            placeholder: 'What would you suggest as a bounty?'
          }
        };
      }
    });
  });

})(jQuery);
