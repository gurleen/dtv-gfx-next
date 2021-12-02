const socket = io()
const TextInput = {
    props: ["key"],
    template: `<div>
        <input v-model="lt[key]">
    </div>`
}
const vue = new Vue({
    el: ".app",
    components: {
        TextInput
    },
    data: {
        lt: {teams: [[], []], homeKey: 0, awayKey: 1},
    },
    /*
    watch: {
        'lt': {
            deep: true,
            handler: (oldVal, newVal) => {
                console.log(shallowDiff(oldVal, newVal))
            }
        }
    },
    */
    async created() {
        this.lt = await (await fetch("/cache")).json()
    },
    mounted() {
        socket.on("state-update", (payload) => {
            this.lt = { ...this.lt, ...payload }
        })
    }
})

function shallowDiff(oldVal, newVal) {
    const keys1 = Object.keys(oldVal)
    let rv = {}
    for(key in keys1) {
        if(oldVal[key] != newVal[key]){
            rv = {...rv, key: newVal[key]}
        }
    }
    return rv
}