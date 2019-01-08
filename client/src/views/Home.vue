<template>

  <v-container fluid>
    <v-layout row justify-center>
      <tank-gauge
        v-for="tank in tanks"
        :key="tank.id"
        :tank="tank"
      />
    </v-layout>

    <v-layout row justify-center>
      <switchy
        v-for="switchy in switches"
        :key="switchy.id"
        :switchy="switchy"
      />
    </v-layout>
    
  </v-container>
  
</template>

<script>

import { mapState } from 'vuex'
import TankGauge from '../components/TankGauge'
import Switchy from '../components/Switchy'

export default {
  name: 'Home',
  
  data() {
    return {}
  },
  
  components: {
    TankGauge,
    Switchy,
  },
  
  created() {
    this.$emit('show-page', false)
  },
  
  computed: {
    ...mapState({
      tanks: state => state.tanks.tanks,
      switches: state => state.switches.switches,
    }),
  },
  
  beforeRouteEnter(to, from, next) {
    next(t => {
      t.$store.dispatch('tanks/getAll')
      t.$store.dispatch('switches/getAll')
    });
  },
  
  beforeRouteLeave(to, from, next) {
    this.$store.commit('tanks/destroy')
    this.$store.commit('switches/destroy')
    next()
  }
  
}

</script>
