class LiveInput extends HTMLElement {
    constructor() {
        super();
        this.attachShadow({ mode: 'open' });

        const wrapper = document.createElement('div');

        const label = document.createElement('label');
        const nameLabel = document.createElement('span');
        this.nameLabel = nameLabel;
        this.liveText = document.createElement('live-text');
        label.appendChild(nameLabel);
        label.appendChild(this.liveText);

        const uid = Date.now();
        this.input = document.createElement('input');
        this.input.setAttribute('type', 'text');
        this.input.setAttribute('name', uid);
        label.setAttribute('for', uid);

        const button = document.createElement('button');
        button.setAttribute('type', 'submit');
        button.innerText = "Submit"
        button.onclick = () => {
            socket.emit("update-key", this.key, this.input.value);
        };

        wrapper.appendChild(label);
        wrapper.appendChild(document.createElement('br'));
        wrapper.appendChild(this.input);
        wrapper.appendChild(button);

        this.shadowRoot.append(wrapper);
    }

    connectedCallback() {
        this.key = this.getAttribute('key');
        this.type = this.getAttribute('type') || 'data';
        console.log(this.type)
        this.liveText.setAttribute('key', this.key);
        this.nameLabel.innerText = `${this.key} - `;
    }
}

customElements.define('live-input', LiveInput);