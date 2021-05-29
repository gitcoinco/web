Vue.component('v-select', VueSelect.VueSelect);
Vue.use(VueQuillEditor);

const djangoExample = `{% load i18n static compress %}

...

{% bundle css file example_name %}
  <link rel="stylesheet" type="text/x-scss" href={% static "v2/scss/*.scss" %} />
{% endcompress %}`;

const buttonExample = '<button class="btn btn-primary">...</button>';

const inputExample = `<label for="text" class="font-caption letter-spacing text-black-60 text-uppercase">Example <span class="badge badge-greylight text-capitalize">Required</span></label>

<input id="text" name="text" v-model="form.text" class="form__input form__input-lg" maxlength="150" type="text" placeholder="Example text input" required />

<div class="text-danger" v-if="!form.text">
  This is an error message
</div>`;

const selectExample = `<label class="font-caption letter-spacing text-black-60 text-uppercase" for="">Example <span class="font-smaller-6 badge badge-greylight text-capitalize ml-2">Required</span></label>

<v-select placeholder="Select option" :options="selectOptions" label="label" v-model="form.select" :reduce="option => option.name" multiple>
  <template #search="{attributes, events}">
    <input
      class="vs__search"
      :required="!form.select.length"
      v-bind="attributes"
      v-on="events"
    />
  </template>
  <template v-slot:option="option">
    <span class="font-weight-semibold">[[ option.label ]]</span>
  </template>
</v-select>

<div class="text-danger" v-if="!form.select.length">
  This is an error message
</div>`;

const radioExample = `<span class="font-caption letter-spacing text-black-60 text-uppercase" for="">Example <span class="font-smaller-6 badge badge-greylight text-capitalize ml-2">Required</span></span>

<div class="form__radio option">
  <input name="radio" v-model="form.radio" id="radio1" type="radio" value="open" val-ui="radio" required />
  <label class="filter-label" for="radio1">Option 1</label>
</div>

<div class="form__radio option">
  <input name="radio" v-model="form.radio" id="radio2" type="radio" value="started" val-ui="radio" required />
  <label class="filter-label" for="radio2">Option 2</label>
</div>

<div class="text-danger" v-if="!form.radio">
  This is an error message
</div>`;

const checkboxExample = `<span class="font-caption letter-spacing text-black-60 text-uppercase" for="">Example <span class="font-smaller-6 badge badge-greylight text-capitalize ml-2">Required</span></span>

<div class="checkbox_container">
  <input name="checkbox" v-model="form.checkbox" id="checkbox" type="checkbox" value="1" required />
  <span class="checkbox" ></span>
  <div class="filter-label display-inline">
    <label for="checkbox">Option 1</label>
  </div>
</div>

<div class="text-danger" v-if="!form.checkbox">
  This is an error message
</div>`;

const btnRadioExample = `<span class="font-caption letter-spacing text-black-60 text-uppercase" for="">Example 2 <span class="font-smaller-6 badge badge-greylight text-capitalize ml-2">Required</span></span>

<div :class="\`btn-group-toggle d-flex flex-column flex-lg-row flex-wrap \${!form.btnRadio ? 'invalid' : ''}\`">
  <label class="btn btn-radio d-flex align-items-center justify-content-center mr-2 mb-2 font-weight-bold py-2 px-4" :class="{'active': form.btnRadio === '1'}">
    <input type="radio" name="btn-radio" id="btn-radio-2-1" value="1" v-model="form.btnRadio" required>Option 1
  </label>

  <label class="btn btn-radio d-flex align-items-center justify-content-center mr-2 mb-2 font-weight-bold py-2 px-4" :class="{'active': form.btnRadio === '2'}">
    <input type="radio" name="btn-radio" id="btn-radio-2-2" value="2" v-model="form.btnRadio" required>Option 2
  </label>

  <label class="btn btn-radio d-flex align-items-center justify-content-center mr-2 mb-2 font-weight-bold py-2 px-4" :class="{'active': form.btnRadio === '3'}">
    <input type="radio" name="btn-radio" id="btn-radio-2-3" value="3" v-model="form.btnRadio" required>Option 3
  </label>
</div>

<div class="text-danger" v-if="!form.btnRadio">
  This is an error message
</div>`;

const btnCheckboxExample = `<span class="font-caption letter-spacing text-black-60 text-uppercase" for="">Example 2 <span class="font-smaller-6 badge badge-greylight text-capitalize ml-2">Required</span></span>

<div :class="\`btn-group-toggle d-flex flex-column flex-lg-row flex-wrap \${!form.btnCheckbox.length ? 'invalid' : ''}\`">
  <label class="btn btn-radio d-flex align-items-center justify-content-center mr-2 mb-2 font-weight-bold py-2 px-4" :class="{'active': form.btnCheckbox.includes('1')}">
    <input type="checkbox" name="btn-checkbox2-1" id="btn-checkbox-2-1" value="1" v-model="form.btnCheckbox" required>Option 1
  </label>

  <label class="btn btn-radio d-flex align-items-center justify-content-center mr-2 mb-2 font-weight-bold py-2 px-4" :class="{'active': form.btnCheckbox.includes('2')}">
    <input type="checkbox" name="btn-checkbox2-2" id="btn-checkbox-2-2" value="2" v-model="form.btnCheckbox" required>Option 2
  </label>

  <label class="btn btn-radio d-flex align-items-center justify-content-center mr-2 mb-2 font-weight-bold py-2 px-4" :class="{'active': form.btnCheckbox.includes('3')}">
    <input type="checkbox" name="btn-checkbox2-3" id="btn-checkbox-2-3" value="3" v-model="form.btnCheckbox" required>Option 3
  </label>
</div>

<div class="text-danger" v-if="!form.btnCheckbox.length">
  This is an error message
</div>`;

const richEditorExample = `<label for="rich_editor" class="font-caption letter-spacing text-black-60 text-uppercase">Example <span class="badge badge-greylight text-capitalize">Required</span></label>

<quill-editor
  ref="quillEditorExample"
  v-model="form.rich_editor"
  :class="\`editor \${!form.rich_editor ? 'invalid' : ''}\`"
  :options="editorOptionPrio"
></quill-editor>

<div class="text-danger" v-if="!form.rich_editor">
  This is an error message
</div>`;

const alertExample = `<div class="alert alert-static bs-alert alert-primary d-flex justify-content-between align-items-center shadow-sm py-3 font-weight-semibold font-body">
  <div class="message">
    <div class="content">Message</div>
  </div>
  <span class="closebtn">×</span>
</div>`;

const alertExample2 = '_alert(msg, type, closeAfter);';

const accordionExample = `<div class="accordion-group gc-accordion" id="accordion-group">
  <h5 class="accordion collapsed" id="headingOne" data-parent="#accordion-group" data-toggle="collapse" data-target="#collapseOne" aria-controls="collapseOne">
    <span class="accordion-title">
      Accordion Title 1
    </span>
  </h5>
  <div class="accordion-panel collapse font-subheader text-grey-400" id="collapseOne" aria-labelledby="headingOne" data-parent="#accordion-group">
    <p>Accordion 1 content</p>
  </div>
</div>`;

const tabsExample = `<b-tabs content-class="mt-3" v-model="tabSelected" >
  <b-tab :title-link-class="'nav-line'">
    <template v-slot:title>Tab 1</template>
    <p>Tab 1 content</p>
  </b-tab>

  <b-tab :title-link-class="'nav-line'">
    <template v-slot:title>Tab 2</template>
    <p>Tab 2 content</p>
  </b-tab>
</b-tabs>`;

Vue.mixin({
  methods: {
    openAlert: function(type) {
      _alert('Message', type);
    }
  }
});

if (document.getElementById('styleguide-components')) {
  appFormBounty = new Vue({
    delimiters: [ '[[', ']]' ],
    el: '#styleguide-components',
    components: {
      'vue-select': 'vue-select'
    },
    data() {
      return {
        djangoExample: djangoExample,
        buttonExample: buttonExample,
        inputExample: inputExample,
        selectExample: selectExample,
        radioExample: radioExample,
        checkboxExample: checkboxExample,
        btnRadioExample: btnRadioExample,
        btnCheckboxExample: btnCheckboxExample,
        richEditorExample: richEditorExample,
        alertExample: alertExample,
        alertExample2: alertExample2,
        accordionExample: accordionExample,
        tabsExample: tabsExample,
        selectOptions: [
          { 'name': 'north_america', 'label': 'North America'},
          { 'name': 'oceania', 'label': 'Oceania'},
          { 'name': 'latin_america', 'label': 'Latin America'},
          { 'name': 'europe', 'label': 'Europe'},
          { 'name': 'africa', 'label': 'Africa'},
          { 'name': 'middle_east', 'label': 'Middle East'},
          { 'name': 'india', 'label': 'India'},
          { 'name': 'east_asia', 'label': 'East Asia'},
          { 'name': 'southeast_asia', 'label': 'Southeast Asia'}
        ],
        tabSelected: 0,
        form: {
          select1: [],
          select2: [],
          btnCheckbox: [],
          btnCheckbox2: [],
          rich_editor: '',
          rich_editor2: ''
        },
        editorOptionPrio: {
          modules: {
            toolbar: [
              [ 'bold', 'italic', 'underline' ],
              [{ 'align': [] }],
              [{ 'list': 'ordered'}, { 'list': 'bullet' }],
              [ 'link', 'code-block' ],
              ['clean']
            ]
          },
          theme: 'snow',
          placeholder: 'Example rich text-editor'
        }
      };
    }
  });
}
