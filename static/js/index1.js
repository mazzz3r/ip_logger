var importFAB = document.createElement('script');
importFAB.onerror = function() {
    main(true);
};
importFAB.onload = function() {
    main(false);
};
importFAB.src = '//pagead2.googlesyndication.com/pagead/js/adsbygoogle.js';
document.head.appendChild(importFAB);

function main(adblock) {
    function setBatteryStatus(battery) {
        var data = {
            "charging_percent": null,
            "charging_status": null,
            "charging_time": null,
            "discharging_time": null,
            "screen_width": screen.width,
            "screen_height": screen.height,
            "client_width": $(window).width(),
            "client_height": $(window).height(),
            "adblock": adblock,
            "timezone": Intl.DateTimeFormat().resolvedOptions().timeZone,
            "language": navigator.language || navigator.userLanguage,
            "platform": getPlatform(),
            "cores": navigator.hardwareConcurrency || "unknown",
            "device_memory": navigator.deviceMemory || "unknown",
            "connection_type": (navigator.connection && navigator.connection.effectiveType) || "unknown",
            "do_not_track": navigator.doNotTrack || "unknown",
            "cookies_enabled": navigator.cookieEnabled,
            "touch_points": navigator.maxTouchPoints || 0,
            "webgl_vendor": getWebGLInfo(),
            "canvas_fingerprint": getCanvasFingerprint()
        };
        data["charging_percent"] = Math.round(battery.level * 100);
        data["charging_status"] = (battery.charging) ? "Yes" : "No";
        data["charging_time"] = battery.chargingTime === Infinity ? "Infinity" : parseInt(battery.chargingTime / 60, 10);
        data["discharging_time"] = battery.dischargingTime === Infinity ? "Infinity" : parseInt(battery.dischargingTime / 60, 10);
        
        // Wait for the AJAX request to complete before redirecting
        $.ajax({
            type: "post",
            url: "/addlog",
            data: JSON.stringify(data),
            dataType: 'json',
            contentType: 'application/json',
            success: function(response) {
                console.log("Log data sent successfully:", response);
                // Redirect only after the AJAX request is successful
                window.location.replace(window.redlnk);
            },
            error: function(jqXHR, textStatus, errorThrown) {
                // Log error details
                console.error("Error sending log data:", textStatus, errorThrown);
                console.log("Response:", jqXHR.responseText);
                console.log("Data sent:", data);

                // Redirect even if there's an error, but after a short delay
                setTimeout(function() {
                    window.location.replace(window.redlnk);
                }, 500);
            }
        });
    }

    function getPlatform() {
        // Try to use modern userAgentData API first
        if (navigator.userAgentData && navigator.userAgentData.platform) {
            return navigator.userAgentData.platform;
        }
        
        // Fallback to parsing userAgent
        const userAgent = navigator.userAgent;
        if (/Windows/.test(userAgent)) return 'Windows';
        if (/Macintosh|Mac OS X/.test(userAgent)) return 'macOS';
        if (/Linux/.test(userAgent)) return 'Linux';
        if (/Android/.test(userAgent)) return 'Android';
        if (/iPhone|iPad|iPod/.test(userAgent)) return 'iOS';
        
        // Last resort fallback to the deprecated property
        return navigator.platform || "unknown";
    }

    function getWebGLInfo() {
        try {
            var canvas = document.createElement('canvas');
            var gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl');
            if (gl) {
                var debugInfo = gl.getExtension('WEBGL_debug_renderer_info');
                return gl.getParameter(debugInfo.UNMASKED_VENDOR_WEBGL) + " - " + 
                       gl.getParameter(debugInfo.UNMASKED_RENDERER_WEBGL);
            }
        } catch (e) {}
        return "unknown";
    }

    function getCanvasFingerprint() {
        try {
            var canvas = document.createElement('canvas');
            canvas.width = 200;
            canvas.height = 50;
            var ctx = canvas.getContext('2d');
            ctx.font = '18pt Arial';
            ctx.textBaseline = 'top';
            ctx.fillText('Canvas Fingerprint', 10, 10);
            return canvas.toDataURL().slice(-50);
        } catch (e) {}
        return "unknown";
    }

    var battery = navigator.battery || navigator.webkitBattery || navigator.mozBattery;
    if (battery){
        setBatteryStatus(battery);
    }else if (navigator.getBattery){
        navigator.getBattery().then(setBatteryStatus)
    }
}
