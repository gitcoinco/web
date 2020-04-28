/* eslint-disable no-loop-func */


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
    Vue.component('tribes-profile-header', {
      delimiters: [ '[[', ']]' ],
      props: ['tribe'],
      data: () => ({
        isOnTribe: document.is_on_tribe
      }),
      methods: {
        followTribe: function (tribe, event) {
          event.preventDefault();
          let vm = this;

          const url = `/tribe/${tribe}/join/`;
          const sendJoin = fetchData(url, 'POST', {}, {'X-CSRFToken': vm.csrf});

          $.when(sendJoin).then((response) => {
            if (response && response.is_member) {
              vm.tribe.follower_count++;
              vm.isOnTribe = true;
            } else {
              vm.tribe.follower_count--;
              vm.isOnTribe = false;
            }
          }).fail((error) => {
            console.log(error);
          });
        }
      }
    });
    Vue.use(VueQuillEditor);
    window.tribesApp = new Vue({
      delimiters: [ '[[', ']]' ],
      el: '#tribes-vue-app',
      methods: {
        tabChange: function(input) {
          let vm = this;

          switch (input) {
            default:
            case 0:
              newPathName = 'townsquare';
              break;
            case 1:
              newPathName = 'projects';
              break;
            case 2:
              newPathName = 'people';
              break;
            case 3:
              newPathName = 'chat';
              break;
          }
          let newUrl = `/${vm.tribe.handle}/${newPathName}${window.location.search}`;

          history.pushState({}, `Tribe - @${vm.tribe.handle}`, newUrl);
        },
        onEditorBlur(quill) {
          console.log('editor blur!', quill)
        },
        onEditorFocus(quill) {
          console.log('editor focus!', quill)
        },
        onEditorReady(quill) {
          console.log('editor ready!', quill)
        }
      },
      computed: {
        editor() {
          return this.$refs.quillEditor.quill
        }
      },
      updated() {
        console.log('something happened');
      },
      mounted() {
        console.log('we mounted');
      },
      data: function() {
        return $.extend({
          chatURL: document.chatURL || 'https://chat.gitcoin.co/',
          activePanel: document.activePanel,
          tribe: document.currentProfile
        }, document.initData, {
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
          }
        });
      }
    });
  });

})(jQuery);
