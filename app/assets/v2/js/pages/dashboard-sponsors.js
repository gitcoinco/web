(function($) {
  $(function() {
    window.hackathonApp = new Vue({
      delimiters: [ '[[', ']]' ],
      el: '#sponsors-app',
      mounted() {
        this.retrieveSponsorPrizes();
      },
      methods: {
        retrieveSponsorPrizes: function() {
          const vm = this;
          const hackathon = fetchData(`/api/v1/hackathon/${vm.hackathonObj['slug']}/prizes`);

          $.when(hackathon).then((response) => {
            console.log(response);
            vm.prizes = response.prizes;
          });
        },
        tabChange: function(input) {
          let vm = this;

          switch (input) {
            default:
            case 0:
              newPathName = 'prizes';
              break;
            case 1:
              newPathName = 'submissions';
              break;
          }
          let newUrl = `/hackathon/dashboard/${vm.hackathonObj['slug']}/${newPathName}`;

          history.pushState({}, `${vm.hackathonObj['slug']} - ${newPathName}`, newUrl);

        }
      },
      data: () => ({
        activePanel: document.activePanel,
        hackathonObj: document.hackathonObj,
        hackathonSponsors: document.hackathonSponsors,
        hackathonProjects: [],
        chatURL: document.chatURL,
        prizes: []
      })
    });
  });
})(jQuery);
