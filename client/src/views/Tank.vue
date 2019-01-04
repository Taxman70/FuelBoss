<template>

  <v-card flat>
    
    <loading v-if="loading"></loading>
    
    <template v-else>
    
      <div class="pa-3">
      
        <h1 class="mb-3">{{tank.name}}</h1>
        
      </div>
      
    </template>
    
  </v-card>
        
</template>

<script>

import { mapState } from 'vuex'
import Loading from '../components/Loading'

export default {
  name: 'Tank',
  props: {
    id: {},
  }, 
  data() {
    return {
    }
  },
  
  components: {
    Loading,
  },
  
  created() {
    this.$emit('show-page', 'Tanks')
  },
  
  computed: {
  
    ...mapState({
      loading: state => state.tanks.loading,
      tank: state => state.tanks.tank,
    })
    
  },
  
  methods: {

  },
  
  beforeRouteEnter(to, from, next) {
    next(t => {
      t.$store.dispatch('tanks/getOne', t.id)
    });
  },
  
  beforeRouteLeave(to, from, next) {
    this.$store.commit('tanks/destroy')
    next()
  },
  
}

</script>
