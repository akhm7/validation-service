<template>
    <div v-if="request">
      <p><strong>Title:</strong> {{ request.title }}</p>
      <p><strong>Content:</strong> {{ request.content }}</p>
      <p><strong>Author:</strong> {{ request.author.username }}</p>
  
      <div v-if="user.id === request.author.id">
        <p><router-link :to="{name: 'EditRequest', params:{id: request.id}}" class="btn btn-primary">Edit</router-link></p>
        <p><button @click="removeRequest()" class="btn btn-secondary">Delete</button></p>
      </div>
    </div>
  </template>
  
  
  <script>
  import { mapGetters, mapActions } from 'vuex';
  export default {
    name: 'Request',
    props: ['id'],
    async created() {
      try {
        await this.viewRequest(this.id);
      } catch (error) {
        console.error(error);
        this.$router.push('/dashboard');
      }
    },
    computed: {
      ...mapGetters({ request: 'stateRequest', user: 'stateUser'}),
    },
    methods: {
      ...mapActions(['viewRequest', 'deleteRequest']),
      async removeRequest() {
        try {
          await this.deleteRequest(this.id);
          this.$router.push('/dashboard');
        } catch (error) {
          console.error(error);
        }
      }
    },
  };
  </script>