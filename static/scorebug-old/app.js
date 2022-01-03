const SCORING_PLAYS = ["3PTR", "JUMPER", "LAYUP", "FT"]
const socket = io();
const vue = new Vue({
    el: ".app",
    data: {
        lt: {stats: {plays: [], teams: {H: [], V: []}}},
    },
    computed: {
        compStat: function () {
            if(this.lt.stats.box === undefined) return {}
            /*return {
                home: this.lt.stats.box["H"][this.lt.compStatType],
                away: this.lt.stats.box["V"][this.lt.compStatType]
            }*/
            let H = this.lt.stats.box["H"]
            let V = this.lt.stats.box["V"]
            switch(this.lt.compStatName) {
                case 'Field Goals':
                    return {home: `${H.fgm}/${H.fga}`, away: `${V.fgm}/${V.fga}`}
                case '3PT FG':
                    return {home: `${H.fgm3}/${H.fga3}`, away: `${V.fgm3}/${V.fga3}`}
                case 'Free Throws':
                    return {home: `${H.ftm}/${H.fta}`, away: `${V.ftm}/${V.fta}`}
                case 'Turnovers':
                    return {home: H.to, away: V.to}
                case 'Blocks':
                    return {home: H.blk, away: V.blk}
                case 'Steals':
                    return {home: H.stl, away: V.stl}
                case 'Rebounds':
                    return {home: H.treb, away: V.treb}
                case 'Off. Reb':
                    return {home: H.oreb, away: V.oreb}
                case 'Def. Reb':
                    return {home: H.dreb, away: V.dreb}
                default: 
                    return {home: "", away: ""}
            }
        },
        awayLth: function () {
            let player = this.lt.stats.teams["V"][this.lt.awayPlayerNum]
            if(player === undefined) return {}
            let nameSplit = player.name.split(", ")
            return {
                name: `${nameSplit[1]} ${nameSplit[0]}`.toUpperCase(),
                stat: `${player.tp} PTS ${player.fgm}/${player.fga} FG ${player.ast} AST`,
                num: player.uni,
                pos: player.pos
            }
        },
        homeLth: function () {
            let player = this.lt.stats.teams["H"][this.lt.homePlayerNum]
            if(player === undefined) return {}
            let nameSplit = player.name.split(", ")
            return {
                name: `${nameSplit[1]} ${nameSplit[0]}`.toUpperCase(),
                stat: `${player.tp} PTS ${player.fgm}/${player.fga} FG ${player.ast} AST`,
                num: player.uni,
                pos: player.pos
            }
        },
        awayScoringDrought: function () {
            let lastScore = _.findLast(this.lt.stats.plays, play => play.vh == "V" && (SCORING_PLAYS.includes(play.type) && play.action == "GOOD"))
            if(lastScore === undefined) return {}
            return timeDelta(lastScore.time, this.lt.clock)
        },
        homeScoringDrought: function () {
            let lastScore = _.findLast(this.lt.stats.plays, play => play.vh == "H" && (SCORING_PLAYS.includes(play.type) && play.action == "GOOD"))
            if(lastScore === undefined) return {}
            return timeDelta(lastScore.time, this.lt.clock)
        },
    },
    async created() {
        this.lt = await (await fetch("/cache")).json()
    },
    mounted() {
        socket.on("state-update", (payload) => {
            this.lt = { ...this.lt, ...payload }
        })
        createAnimations()
        createToggleConnections(socket)
        // tl.play()
    }
});


function timeInSeconds(x) {
    let parts = x.split(":")
    return (parseInt(parts[0]) * 60) + parseInt(parts[1])
}


function timeDelta(a, b) {
    let diff = Math.abs(timeInSeconds(a) - timeInSeconds(b))
    let mins = Math.floor(diff / 60)
    let seconds = diff - (mins * 60)
    return `${mins}:${seconds}`
}

function play(input) {
    console.log("play called")
    console.log(input)
    tl.play()
}

function next() {
    console.log("next called")
    tl.play()
}

function stop() {
    console.log("stop called")
}