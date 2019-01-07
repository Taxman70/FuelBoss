<template>

  <v-container fluid>
    <v-layout row justify-center>
      <v-layout column align-center>
        <tank-gauge :tank="tank"/>
        <tank-graph
          v-for="i in tank.graphs"
          :key="i"
          :tank="tank"
          :graph="i"
        />
      </v-layout>
    </v-layout>

  </v-container>

        
</template>

<script>

import { mapState } from 'vuex'
import Loading from '../components/Loading'
import TankGauge from '../components/TankGauge'
import TankGraph from '../components/TankGraph'

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
    TankGauge,
    TankGraph,
  },
  
  created() {
    this.$emit('show-page', 'Tank')
  },
  
  computed: {
  
    ...mapState({
      loading: state => state.tanks.loading,
      tank: state => state.tanks.tank,
    }),
    
    numGraphs() {
      return this.tank.graphs
    },
    
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
