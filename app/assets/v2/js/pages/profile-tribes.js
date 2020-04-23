/* eslint-disable no-loop-func */
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
        }
      },
      updated() {
        console.log('something happened');
      },
      mounted() {
        console.log('we mounted');
      },
      data: function() {
        const data = $.extend({
          chatURL: document.chatURL || 'https://chat.gitcoin.co/',
          activePanel: document.activePanel,
          tribe: document.currentProfile
        }, document.initData);

        console.log(data);
        return data;
      }
    });
  });

})(jQuery);
