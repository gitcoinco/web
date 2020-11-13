/* eslint-disable no-loop-func */
(function($) {

  $(function() {
    Vue = Vue.extend({
      delimiters: [ '[[', ']]' ]
    });

    Vue.component('hackathon-project', {
      delimiters: [ '[[', ']]' ],
      props: [ 'hackathon', 'project' ],
      mounted() {
        let vm = this;

      },
      methods: {
        tabChange: function(input) {
          let vm = this;

          switch (input) {
            default:
            case 0:
              newPathName = 'summary';
              break;
            case 1:
              newPathName = 'activity';
              break;
          }

          let newUrl = `/hackathon/${vm.hackathon['slug']}/projects/${vm.project.id}/${vm.project.name}/${newPathName}?${window.location.search}`;

          history.pushState({}, `${vm.hackathon['slug']} - ${newPathName}`, newUrl);
        },
        getVideoId(videoURL) {
          const metadata = getVideoMetadata(videoURL);

          if (metadata) {
            return metadata['id'];
          }

          return '';
        }
      },
      data: function() {
        return {
          csrf: $("input[name='csrfmiddlewaretoken']").val(),
          activePanel: document.tab
        };
      }
    });

    window.hackathonApp = new Vue({
      delimiters: [ '[[', ']]' ],
      el: '#hackathon-project-app',
      mounted: () => {
        setTimeout(() => {

          $(window).on('popstate', function(e) {
            e.preventDefault();
            // we change the url with the panels to ensure if you refresh or get linked here you're being shown what you want
            // this is so that we go back to where we got sent here from, townsquare, etc.
            window.location = document.referrer;
          });
        }, 0);
      },
      methods: {
        projectModal() {
          let project = this.project;
          let vm = this;

          projectModal(project.prize.id, project.id, async() => {
            const context = await fetchData(`/api/v0.1/projects/${project.id}`);

            vm.project = Object.assign({}, context.project);
            vm.hackathon = Object.assign({}, context.hackathon);

          });
        }
      },
      data: () => ({
        project: document.projectObj,
        hackathon: document.hackathonObj,
        activePanel: document.tab
      })
    });
  });
})(jQuery);
