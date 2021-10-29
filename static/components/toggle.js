class ToggleButton extends HTMLElement {
    constructor() {
        super();
        this.attachShadow({ mode: 'open' });

        const wrapper = document.createElement('button');
        wrapper.innerHTML = "<slot></slot>";
        wrapper.onclick = () => {
            socket.emit("update-key", this.key, "");
            socket.emit("set-key", {
                key: this.key,
                value: "",
                type: "state-update"
            });
        }

        this.shadowRoot.append(wrapper);
    }

    connectedCallback() {
        this.key = this.getAttribute("key");
    }
}

customElements.define('toggle-button', ToggleButton);