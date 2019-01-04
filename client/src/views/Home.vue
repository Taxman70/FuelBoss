<template>

  <v-container fluid fill-height pa-0>
    <v-layout column justify-start fill-height>
    
    </v-layout>
      
  </v-container>
  
</template>

<script>

//import { mapState } from 'vuex'

export default {
  name: 'Home',
  data() {
    return {}
  },
  
  components: {
  },
  
  created() {
    this.$emit('show-page', false)
  },
  
  computed: {
  },
  
  beforeRouteEnter(to, from, next) {
    next(t => {
      t.$store.dispatch('tanks/getAll')
    });
  },
  
  beforeRouteLeave(to, from, next) {
    this.$store.commit('tanks/destroy')
    next()
  }
  
}

</script>
