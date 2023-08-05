"use strict";


(function () {
    // Adds hidden fields for each submit button for identification on the server side
    $(":submit").each(function () {
        $(this).closest("form").append($("<input type='hidden'>").attr({
            name: $(this).attr("name"),
            value: $(this).attr("value")
        }));
    });

    // Acts as a form submission for all forms.
    $("form").submit(function (e) {
        $.ajax({
            type: "POST",
            url: "/settings",
            data: $(this).serialize(),
            success: function (response) {
                toastr.success(response.success, "SETTINGS");
            },
            error: function (xhr, ajaxOptions, thrownError) {
                for (var error in xhr.responseJSON.error) {
                    toastr.error(error, "SETTINGS");
                }
            }
        });

        e.preventDefault(); // block the traditional submission of the form.
    });

    /**
     * Dropdown selection lists
     */
    $(".select2-selection--single").select2({
        theme: "bootstrap"
    });

    $(".select2-selection--multiple").select2({
        theme: "bootstrap"
    });

    // Various
    $(".i-checks").iCheck({
        checkboxClass: "icheckbox_square-green",
        radioClass: "iradio_square-green"
    });
})();
