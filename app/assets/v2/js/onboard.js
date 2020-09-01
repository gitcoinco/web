Vue.component('v-select', VueSelect.VueSelect);

Vue.mixin({
  methods: {
  },
  computed: {

  }

});


if (document.getElementById('gc-onboard')) {
  var appOnboard = new Vue({
    delimiters: [ '[[', ']]' ],
    el: '#gc-onboard',
    components: {
      'vue-select': 'vue-select'
    },
    data() {
      return {
        skills: ['css','php'],
        skillsSelected: [],
      };
    },
    computed: {

    },
    methods: {

    },
    mounted() {
      this.$refs['onboard-modal'].openModal();
    },
    created() {

    }
  });
}
