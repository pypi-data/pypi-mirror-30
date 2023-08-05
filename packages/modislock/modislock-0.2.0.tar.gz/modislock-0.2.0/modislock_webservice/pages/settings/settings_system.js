"use strict";


(function (){
    // System
    $("#datetimepicker1").datetimepicker({
        format: "HH:mm:ss YYYY-MM-DD",
        sideBySide: true,
        widgetPositioning: {horizontal: "right", vertical: "bottom"},
        allowInputToggle: true
    });

    /**
    * Purge Events from database
    */
    $("#purge_btn").confirmation({
        title: "Confirm Purge all Events",
        btnOkClass: "btn-xs btn-warning",
        btnOkIcon: "fa fa-exclamation",
        btnOkLabel: "Purge All",
        btnCancelClass: "btn-xs btn-default",
        btnCancelIcon: "fa fa-close",
        btnCancelLabel: "Cancel",
        onConfirm: function() {
            $.ajax({
                url: "/settings",
                type: "POST",
                data: {action : "purge"},
                success: function (response) {
                    toastr.success(response.success, "DATABASE");
                },
                error: function (xhr, ajaxOptions, thrownError) {
                    toastr.error(xhr.responseJSON.error, "DATABASE");
                }
            });
        },
        onCancel: function () {
            console.log("Purge cancelled");
        }
    });

    /**
     * Reboot system
     */
    $("#reboot_btn").confirmation({
        title: "Confirm Reboot",
        btnOkClass: "btn-xs btn-danger",
        btnOkIcon: "fa fa-check",
        btnOkLabel: "Reboot",
        btnCancelClass: "btn-xs btn-default",
        btnCancelIcon: "fa fa-close",
        btnCancelLabel: "Cancel",
        onConfirm: function () {
            $.ajax({
                url: "/settings",
                type: "POST",
                data: {action: "reboot"},
                success: function (response) {
                    toastr.success(response.success, "SYSTEM");
                    window.location.href = "/settings/reboot";
                },
                error: function (xhr, ajaxOptions, thrownError) {
                    toastr.error(xhr.responseJSON.error, "SYSTEM");
                }
            });
        },
        onCancel: function () {
            console.log("Reboot option cancelled");
        }
    });
})();