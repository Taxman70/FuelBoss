<template>

  <v-card flat>
  
    <div class="pa-3 text-xs-center">

      <img src="../assets/logo.png"/>
      
      <p class="headline">{{settings.appTitle}}</p>
    
      <p class="mb-0">Git: {{gitVersion}}/{{gitBranch}}</p>
      <p>Built: {{buildDate}}</p>

    </div>
    
    <v-footer absolute>
      <v-layout justify-center row>
        <div>&copy; {{new Date().getFullYear()}}</div>
      </v-layout>
    </v-footer>
    
  </v-card>
        
</template>

<style>

li {
  list-style-type: none;
}

</style>

<script>

import { mapState } from 'vuex'
import build from '../build'

export default {
  name: 'About',
  data() {
    return {
      statistics: {},
    }
  },
  
  created() {
    this.$emit('show-page', 'About')
  },
  
  computed: {
    gitVersion() {
      return build.gitVersion
    },
    gitBranch() {
      return build.gitBranch
    },
    buildDate() {
      return build.buildDate
    },
    ...mapState({
      settings: state => state.settings,
    }),
  },
  
  methods: {
  
  },
  
}

</script>
