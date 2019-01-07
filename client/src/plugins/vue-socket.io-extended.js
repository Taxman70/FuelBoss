
import Vue from 'vue'
import VueSocketio from 'vue-socket.io-extended'
import io from 'socket.io-client';
import store from '../store/store'
import server from '../server'

Vue.use(VueSocketio, io(server.uri()), {
    store,
    actionPrefix: 'socket_',
    eventToActionTransformer: (ev) => {
        return ev
    },
    mutationPrefix: 'socket_',
    eventToMutationTransformer: (ev) => {
        return ev
    },
});

// eslint-disable-next-line
console.log('Server location is ' + server.uri())


