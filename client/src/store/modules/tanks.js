import Vue from 'vue'

export default {
    namespaced: true,
    
    state: {
        tanks: null,
        tank: {},
        loading: false,
    },
    
    getters: {
        
        sortedTanks(state) {
            if (state.tanks)
                return state.tanks.slice().sort((a, b) => {
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
        
        setTanks(state, tanks) {
            state.tanks = tanks
            state.loading = false
        },
        
        setTank(state, tank) {
            state.tank = tank
            state.loading = false
        },
        
        destroy(state) {
            state.tanks = null
            state.tank = {}
        },
        
        socket_tank_changed(state, tank) {
            if (state.tanks) {
                let d = state.tanks.find((e) => { return e.id === tank.id })
                if (d) {
                    Object.assign(d, tank)
                }
            }
            if (state.tank.id === tank.id) {
                Object.assign(state.tank, tank)
            }
        },
        
    },
    
    actions: {
        
        getAll({commit, state}) {
            return new Promise((resolve, reject) => {
                if (state.tanks)
                    resolve()
                else {
                    commit('loading')
                    Vue.prototype.$socket.emit('tank_getAll', (res) => {
                        if (res.error) {
                            commit('setError', res.error, {root: true})
                            reject()
                        } else {
                            commit('setTanks', res.tanks)
                            resolve(res.tanks)
                        }
                    })
                }
            })
        },
        
        getOne({commit}, id) {
            return new Promise((resolve, reject) => {
                commit('loading')
                Vue.prototype.$socket.emit('tank_getOne', id, (res) => {
                    if (res.error) {
                        commit('setError', res.error, {root: true})
                        reject()
                    } else {
                        commit('setTank', res.tank)
                        resolve(res.tank)
                    }
                })
            })
        },
        
    }
    
}
