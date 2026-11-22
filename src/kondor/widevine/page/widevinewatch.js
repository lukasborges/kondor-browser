{
    let bridge = null;
    let isPending = false;

    const send = () => {
        if (bridge)
            bridge.reportMissing();
        else
            isPending = true;
    };

    const connectBridge = (objects) => {
        bridge = objects.kondorWidevine;
        if (bridge && isPending)
            bridge.reportMissing();
    };

    if (window.__kondorChannel) {
        document.addEventListener("kondor-widevine-missing", send);
        window.__kondorChannel.then(connectBridge);
    }
}
