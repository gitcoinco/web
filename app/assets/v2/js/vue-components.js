Vue.component('modal', {
  props: [ 'user', 'size' ],
  template: `<div class="vue-modal modal fade" id="userModal" tabindex="-1" role="dialog" aria-labelledby="userModalLabel" aria-hidden="true">
        <div class="modal-dialog modal-dialog-centered" :class="size" role="document">
          <div class="modal-content">
            <div class="modal-header border-0">
              <button type="button" class="close" data-dismiss="modal" aria-label="Close">
                <span aria-hidden="true">×</span>
              </button>
            </div>
            <div class="modal-body pt-0 ">
              <slot name="header"></slot>
              <slot name="body"></slot>
            </div>
            <div class="modal-footer border-0">
              <slot name="footer"></slot>
            </div>
          </div>
        </div>
      </div>`,
  data() {
    return {
      jqEl: null
    };
  },
  mounted() {
    let vm = this;

    vm.jqEl = $(this.$el);
  },
  methods: {
    closeModal() {
      this.jqEl.bootstrapModal('hide');
    }
  }

});


Vue.component('select2', {
  props: [ 'options', 'value' ],
  template: '#select2-template',
  mounted: function() {
    var vm = this;

    $(this.$el).select2({ data: this.options })
      .val(this.value)
      .trigger('change')
      .on('change', function() {
        vm.$emit('input', this.value);
      });
  },
  watch: {
    value: function(value) {
      // update value
      $(this.$el).val(value).trigger('change');
    },
    options: function(options) {
      // update options
      $(this.$el).empty().select2({ data: options });
    }
  },
  destroyed: function() {
    $(this.$el).off().select2('destroy');
  }
});

Vue.component('loading-screen', {
  template: `<div class="rhombus-spinner">
              <div class="rhombus child-1"></div>
              <div class="rhombus child-2"></div>
              <div class="rhombus child-3"></div>
              <div class="rhombus child-4"></div>
              <div class="rhombus child-5"></div>
              <div class="rhombus child-6"></div>
              <div class="rhombus child-7"></div>
              <div class="rhombus child-8"></div>
              <div class="rhombus big"></div>
            </div>`
});
