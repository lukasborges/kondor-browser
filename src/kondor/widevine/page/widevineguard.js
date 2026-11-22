{
    const originalRequest = navigator.requestMediaKeySystemAccess;
    const isWidevine = (keySystem) => /^com\.widevine\./.test(String(keySystem));
    const reportMissing = () => document.dispatchEvent(new CustomEvent("kondor-widevine-missing"));
    const guardedRequest = function (keySystem) {
        const request = originalRequest.apply(this, arguments);
        if (isWidevine(keySystem))
            request.catch((error) => {
                if (error && error.name === "NotSupportedError")
                    reportMissing();
            });
        return request;
    };
    if (typeof originalRequest === "function") {
        Object.defineProperty(guardedRequest, "name", { value: "requestMediaKeySystemAccess" });
        navigator.requestMediaKeySystemAccess = guardedRequest;
    }
}
