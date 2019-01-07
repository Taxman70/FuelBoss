<template>
  <v-app>
    <html-title :title="title"/>
    
    <v-navigation-drawer
      persistent
      clipped
      v-model="drawer"
      enable-resize-watcher
      fixed
      app
    >
      <v-list>
        <v-list-tile @click="gotoAbout()">
          <v-list-tile-action>
            <v-icon>mdi-information</v-icon>
          </v-list-tile-action>
          <v-list-tile-title>About</v-list-tile-title>
        </v-list-tile>
          
        <v-divider/>
        
        <v-list-group
          prepend-icon="mdi-settings"
          no-action
        >
          <v-list-tile slot="activator">
            <v-list-tile-title>System</v-list-tile-title>
          </v-list-tile>

          <v-list-tile @click="restart()">
            <v-list-tile-title>Restart</v-list-tile-title>
            <v-list-tile-action>
              <v-icon>mdi-restart</v-icon>
            </v-list-tile-action>
          </v-list-tile>

          <v-list-tile @click="shutdown()">
            <v-list-tile-title>Shutdown</v-list-tile-title>
            <v-list-tile-action>
              <v-icon>mdi-power</v-icon>
            </v-list-tile-action>
          </v-list-tile>
          
        </v-list-group>
          
      </v-list>
    </v-navigation-drawer>
    
    <v-toolbar
      app
      clipped-left
      color="primary"
      dark
    >
      <v-toolbar-side-icon
        v-if="!showBack"
        @click.stop="drawer = !drawer"
      ></v-toolbar-side-icon>
      
      <v-btn
        v-if="showBack"
        icon
        @click="goBack()">
        <v-icon>mdi-arrow-left</v-icon>
      </v-btn>      
      
      <v-toolbar-title>{{title}}</v-toolbar-title>
      <v-spacer></v-spacer>

    </v-toolbar>
    
    <v-content>
      <router-view
        @show-page="showPage"
      />
    </v-content>
    
    <connecting-dialog/>
    <error-dialog/>
    <notifier/>
    <confirm-dialog ref="confirmDialog"/>
    
  </v-app>
</template>

<script>

import { mapState } from 'vuex'
import HTMLTitle from './components/HTMLTitle'
import ConnectingDialog from './components/ConnectingDialog'
import ErrorDialog from './components/ErrorDialog'
import Notifier from './components/Notifier'
import ConfirmDialog from './components/ConfirmDialog'

export default {
  name: 'App',
  data () {
    return {
      pageTitle: false,
      drawer: false,
      showBack: false,
    }
  },
  
  components: {
    'html-title': HTMLTitle,
    ConnectingDialog,
    ErrorDialog,
    Notifier,
    ConfirmDialog,
  },
  
  computed: {
    ...mapState({
      settings: state => state.settings,
    }),
    title () {
      return this.settings.appTitle + (this.pageTitle ? (": " + this.pageTitle) : "");
    },
  },
  
  methods: {
  
    goBack() {
      window.history.length > 1
        ? this.$router.go(-1)
        : this.$router.push('/')
    },
    
    gotoAbout() {
      this.drawer = false
      this.$router.push({name: 'about'})
    },
    
    restart() {
      this.$refs.confirmDialog.open('Restart', 'Are you sure you want to restart the system?').then(() => {
        this.$socket.emit('core_restart', (res) => {
          if (res.error) {
              this.$store.commit('setError', res.error)
          }
        })
      }, ()=>{})
    },
    
    shutdown() {
      this.$refs.confirmDialog.open('Shutdown', 'Are you sure you want to shutdown the system?').then(() => {
        this.$socket.emit('core_shutdown', (res) => {
          if (res.error) {
              this.$store.commit('setError', res.error)
          }
        })
      }, ()=>{})
    },
    
    showPage(pageTitle) {
      this.pageTitle = pageTitle
      this.showBack = !!pageTitle
    },
    
  },
  
}
</script>
