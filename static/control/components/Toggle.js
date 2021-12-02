export default {
    name: 'ToggleButton',
    props: ['key', 'text'],
    methods: {
        doToggle: function () {
            socket.emit(this.key, '')
        }
    },
    template: `
    <button @click="doToggle()">{{ text }}</button>
    `
}