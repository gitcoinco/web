let activities = [];
let activityPage = 1;
let activityNext = '';
let activityNumPages = '';
let numActivities = '';


Vue.mixin({
  methods: {
    fetchActivity: function() {
      let vm = this;
      console.log('test')

      vm.loadingActivity = true;


      let url = '/api/v0.1/activities/';
      if (vm.activityNext) {
        url = vm.activityNext;
      }

      let getActivities = fetchData (url, 'GET');

      $.when(getActivities).then(function(response) {
        // newActivities = newData(response.results, vm.activities);
        vm.loadingActivity = false;

        response.results.forEach(function(item) {
          vm.activities.push(item);
        });

        vm.activityNext = response.next;
        vm.numActivities = response.count;



      });
    },

    onScroll: function(event) {
      vm = this;
      let scrollContainer = event.target;
      // console.log(scrollContainer);

      if (scrollContainer.scrollTop + scrollContainer.clientHeight >= scrollContainer.scrollHeight) {
        if (vm.activityNext) {
          this.fetchActivity();
        }
      }
    }
  },
  computed: {
    sortedItems: function() {
      if (!this.activities) {
        return;
      }
      return this.activities.slice().sort((a, b) => new Date(b.created_on) - new Date(a.created_on));
    }
  }

});



if (document.getElementById('gc-activity')) {
  var appActivity = new Vue({
    delimiters: [ '[[', ']]' ],
    el: '#gc-activity',
    data: {
      activityPage,
      activities,
      activityNext,
      activityNumPages,
      numActivities,
      loadingActivity: false
    },
    mounted() {
      this.fetchActivity();

    },
    created() {
      // this.sendState();
    }
  });
}
