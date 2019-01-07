
export default {
    
    uri() {
        let loc = location.href
        if (process.env.NODE_ENV === 'development') {
            if (process.env.VUE_APP_SERVER_LOCATION)
                loc = process.env.VUE_APP_SERVER_LOCATION
            else
                loc = 'http://localhost:8080'
        }
        return loc
    },
        
}
