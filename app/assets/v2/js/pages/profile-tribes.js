/* eslint-disable no-loop-func */
(function($) {
  // doc ready
  $(() => {
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
              newPathName = 'people';
              break;
            case 2:
              newPathName = 'projects';
              break;
            case 3:
              newPathName = 'chat';
              break;
          }
          // let newUrl = `/${vm.initData.currentProfile.title.slice()}/${vm.hackathonObj['slug']}/${newPathName}/${window.location.search}`;

          // history.pushState({}, `${vm.hackathonObj['slug']} - ${newPathName}`, newUrl);
        }
      },
      updated() {
        console.log('something happened');
      },
      mounted() {
        console.log('we mounted');
      },
      data: function() {
        return {
          chatURL: document.chatURL || 'https://chat.gitcoin.co/',
          activePanel: document.activePanel,
          tribe: document.initData || {}
        };
      }
    });
  });

})(jQuery);
