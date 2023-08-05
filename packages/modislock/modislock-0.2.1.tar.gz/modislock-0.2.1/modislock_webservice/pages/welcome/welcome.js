"use strict";

(function() {
    var hide_time = 400;
    var show_time = 3000;

    $("#welcomeForm").children("div").steps({
        cssClass: "wizard modis-wizard-big",
        headerTag: "h3",
        bodyTag: "section",
        /* Events */
        onStepChanging: function(event, currentIndex, newIndex){
            if( currentIndex > newIndex)
                return true;

            if( newIndex === 1 && currentIndex === 0 ){
                var ser_val = $('#serial_number').val();
                var re = /^[0-9A-Z]{8,}$/g;

                if( !re.test(ser_val) ) {
                    $('#serial_message').show();
                    $('#serial_number').focus();
                    setTimeout(function(){
                        $("#serial_message").hide(hide_time);
                    }, show_time);

                    return false;
                }

                return true;
            } else if( newIndex === 2 && currentIndex === 1 ){
                var email_rule = /^[a-zA-Z0-9.!#$%&'*+\/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$/i;
                var fname = $('#first_name').val();
                var lname = $('#last_name').val();
                var email = $('#email').val();
                var pwd = $('#password').val();
                var pwd2 = $('#pwd_confirm').val();

                if( fname === '') {
                    $('#first_name_message').show();
                    setTimeout(function(){
                        $('#first_name_message').hide(hide_time);
                    }, show_time);
                    return false
                }

                if( lname === '' ) {
                    $('#last_name_message').show();
                    setTimeout(function(){
                        $('#last_name_message').hide(hide_time);
                    }, show_time);
                    return false;
                }

                if( !email_rule.test(email) ){
                    $('#email_message').show();
                    setTimeout(function(){
                        $('#email_message').hide(hide_time);
                    }, show_time);
                    return false;
                }

                if( $('.password-verdict').html() === 'Very Weak' || $('.password-verdict').html() === 'Weak' ){
                    $('#password_message').show();
                    setTimeout(function(){
                        $('#password_message').hide(hide_time);
                    }, show_time);
                    return false;
                }

                if( pwd !== pwd2 ){
                    $('#pwd_confirm_message').show();
                    setTimeout(function(){
                        $('#pwd_confirm_message').hide(hide_time);
                    }, show_time);
                    return false;
                }

                return true;
            } else if( newIndex === 3 && currentIndex === 2 ) {
                return true;
            }

        },
        onFinishing: function (event, currentIndex) {
            if( currentIndex === 3 ){
                return $('#terms_agree').prop('checked');
            }
        },
        onFinished: function (event, currentIndex) {
            $('#welcomeForm').submit();
        }
    });

    $('#password').pwstrength({
        common: {
            debug: false
        },
        rules: {},
        ui: {
            container: "#pwd-container",
            showVerdictsInsideProgressBar: true,
            showProgressBar: true,
            viewports: {
                progress: ".pwstrength_viewport_progress"
            }
        }
    });

    $(".select2-single" ).select2( {
        width: null,
        containerCssClass: ':all:',
        theme: "bootstrap"
    });

   $('#datetimepicker1').datetimepicker({
        format: 'HH:mm:ss YYYY-MM-DD',
        sideBySide: true,
        allowInputToggle: true,
        widgetPositioning: {
            horizontal: 'left',
            vertical: 'bottom'
        }
   });
})();