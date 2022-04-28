if (document.getElementById('grants-showcase')) {

  var appGrants = new Vue({
    delimiters: [ '[[', ']]' ],
    el: '#grants-showcase',
    data: {
      activePage: document.activePage,
      state: 'active',
      mainBanner: document.current_style,
    },
    computed: {
      isLandingPage() {
        return (this.activePage == 'grants_landing');
      }
    },
  });
}

