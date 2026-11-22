if (location.protocol === "devtools:") {
    const canDockParameter = "can_dock=true";
    const dockSidePrefix = "kondor:devtools-dock:";
    const readyMessage = "kondor:devtools-dock-ready";
    const presentedPollInterval = 50;

    const showDockSideRow = () => {
        if (location.search.includes(canDockParameter))
            return;
        const separator = location.search ? "&" : "?";
        const search = location.search + separator + canDockParameter;
        history.replaceState(history.state, "", location.pathname + search + location.hash);
    };

    const loadModule = (path) => import(new URL(path, location.href).href);

    const loadModules = () => Promise.all([
        loadModule("ui/legacy/legacy.js"),
        loadModule("panels/emulation/emulation.js"),
    ]);

    const keepWholeView = (advancedApp) => {
        advancedApp.prototype.updateForDocked = function() { this.updateForUndocked(); };
        advancedApp.prototype.isDocked = () => false;
    };

    const isPresented = () => document.querySelector("body > .root-view") !== null;

    const whenPresented = () => new Promise((resolve) => {
        const check = () => isPresented() ? resolve() : setTimeout(check, presentedPollInterval);
        check();
    });

    const hideScreencast = (screencast) => {
        const screencastApp = screencast.ScreencastApp.ScreencastApp.instance();
        screencastApp.enabledSetting.set(false);
        screencastApp.onScreencastEnabledChanged();
        screencastApp.toggleButton.setVisible(false);
    };

    const reportDockSide = (dockController) => {
        dockController.addEventListener("DockSideChanged", () =>
            console.log(dockSidePrefix + dockController.dockSide()));
    };

    const connect = ([legacy, emulation]) => {
        const advancedApp = emulation.AdvancedApp.AdvancedApp;
        const dockController = legacy.DockController.DockController.instance();
        keepWholeView(advancedApp);
        advancedApp.instance().updateForUndocked();
        reportDockSide(dockController);
        globalThis.kondorShowDockSide = (side) => dockController.setDockSide(side);
        console.log(readyMessage);
    };

    const reportFailure = (feature) => (error) => console.warn(`Kondor: ${feature} is off`, error);

    showDockSideRow();
    whenPresented().then(loadModules).then(connect, reportFailure("DevTools dock side"));
    whenPresented().then(() => loadModule("panels/screencast/screencast.js"))
        .then(hideScreencast, reportFailure("hiding the DevTools screencast"));
}
