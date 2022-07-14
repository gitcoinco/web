if (document.getElementById('grants-showcase')) {

  var appGrants = new Vue({
    delimiters: [ '[[', ']]' ],
    el: '#grants-showcase',
    data: {
      activePage: document.activePage,
      state: 'active',
      mainBanner: document.current_style,
      visibleModal: false
    },
    computed: {
      isLandingPage() {
        return (this.activePage == 'grants_landing');
      },
      showModal(modalName) {
        this.visibleModal = modalName;
      },
      hideModal() {
        this.visibleModal = 'none';
      }
    }
  });
}

