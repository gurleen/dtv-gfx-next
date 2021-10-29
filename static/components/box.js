class GBox extends HTMLElement {
    constructor() {
        super();
        this.attachShadow({ mode: 'open' });
        const wrapper = document.createElement('div');
        wrapper.innerHTML = "<slot></slot>";
        this.wrapper = wrapper;
        this.shadowRoot.append(wrapper);
    }

    async connectedCallback() {
        let color;
        const dc = this.getAttribute("dcolor");
        if(dc) { color = await getFromSocket(dc); }
        let c = hexToRgb(color || this.getAttribute("color") || "#000");
        console.log(this, c);
        const a = this.getAttribute("opacity") || "1"
        const rgba = this.hasAttribute("color")? `background-color: rgba(${c.r}, ${c.g}, ${c.b}, ${a});` : "";
        const style = `
        height: ${this.getAttribute("height")};
        width: ${this.getAttribute("width")};
        ${rgba}
        display: flex;
        justify-content: ${this.getAttribute("justify") || "center"};
        align-items: ${this.getAttribute("align") || "center"}
        `;
        this.wrapper.setAttribute('style', style);
    }
}

function hexToRgb(hex) {
    // Expand shorthand form (e.g. "03F") to full form (e.g. "0033FF")
    var shorthandRegex = /^#?([a-f\d])([a-f\d])([a-f\d])$/i;
    hex = hex.replace(shorthandRegex, function (m, r, g, b) {
        return r + r + g + g + b + b;
    });

    var result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
    return result ? {
        r: parseInt(result[1], 16),
        g: parseInt(result[2], 16),
        b: parseInt(result[3], 16)
    } : null;
}


customElements.define('g-box', GBox);