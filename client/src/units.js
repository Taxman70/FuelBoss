
export default {

    toUnits(liters, conf) {
        return liters * conf.fromLiters
    },

    format(liters, conf, appendUnits = true) {
        let str = (liters * conf.fromLiters).toFixed(conf.precision)
        if (appendUnits)
            str += ' ' + conf.abbreviation
        return str
    },
    
}

