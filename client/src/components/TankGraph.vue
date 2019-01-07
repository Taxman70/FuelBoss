<template>
  <img
    class="tankGraph"
    :src="imageURL"
  />
</template>

<style>
.tankGraph {
  margin: 10px;
}
</style>

<script>

import server from '../server'

export default {
  name: 'TankGraph',
  
  props: {
    tank: Object,
    graph: Number,
  },
  
  data() {
    return {
      ts: (new Date()).valueOf(),
    }
  },
  
  computed: {
  
    imageURL() {
      return server.uri() +
        '/tank/' + this.tank.id +
        '/rrd/' + this.graph +
        '?ts=' + this.ts
    },
    
  },
  
  methods: {
  
    refresh() {
      this.ts = (new Date()).valueOf()
    },
  
  },
  
  sockets: {
  
    tank_changed(tank) {
      if (this.tank && (tank.id === this.tank.id))
        this.refresh()
    },
    
  },  
  
  
}

</script>
