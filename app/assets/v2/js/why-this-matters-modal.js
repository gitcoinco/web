Vue.component('why-this-matters-modal', {
  delimiters: [ '[[', ']]' ],
  props: {
    showModal: {
      type: Boolean,
      required: false,
      'default': false
    }
  },
  template: `
    <b-modal id="why-this-matters-modal" @hide="dismissModal()" :visible="showModal" size="lg" body-class="p-3" center hide-header hide-footer>
      <template v-slot:default="{ hide }">
        <div class="modal-content p-0">
          <div class="w-100">
            <button @click="dismissModal()" type="button" class="close" data-dismiss="modal" aria-label="Close">
              <span aria-hidden="true">&times;</span>
            </button>
          </div>
          <div class="py-4">
            <iframe src="https://www.youtube.com/embed/v1Dm7FI2AdU?rel=0" frameborder="0" allowfullscreen class="w-100" style="min-height: 60vh;"></iframe>
          </div>
        </div>
      </template>
    </b-modal>`,

  methods: {
    dismissModal() {
      // localStorage.setItem('dismiss-sms-validation', true);
      this.$emit('modal-dismissed');
    }
  }
});
