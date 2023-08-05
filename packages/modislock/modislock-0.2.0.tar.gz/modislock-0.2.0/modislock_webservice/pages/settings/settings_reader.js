"use strict";


(function(){
    /**
     * Sliders for time delay
     */
    $(".delay_slider").ionRangeSlider({
        min: 0,
        max: 9,
        step: 0.5,
        grid: true,
        prettify_enabled: true,
        onFinish: function(data){
            console.log(data.from);
        }
    });
})();