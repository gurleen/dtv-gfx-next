class LiveText extends HTMLElement {
    static liveTextObjects = {};

    constructor() {
        super();
    }

    connectedCallback() {
        let key = this.getAttribute("key");
        this.willFade = this.getAttribute("fade") === "true";
        LiveText.liveTextObjects[key] = this;
        if(this.willFade) {
            this.tween = gsap.to(this, {opacity: 0, duration: 0.1});
        }
    }

    static update(key, value) {
        if(!(key in this.liveTextObjects)) { return; }
        let element = this.liveTextObjects[key];
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

customElements.define('live-text', LiveText);

const socket = io();
socket.on("data-update", (payload) => {
    console.log(payload);
    for(const property in payload) {
        LiveText.update(property, payload[property]);
    }
});

socket.emit("get-cache");