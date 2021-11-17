const liveTextObjects = {};
let alpineInit = false;
let cache = {
    "homePlayer": {"uni": "", "pos": "", "normalName": ""},
    "awayPlayer": {"uni": "", "pos": "", "normalName": ""},
    "stats": {teams: {H: [], V: []}}
};

document.addEventListener('alpine:init', () => {
    Alpine.store('sock', {
        data: {...cache},
        update (data) {
            this.data = {...this.data, ...data}
        },
        getHomePlayer(name) {
            return this.data.stats.teams.H.find(p => p.name == name)
        },
        getAwayPlayer(name) {
            return this.data.stats.teams.V.find(p => p.name == name)
        }
    })
    Alpine.magic('sock', (el, { Alpine }) => Alpine.store('sock').data)
    alpineInit = true;
})

class LiveText extends HTMLElement {
    constructor() {
        super();
    }

    connectedCallback() {
        let key = this.getAttribute("key");
        this.willFade = this.getAttribute("fade") === "true";
        liveTextObjects[key] = this;
        if(this.willFade) {
            this.tween = gsap.to(this, {opacity: 0, duration: 0.1});
        }
    }

    static update(key, value) {
        if(!(key in liveTextObjects)) { return; }
        let element = liveTextObjects[key];
        if(element.innerText == value) { return ;}
        if(element.willFade) {
            element.tween.play().then(() => {
                element.innerText = value;
                element.tween.reverse();
            })
        } else {
            element.innerText = value;
        }
    }

    static updateBulk(payload) {
        cache = {...cache, ...payload};
        if(alpineInit) {
            Alpine.store('sock').update(payload);
        }
        for(const property in payload) {
            LiveText.update(property, payload[property]);
        }
    }
}

customElements.define('live-text', LiveText);

const socket = io();
socket.on("state-update", LiveText.updateBulk);

function getFromSocket(key) {
    return new Promise(resolve => {
        socket.emit("get-key", key, (response) => {
            resolve(response)
        });
    });
}

function updateKey(key, value) {
    return new Promise(resolve => {
        socket.emit("update-key", key, value, (_) => {
            resolve()
        })
    })
}

socket.emit("get-cache", LiveText.updateBulk);