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

            let H = this.lt.boxscore["teams"][this.lt.homeKey - 1]["total"]["team"]
            let V = this.lt.boxscore["teams"][this.lt.awayKey - 1]["total"]["team"]
            switch(this.lt.compStatName) {
                case 'Field Goals':
                    return {home: `${H.sTwoPointersMade}/${H.sTwoPointersAttempted}`, away: `${V.sTwoPointersMade}/${V.sTwoPointersAttempted}`}
                case '3PT FG':
                    return {home: `${H.sThreePointersMade}/${H.sThreePointersAttempted}`, away: `${V.sThreePointersMade}/${V.sThreePointersAttempted}`}
                case 'Free Throws':
                    return {home: `${H.sFreeThrowsMade}/${H.sFreeThrowsAttempted}`, away: `${V.sFreeThrowsMade}/${V.sFreeThrowsAttempted}`}
                case 'Turnovers':
                    return {home: H.sTurnovers, away: V.sTurnovers}
                case 'Blocks':
                    return {home: H.sBlocks, away: V.sBlocks}
                case 'Steals':
                    return {home: H.sSteals, away: V.sSteals}
                case 'Rebounds':
                    return {home: H.sReboundsTeam, away: V.sReboundsTeam}
                case 'Off. Reb':
                    return {home: H.sReboundsOffensive, away: V.sReboundsOffensive}
                case 'Def. Reb':
                    return {home: H.sReboundsDefensive, away: V.sReboundsDefensive}
                default: 
                    return {home: "", away: ""}
            }
        },
        awayLth: function () {
            try {
                let pno = this.lt.awayPlayerNum
                let player = this.lt.teams[this.lt.awayKey - 1].players.find(p => p.pno == pno)
                let stats = this.lt.boxscore.teams[this.lt.awayKey - 1].total.players.find(p => p.pno == pno)
                return {
                    name: `${player.firstName} ${player.familyName}`.toUpperCase(),
                    stat: `${stats.sPoints} PTS ${stats.sTwoPointersMade}/${stats.sTwoPointersAttempted} FG ${stats.sAssists} AST`,
                    num: player.shirtNumber,
                    pos: player.playingPosition[0]
                }
            } catch(err) {
                return {}
            }
        },
        homeLth: function () {
            try {
                let pno = this.lt.homePlayerNum
                let player = this.lt.teams[this.lt.homeKey - 1].players.find(p => p.pno == pno)
                let stats = this.lt.boxscore.teams[this.lt.homeKey - 1].total.players.find(p => p.pno == pno)
                return {
                    name: `${player.firstName} ${player.familyName}`.toUpperCase(),
                    stat: `${stats.sPoints} PTS ${stats.sTwoPointersMade}/${stats.sTwoPointersAttempted} FG ${stats.sAssists} AST`,
                    num: player.shirtNumber,
                    pos: player.playingPosition[0]
                }
            } catch(err) {
                return {}
            }
        },
        awayScoringDrought: function () {
            let lastScore = this.lt["last_away_score"]
            if(lastScore == null) return ""
            return timeDelta(lastScore.clock.slice(0, -3), this.lt.clock)
        },
        homeScoringDrought: function () {
            let lastScore = this.lt["last_home_score"]
            if(lastScore == null) return ""
            return timeDelta(lastScore.clock.slice(0, -3), this.lt.clock)
        },
        homeInfo: function () {
            if(this.lt.homeInfoSliderText == "SCORING DROUGHT") return `SCORING DROUGHT ${this.homeScoringDrought}`
            return this.lt.homeInfoSliderText
        },
        awayInfo: function () {
            if(this.lt.awayInfoSliderText == "SCORING DROUGHT") return `SCORING DROUGHT ${this.awayScoringDrought}`
            return this.lt.awayInfoSliderText
        }
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
        tl.play()
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
}


function next() {
    console.log("next called")
    // tl.play()
}

function stop() {
    console.log("stop called")
}