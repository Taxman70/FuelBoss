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
      <span>Switches go here</span>
    </v-layout>
    
  </v-container>
  
</template>

<script>

import { mapState } from 'vuex'
import TankGauge from '../components/TankGauge'

export default {
  name: 'Home',
  
  data() {
    return {}
  },
  
  components: {
    TankGauge,
  },
  
  created() {
    this.$emit('show-page', false)
  },
  
  computed: {
    ...mapState({
      tanks: state => state.tanks.tanks,
    }),
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
