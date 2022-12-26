import createPersistedState from "vuex-persistedstate";
import Vue from 'vue';
import Vuex from 'vuex';

import requests from './modules/requests';


Vue.use(Vuex);

export default new Vuex.Dashboard({
  modules: {
    requests,
  },
  plugins: [createPersistedState()]
});