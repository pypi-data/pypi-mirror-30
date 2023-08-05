"use strict";

/**
 * @brief disables network fields
 */
function ldap_disable() {
    $("#ldap_form :input:not(#ldap_enable):not(#submit_ldap_btn)").prop("disabled", true);
}

/**
 * @brief enables network fields
 */
function ldap_enable() {
    $("#ldap_form :input:not(#ldap_enable):not(#submit_ldap_btn)").prop("disabled", false);
}


(function (){
    var ldap_mode = $("#ldap_enable");
    var ldap_ssl_mode = $("#ldap_use_ssl");
    var ldap_is_ad = $("#ldap_is_active_directory");

    if(ldap_ssl_mode.is(":checked")){
        $("#ldap_use_ssl_hidden").prop("disabled", true);
    }

    if(ldap_is_ad.is(":checked")){
        $("#ldap_is_active_directory_hidden").prop("disabled", true);
    }

    if (ldap_mode.is(":checked")) {
        ldap_enable();
        $("#ldap_enable_hidden").prop("disabled", true);
    } else {
        ldap_disable();
        $("#ldap_enable_hidden").prop("disabled", false);
    }

    ldap_mode.change(function () {
        if ($(this).is(':checked')) {
            ldap_enable();
            $("#ldap_enable_hidden").prop("disabled", true);
        } else {
            ldap_disable();
            $("#ldap_enable_hidden").prop("disabled", false);
        }
    });

    ldap_is_ad.change(function(){
       if($(this).is(":checked")){
           $("#ldap_is_active_directory_hidden").prop("disabled", true);
       } else {
           $("#ldap_is_active_directory_hidden").prop("disabled", false);
       }
    });

    ldap_ssl_mode.change(function(){
       if($(this).is(":checked")){
           $("#ldap_use_ssl_hidden").prop("disabled", true);
       } else {
           $("#ldap_use_ssl_hidden").prop("disabled", false);
       }
    });

    // Bind progress buttons and simulate loading progress
    // Ladda.bind("#ldap_import_users_btn", {
    //     callback: function( instance ) {
    //         var interval = setInterval( function() {
    //             $.ajax({
    //                 type: "POST",
    //                 url: "/settings/import_users",
    //                 success: function(response){
    //                     if(response.state === 'FAILURE') {
    //                         toastr.error(response.message, 'DATABASE');
    //                         instance.stop();
    //                         clearInterval(interval);
    //                     } else if(response.state === 'SUCCESS') {
    //                         instance.stop();
    //                         clearInterval(interval);
    //                         toastr.success(response.message, 'LDAP');
    //                     } else if(response.state === 'PENDING') {
    //                         var stage = response.stage;
    //
    //                         if(stage === 1){
    //                             instance.setProgress(0.25);
    //                         } else if (stage === 2){
    //                             instance.setProgress(0.5);
    //                         } else if (stage === 3){
    //                             instance.setProgress(0.75);
    //                         } else if (stage === 4){
    //                             instance.setProgress(0.95);
    //                         }
    //                     }
    //                 },
    //                 error: function(response){
    //                     console.log(JSON.stringify(response));
    //                 }
    //             });
    //         }, 100);
    //     }
    // });
})();