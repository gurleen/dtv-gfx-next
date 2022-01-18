function createAnimations() {
    tl = gsap.timeline({ paused: true, onComplete: () => { this.tl.seek(0); this.tl.pause() } })
    tl.from(".anim1", { duration: .75, scaleX: 0, transformOrigin: "left", ease: "power4.inOut" })
    tl.from(".anim2", { duration: .5, y: 20, opacity: 0, stagger: 0.03 }, "-=.5")
    tl.addPause(1.5)
    tl.to("#scorebug", { duration: .2, opacity: 0 })
    window.tl = tl

    // SLIDER ANIMATION
    var slider1Tl = gsap.timeline()
    slider1Tl.from("#slider1", { duration: .5, y: 36, opacity: 0, ease: "power4.inOut" })
    slider1Tl.reverse()
    window.slider1Tl = slider1Tl

    // TEXT SLIDER
    var slider2Tl = gsap.timeline()
    slider2Tl.from("#slider2", { duration: .5, y: 36, opacity: 0, ease: "power4.inOut" })
        .from('#slider2Anim2', { duration: .7, x: 10, opacity: 0, ease: "power4.inOut" }, "-=.5")
    slider2Tl.reverse()
    window.slider2Tl = slider2Tl

    var homeLthTl = gsap.timeline()
    homeLthTl.from("#homeLthSlider", { duration: .5, y: 36, opacity: 0, ease: "power4.inOut" })
        .from('#slider3Anim2', { duration: .7, x: 10, opacity: 0, ease: "power4.inOut" }, "-=.5")
    homeLthTl.reverse()
    window.homeLthTl = homeLthTl

    var awayLthTl = gsap.timeline()
    awayLthTl.from("#awayLthSlider", { duration: .5, y: 36, opacity: 0, ease: "power4.inOut" })
        .from('#slider4Anim2', { duration: .7, x: 10, opacity: 0, ease: "power4.inOut" }, "-=.5")
    awayLthTl.reverse()
    window.awayLthTl = awayLthTl

    var homeInfoTl = gsap.timeline()
    homeInfoTl.from("#homeInfoSlider", { duration: .5, y: 36, opacity: 0, ease: "power4.inOut" })
        .from('#slider5Anim2', { duration: .7, x: 10, opacity: 0, ease: "power4.inOut" }, "-=.5")
    homeInfoTl.reverse()
    window.homeInfoTl = homeInfoTl

    var awayInfoTl = gsap.timeline()
    awayInfoTl.from("#awayInfoSlider", { duration: .5, y: 36, opacity: 0, ease: "power4.inOut" })
        .from('#slider6Anim2', { duration: .7, x: 10, opacity: 0, ease: "power4.inOut" }, "-=.5")
        awayInfoTl.reverse()
    window.awayInfoTl = awayInfoTl
}

function createToggleConnections(socket) {
    socket.on("state-update", (payload) => {
        if ("scoreboard:toggle" in payload) { tl.play() }
        if ("scoreboard:toggle-comp" in payload) { !slider1Tl.reversed() ? slider1Tl.reverse() : slider1Tl.play() }
        if ("scoreboard:toggle-text" in payload) { !slider2Tl.reversed() ? slider2Tl.reverse() : slider2Tl.play() }
        if ("scoreboard:toggle-home" in payload) { !homeLthTl.reversed() ? homeLthTl.reverse() : homeLthTl.play() }
        if ("scoreboard:toggle-away" in payload) { !awayLthTl.reversed() ? awayLthTl.reverse() : awayLthTl.play() }
        if ("scoreboard:toggle-home-info" in payload) { !homeInfoTl.reversed() ? homeInfoTl.reverse() : homeInfoTl.play() }
        if ("scoreboard:toggle-away-info" in payload) { !awayInfoTl.reversed() ? awayInfoTl.reverse() : awayInfoTl.play() }
    })
}