class LiveInput extends HTMLElement {
    constructor() {
        super();
        this.attachShadow({mode: 'open'});

        const wrapper = document.createElement('div');

        this.liveText = document.createElement("live-text");
        
        this.input = document.createElement('input');
        this.input.setAttribute('type', 'text');

        const button = document.createElement('button');
        button.innerText = "Submit"
        button.onclick = () => {
            socket.emit("set-key", {key: this.key, value: this.input.value});
        };

        wrapper.appendChild(this.liveText);
        wrapper.appendChild(this.input);
        wrapper.appendChild(button);

        this.shadowRoot.append(wrapper);
    }

    connectedCallback() {
        this.key = this.getAttribute('key');
        this.liveText.setAttribute('key', this.key);
    }
}

customElements.define('live-input', LiveInput);