<template>
  <v-progress-circular
    :rotate="90"
    :size="200"
    :width="30"
    :value="value"
    :color="color"
    class="tankGauge"
    @click="gotoTank"
  >
    <div class="title text-xs-center" style="color: #000000">
      <span class="title">{{tank.name}}</span><br/>
      <span class="display-1">{{percent}}</span><br/>
      <span class="title">{{volume}}</span>
    </div>
  </v-progress-circular>
</template>

<style>
.tankGauge {
  margin: 10px;
}
</style>

<script>

export default {
  name: 'TankGauge',
  
  props: {
    tank: Object,
  },
  
  computed: {
  
    value() {
      return this.tank.filled * 100
    },
    
    percent() {
      return Math.round(this.tank.filled * 100) + '%'
    },
    
    volume() {
      if (! this.tank.units) return ''
      return (this.tank.liters * this.tank.units.fromLiters).toFixed(this.tank.units.precision) + this.tank.units.abbreviation
    },
    
    color() {
      if (this.tank.liters <= this.tank.criticalVolume)
        return 'red'
      else if (this.tank.liters <= this.tank.warningVolume)
        return 'yellow'
      else
        return 'green'
    },
    
  },
  
  methods: {
  
    gotoTank() {
      this.$router.push({name: 'tank', params: {id: this.tank.id}})
    },
    
  },
  
}

</script>
