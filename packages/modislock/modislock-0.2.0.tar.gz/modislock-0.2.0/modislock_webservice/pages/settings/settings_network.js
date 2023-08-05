"use strict";

/**
 * @brief disables network fields
 */
function network_disable() {
    $("input[id$='address']").prop("disabled", true);
}

/**
 * @brief enables network fields
 */
function network_enable() {
    $("input[id$='address']").prop("disabled", false);
}


(function(){
    var dhcp_mode = $("#dhcp_mode");

     // NETWORKING Settings
    if (dhcp_mode.is(":checked")) {
        network_disable();
    } else {
        network_enable();
    }

        // Toggle the visibility of the network fields based on switch
    dhcp_mode.change(function () {
        if ($(this).is(':checked')) {
            network_disable();
        } else {
            network_enable();
        }
    });
})();