
import Vue from '../../../node_modules/vue'
import { MdButton, MdContent, MdTabs } from '../../../node_modules/vue-material/dist/components'
import { BootstrapVue, IconsPlugin } from 'bootstrap-vue'
 
// Import Bootstrap an BootstrapVue CSS files (order is important)
import 'bootstrap/dist/css/bootstrap.css'
import 'bootstrap-vue/dist/bootstrap-vue.css'

Vue.use(MdButton)
Vue.use(MdContent)
Vue.use(MdTabs)
 
// Make BootstrapVue available throughout your project
Vue.use(BootstrapVue)
 
// Optionally install the BootstrapVue icon components plugin
Vue.use(IconsPlugin)