"use strict";


(function(){
     // EMAIL Settings
    $("#btn_test_mail").click(function() {
        $.ajax({
            url: "/settings",
            data: {action : "test_email"},
            success: function (response) {
                toastr.success(response.success, "EMAIL");
            },
            error: function(response){
                toastr.error(response.error, "EMAIL");
            }
        });
    });
})();