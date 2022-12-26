import 'bootstrap/dist/css/bootstrap.css';
import axios from 'axios';
import Vue from 'vue';

import App from './App.vue';
import router from './router';
import dashboard from './dashboard';


axios.defaults.withCredentials = true;
axios.defaults.baseURL = 'http://localhost:8881/';  // the FastAPI backend

Vue.config.productionTip = false;

new Vue({
  router,
  dashboard,
  render: h => h(App)
}).$mount('#app');