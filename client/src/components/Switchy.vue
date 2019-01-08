<template>
  <v-switch
    class="switchy"
    :label="switchy.name"
    v-model="switchy.value"
    color="green"
    readonly
  />
</template>

<style>
.switchy {
  flex: none;
  margin: 10px;
}
</style>

<script>

export default {
  name: 'Switchy',
  
  props: {
    switchy: Object,
  },
  
  methods: {
  
    gotoSwitchy() {
      this.$router.push({name: 'switchy', params: {id: this.switchy.id}})
    },
    
  },
  
}

</script>
