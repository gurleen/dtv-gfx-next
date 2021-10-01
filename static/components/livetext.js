const liveTextObjects = {};

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
        if(element.willFade) {
            element.tween.play().then(() => {
                element.innerText = value;
                element.tween.reverse();
            })
        } else {
            element.innerText = value;
        }
    }
}

const dataStore = {};
customElements.define('live-text', LiveText);

const socket = io();
socket.on("data-update", (payload) => {
    console.log(payload);
    const hasDataStore = typeof dataStore !== 'undefined';
    for(const property in payload) {
        LiveText.update(property, payload[property]);
        if(hasDataStore) {
            dataStore[property] = payload[property];
        }
    }
});

function getFromSocket(key) {
    return new Promise(resolve => {
        socket.emit("get-key", key, (response) => {
            resolve(response)
        });
    });
}

socket.emit("get-data-cache");