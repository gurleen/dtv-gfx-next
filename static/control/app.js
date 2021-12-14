const socket = io()

const COMP_STATS = [
    "Field Goals",
    "3PT FG",
    "Free Throws",
    "Turnovers",
    "Blocks",
    "Steals",
    "Rebounds",
    "Off. Reb",
    "Def. Reb"
]

Vue.component(`text-input`, {
    props: ["inpKey", "value"],
    data: function () {
        return {
            currentValue: this.value,
        }
    },
    template: `<div>
        <p> {{ inpKey }}: {{ this.$parent.lt[inpKey] }} </p> <input v-model="currentValue"> <button v-on:click="submit">Push</button>
    </div>`,
    methods: {
        submit() {
            updateKey(this.inpKey, this.currentValue)
        }
    } 
})

Vue.component(`toggle-button`, {
    props: ["toggleKey", "name"],
    template: `<div>
        <button v-on:click="submit">Toggle {{ name }}</button>
    </div>`,
    methods: {
        submit() {
            updateKey(this.toggleKey, null)
        }
    }
})

const vue = new Vue({
    el: ".app",
    data: {
        lt: {teams: [[], []], homeKey: 0, awayKey: 1, mediaTimeout: false},
        homePlayer: {},
        awayPlayer: {},
        compStat: null,
        compStatNames: COMP_STATS,
        textSliderDefaults: [
            {title: "Commentators", subtitle: "Ari Bluestein and Kayla Bacon"},
            {title: "Venue", subtitle: "Daskalakis Athletic Center - Philadelphia, PA"}
        ],
        selectedDefault: {},
        textSliderTitle: "",
        textSliderSubtitle: ""
    },
    async created() {
        this.lt = await (await fetch("/cache")).json()
    },
    mounted() {
        socket.on("state-update", (payload) => {
            console.log(payload)
            this.lt = { ...this.lt, ...payload }
        })
    },
    methods: {
        inc(dataKey, amount) {
            updateKey(dataKey, parseInt(this.lt[dataKey]) + amount)
        },
        uk(key, val) {
            updateKey(key, val)
        },
        usePreset() {
            this.textSliderTitle = this.selectedDefault.title
            this.textSliderSubtitle = this.selectedDefault.subtitle
        },
        updateSlider() {
            updateKey("textSliderTitle", this.textSliderTitle)
            updateKey("textSliderSubtitle", this.textSliderSubtitle)
        },
        dskUpdate(state) {
            fetch(`http://10.248.66.57/v1/shortcut?name=main_dsk1_value&value=${state}`)
        }
    }
})

function updateKey(key, value) {
    return new Promise(resolve => {
        socket.emit("update-key", key, value, (_) => {
            resolve()
        })
    })
}