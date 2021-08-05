let activities = [];
let activityPage = 1;
let activityNext = '';
let activityNumPages = '';
let numActivities = '';
let refreshInterval = 55000;


Vue.mixin({
  methods: {
    fetchActivity: async function() {
      let vm = this;
      console.log('test')
      vm.activityId = await vm.getUrlParameters();
      vm.loadingActivity = true;
      let url = '/api/v0.1/activities/?expand=~all';

      if (vm.activityId) {
        url = `/api/v0.1/activities/${vm.activityId}/?expand=~all`;
      }
      if (vm.activityNext) {
        url = vm.activityNext;
      }
      console.log(url, vm.activityId);

      let getActivities = await fetch(url);
      let activitiesJson = await getActivities.json();
      console.log(activitiesJson);

      // $.when(getActivities).then(function(response) {
        // newActivities = newData(response.results, vm.activities);
      vm.loadingActivity = false;
      if (!activitiesJson.results) {
        return vm.activities.push(activitiesJson);;
      }
      vm.activityNext = activitiesJson.next;
      vm.numActivities = activitiesJson.count;

      activitiesJson.results.forEach(function(item) {
        vm.activities.push(item);
      });
      vm.longPoll();

    },
    longPoll: async function() {
      let vm = this;
      let diffCounter = vm.numActivityBuffer > 0 ? vm.numActivityBuffer : 4;
      let url = `/api/v0.1/activities/?expand=~all&page_size=${diffCounter}`;

      if (vm.activityId) {
        return;
      }

      if (document.hidden) {
        return setTimeout(function() {
          vm.longPoll();
        }, refreshInterval);
      }

      let getActivities = await fetch(url);
      let activitiesJson = await getActivities.json();

      if (vm.numActivities !== activitiesJson.count) {
        vm.numActivityBuffer = activitiesJson.count - vm.numActivities;
        vm.activityBuffer = activitiesJson.results.splice(0,vm.numActivityBuffer);
      }

      setTimeout(function() {
        vm.longPoll();
      }, 20000);
    },
    loadNewActivities: async function() {
      let vm = this;

      vm.numActivities = vm.numActivities + vm.numActivityBuffer;
      vm.activityBuffer.forEach(function(item) {
        vm.activities.push(item);
      });

      vm.activityBuffer = [];
      vm.numActivityBuffer = 0;
    },
    deleteActivity: async function(index) {
      console.log(index);
      let vm = this;
      vm.activities.splice(index, 1);
    },
    getUrlParameters: function() {
      let vm = this;
      const params = new URLSearchParams(window.location.search)
      if (params.has('activity')) {
        return params.get('activity');
      }
    },

    onScroll: function(event) {
      vm = this;
      let scrollContainer = event.target;
      // console.log(scrollContainer);

      if (scrollContainer.scrollTop + scrollContainer.clientHeight >= scrollContainer.scrollHeight) {
        if (vm.activityNext && !vm.loadingActivity) {
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
      loadingActivity: false,
      activityId: null,
      activityBuffer: [],
      numActivityBuffer: 0,
    },
    mounted() {
      this.fetchActivity();
    },
    created() {
      // this.sendState();
    }
  });
}
