import axios from 'axios';

const state = {
  requests: null,
  request: null
};

const getters = {
  stateRequests: state => state.requests,
  stateRequest: state => state.request,
};

const actions = {
  async getRequests({commit}) {
    let {data} = await axios.get('requests');
    commit('setRequests', data);
  },
  async viewRequest({commit}, id) {
    let {data} = await axios.get(`request/${id}`);
    commit('setRequests', data);
  },
};

const mutations = {
  setRequests(state, requests){
    state.requests = requests;
  },
  setRequest(state, request){
    state.request = request;
  },
};

export default {
  state,
  getters,
  actions,
  mutations
};