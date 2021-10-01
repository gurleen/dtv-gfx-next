class LiveImage extends HTMLElement {
    constructor() {
        super();
        this.attachShadow({mode: 'open'});

        const wrapper = document.createElement("div");
        wrapper.style = "display: flex; align-items: center; justify-content: center;";
        this.shadowRoot.appendChild(wrapper);

        const img = document.createElement('img');
        img.style = "max-width: 70%; max-height: 70%;"
        this.img = img;
        wrapper.appendChild(img);
    }

    async connectedCallback() {
        let key = this.getAttribute("key");
        let url = await getFromSocket(key);
        this.img.setAttribute("src", url);
    }
}

customElements.define('live-image', LiveImage);