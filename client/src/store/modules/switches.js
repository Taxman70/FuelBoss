import Vue from 'vue'

export default {
    namespaced: true,
    
    state: {
        switches: null,
        switchy: {},
        loading: false,
    },
    
    getters: {
        
        sortedSwitches(state) {
            if (state.switches)
                return state.switches.slice().sort((a, b) => {
                    return a.id - b.id
                })
            else
                return []
        },
        
    },
  
    mutations: {
        
        loading(state) {
            state.loading = true
        },
        
        setSwitches(state, switches) {
            state.switches = switches
            state.loading = false
        },
        
        setSwitch(state, switchy) {
            state.switchy = switchy
            state.loading = false
        },
        
        destroy(state) {
            state.switches = null
            state.switchy = {}
        },
        
        socket_switch_changed(state, switchy) {
            if (state.switches) {
                let d = state.switches.find((e) => { return e.id === switchy.id })
                if (d) {
                    Object.assign(d, switchy)
                }
            }
            if (state.switchy.id === switchy.id) {
                Object.assign(state.switchy, switchy)
            }
        },
        
    },
    
    actions: {
        
        getAll({commit, state}) {
            return new Promise((resolve, reject) => {
                if (state.switches)
                    resolve()
                else {
                    commit('loading')
                    Vue.prototype.$socket.emit('switch_getAll', (res) => {
                        if (res.error) {
                            commit('setError', res.error, {root: true})
                            reject()
                        } else {
                            commit('setSwitches', res.switches)
                            resolve(res.switches)
                        }
                    })
                }
            })
        },
        
        getOne({commit}, id) {
            return new Promise((resolve, reject) => {
                commit('loading')
                Vue.prototype.$socket.emit('switch_getOne', id, (res) => {
                    if (res.error) {
                        commit('setError', res.error, {root: true})
                        reject()
                    } else {
                        commit('setSwitch', res.switchy)
                        resolve(res.switchy)
                    }
                })
            })
        },
        
    }
    
}
