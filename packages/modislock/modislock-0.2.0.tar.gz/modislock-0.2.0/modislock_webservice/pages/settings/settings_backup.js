"use strict";

var backup_task = "";
var restore_task = "";

(function () {
    /**
     * Restore from uploaded file
     */
    $("#submit_restore").click(function (e) {
        e.preventDefault();
        var form_data = new FormData($("#restore_db_form")[0]);

        $.ajax({
            type: "POST",
            url: "/settings/restore",
            data: form_data,
            contentType: false,
            cache: false,
            processData: false,
            async: false,
            success: function (response) {
                toastr.success(response.success, "DATABASE");
                restore_task = response.task_id;
            },
            error: function (xhr, ajaxOptions, thrownError) {
                toastr.error(xhr.responseText, "DATABASE");
            }
        });
    });

    /**
     * Backup database
     */
    $("#btn_backup_db").on("click", function () {
        $.ajax({
            type: "POST",
            url: "/settings",
            data: {action: "backup"},
            success: function (response) {
                toastr.success(response.success, "BACKUP");
                backup_task = response.task_id;
            },
            error: function (xhr, ajaxOptions, thrownError) {
                toastr.error(xhr.responseText, "BACKUP");
            }
        });
    });

    // Bind progress buttons and simulate loading progress
    Ladda.bind("section.progress-backup button", {
        callback: function (instance) {
            var interval = null;
            var url = "/settings/status/" + backup_task;

            interval = setInterval(function () {
                $.ajax({
                    type: "POST",
                    url: url,
                    success: function (response) {
                        if (response.state === "FAILURE") {
                            toastr.error(response.message.message, "DATABASE");
                            instance.stop();
                            clearInterval(interval);
                        } else if (response.state === "SUCCESS") {
                            instance.stop();
                            clearInterval(interval);
                            $("#backup_message").html("");
                            window.location.href = "/settings/get_backup/" + response.message.file;
                        } else if (response.state === "PENDING") {
                            var stage = response.message.stage;

                            if (stage === 1) {
                                instance.setProgress(0.25);
                            } else if (stage === 2) {
                                instance.setProgress(0.5);
                            } else if (stage === 3) {
                                instance.setProgress(0.75);
                            } else if (stage === 4) {
                                instance.setProgress(0.95);
                            }

                            $("#backup_message").html(response.message.message);
                        }
                    },
                    error: function (xhr, ajaxOptions, thrownError) {
                        console.log(JSON.stringify(xhr.responseText));
                    }
                });
            }, 100);
        }
    });

    // Bind progress buttons and simulate loading progress
    Ladda.bind("section.progress-restore button", {
        callback: function (instance) {
            var interval = null;
            var url = "/settings/status/" + restore_task;

            interval = setInterval(function () {
                $.ajax({
                    type: "POST",
                    url: url,
                    success: function (response) {
                        if (response.state === "FAILURE") {
                            toastr.error(response.message.message, "DATABASE");
                            instance.stop();
                            clearInterval(interval);
                        } else if (response.state === "SUCCESS") {
                            instance.stop();
                            clearInterval(interval);
                            $("#restore_message").html("");
                            toastr.success(response.message.message, "DATABASE");
                        } else if (response.state === "PENDING") {
                            var stage = response.message.stage;

                            if (stage === 1) {
                                instance.setProgress(0.25);
                            } else if (stage === 2) {
                                instance.setProgress(0.5);
                            } else if (stage === 3) {
                                instance.setProgress(0.75);
                            } else if (stage === 4) {
                                instance.setProgress(0.95);
                            }

                            $("#restore_message").html(response.message.message);
                        }
                    },
                    error: function (xhr, ajaxOptions, thrownError) {
                        console.log(xhr.responseText);
                    }
                });
            }, 100);
        }
    });
})();
