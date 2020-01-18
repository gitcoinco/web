if (document.getElementById("gc-search")) {
  var app = new Vue({
    delimiters: ["[[", "]]"],
    el: "#gc-search",
    data: {
      term: "",
      results: [],
      currentTab: 0,
      source_types: ["orgs", "profile", "bounties", "grants", "pages"]
    },
    mounted() {
      this.search();
    },
    created() {
      this.search();
    },
    filters: {
      capitalize: function(value) {
        if (!value) return "";
        value = value.toString();
        return value.charAt(0).toUpperCase() + value.slice(1);
      }
    },
    methods: {
      search: async function() {
        let vm = this;
        if (vm.term.length > 3) {
          let search = await fetchData(
            `/api/v0.1/search/?term=${vm.term}`,
            "GET"
          );
          let results = groupBySource("source_type");
          vm.results = results(search);
        } else {
          vm.results = {};
        }
      }
    }
  });
}

const groupBySource = key => array =>
  array.reduce((objectsByKeyValue, obj) => {
    const value = obj[key];
    objectsByKeyValue[value] = (objectsByKeyValue[value] || []).concat(obj);
    return objectsByKeyValue;
  }, {});
