var Battery = Backbone.Model.extend({
	initialize: function(){
		var that = this;
		function updateBatteryInfo(){
			that.updateBatteryInfo();
		}
		function processBattery(batteryManager){
			that.set('batteryManager', batteryManager);
			batteryManager.onchargingchange = updateBatteryInfo;
			batteryManager.onchargingtimechange = updateBatteryInfo;
			batteryManager.ondischargingtimechange = updateBatteryInfo;
			batteryManager.onlevelchange = updateBatteryInfo;
			that.updateBatteryInfo();
		}
		if (navigator.battery){
			processBattery(navigator.battery);
		}
		else if (typeof navigator.getBattery == 'function'){
			navigator.getBattery().then(processBattery);
		}
	},
	updateBatteryInfo: function(){
		var batteryManager = this.get('batteryManager');
		this.set({
			charging: batteryManager.charging,
			chargingTime: batteryManager.chargingTime,
			dischargingTime: batteryManager.dischargingTime,
			level: batteryManager.level
		});
	}
});
var battery = new Battery();