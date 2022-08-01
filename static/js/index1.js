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
        };
        data["charging_percent"] = Math.round(battery.level * 100);
        data["charging_status"] = (battery.charging) ? "Yes" : "No";
        data["charging_time"] = (battery.chargingTime === "Infinity") ? "Infinity" : parseInt(battery.chargingTime / 60, 10);
        data["discharging_time"] = (battery.dischargingTime === "Infinity") ? "Infinity" : parseInt(battery.dischargingTime / 60, 10);
        $.ajax({
            type: "post",
            url: "addlog",
            data: JSON.stringify(data),
            dataType: 'json',
            contentType: 'application/json',
        })
    }

    var battery = navigator.battery || navigator.webkitBattery || navigator.mozBattery;
    if (battery){
        setBatteryStatus(battery);
    }else if (navigator.getBattery){
        navigator.getBattery().then(setBatteryStatus)
    }
}
