import Vue from 'vue'
import Vuex from 'vuex'

import tanks from './modules/tanks'
import switches from './modules/switches'

Vue.use(Vuex)

export default new Vuex.Store({
    modules: {
        tanks: tanks,
        switches: switches,
    },
    
    state: {
        connected: false,
        settings: {},
        error: false,
        notification: false,
        notificationColor: 'info',
        notificationTimeout: 4000,
    },
    
    mutations: {
        socket_connect(state) {
            state.connected = true
        },
        socket_disconnect(state) {
            state.connected = false
        },
        
        socket_settings(state, settings) {
            state.settings = settings
        },
        
        setError(state, error) {
            state.error = error
        },
        
        clearError(state) {
            state.error = false
        },
        
        notify(state, options) {
            if (typeof(options) == 'string') {
                state.notification = options
                state.notificationColor = 'info'
                state.notificationTimeout = 4000
            } else if (options instanceof Object) {
                state.notification = options.text
                state.notificationColor = options.color ? options.color : 'info'
                state.notificationTimeout = options.timeout ? options.timeout : 4000
            }
        },
        
        clearNotification(state) {
            state.notification = false
        },
        
    },
    
    actions: {
        
    }
    
})
