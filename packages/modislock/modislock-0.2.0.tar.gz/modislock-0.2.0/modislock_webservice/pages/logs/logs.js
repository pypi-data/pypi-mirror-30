"use strict";

/**
 * Created by richard on 03.02.17.
 */

// Timeline data
var items = new vis.DataSet();
var start_time = moment();
var end_time = moment().add(1, 'hours');


(function() {
    var timeline = new vis.Timeline($('#timeline_visualization')[0],
        items, {
            start: moment().subtract(4, 'hours'), // Start date of display
            end: end_time,                        // End date of display
            type: 'box',                          // Style of each item displayed
            showCurrentTime: true,                // Shows a red line that represents the current time
            height: '600px',
            width: '100%',
            orientation: 'both',                  // Time orientation top, bottom, none, both
            clickToUse: false,                    // Requires a click to use
            max: moment().add(1, 'hours'),        // Max date the timeline can go to
            min: moment().subtract(4, 'months'),  // Min date the timeline can scroll to
            zoomMax: 60000 * 60 * 24 * 5,         // Max zoom out date, in milliseconds
            zoomMin: 60000 * 60                   // Min zoom in date, in milliseconds
        }).on('select', function(event){
            // Zoom is not working
            this.zoomIn(1, {
                animation: true
            });
            // Centers on the selected item
            this.focus(event.items[0], {
                animation: true
            });
        }).on('rangechange', function(event){
            var daterange = $('#report_range').data('daterangepicker');

            daterange.setStartDate(event.start);
            daterange.setEndDate(event.end);

            $('#report_range span').html(moment(event.start).format('MMMM D, hh:mm A') + ' - ' + moment(event.end).format('MMMM D, hh:mm A'));
        });

    // Date rangepicker from generator
    $('#report_range').daterangepicker({
        timePicker: true,
        timePickerIncrement: 15,
        locale: {
            format: 'MMMM D h:mm A'
        },
        ranges: {
            "Today": [moment().startOf('day'), moment().endOf('day')],
            "Yesterday": [moment().subtract(1,'days').startOf('day'), moment().subtract(1, 'days').endOf('day')],
            "Last 7 Days": [moment().subtract(7,'days').startOf('day'), moment().endOf('day')],
            "Last 30 Days": [moment().subtract(30,'days').startOf('day'), moment().endOf('day')],
            "This Month": [moment().startOf('month').startOf('day'), moment().endOf('month').endOf('day')],
            "Last Month": [moment().subtract(1, 'month').startOf('month').startOf('day'), moment().subtract(1, 'month').endOf('month').endOf('day')]
        },
        showCustomRangeLabel: false,
        startDate: start_time,
        endDate: end_time,
        opens: 'center',
        drops: 'down'
    }).on('apply.daterangepicker', function(event, picker){
        timeline.setWindow(picker.startDate, picker.endDate);
        // update_timeline($('#user_select').val(), picker.startDate, picker.endDate, $('#event').prop('value'));
    });

    // Date Range display
    $('#report_range span').html(start_time.format('MMMM D, hh:mm A') + ' - ' + end_time.format('MMMM D, hh:mm A'));

    // Selection of users
    $("#user_select").select2({
        theme: "bootstrap",
        placeholder: "Select a User",
        containerCssClass: ':all:'
    }).on('select2:select', function(event) {
        // var range = $('#report_range').data('daterangepicker');
        update_timeline(parseInt($('#user_select').val()), start_time, moment(), $('#event').prop('value'));
    });

    $('#radioBtn a').on('click', function(){
        var sel = $(this).data('title');
        var tog = $(this).data('toggle');
        var range = $('#report_range').data('daterangepicker');
        $('#'+tog).prop('value', sel);

        $('a[data-toggle="'+tog+'"]').not('[data-title="'+sel+'"]').removeClass('active').addClass('notActive');
        $('a[data-toggle="'+tog+'"][data-title="'+sel+'"]').removeClass('notActive').addClass('active');
        update_timeline(parseInt($('#user_select').val()), start_time, moment(), sel);
    });
})();


function init_timeline_data(preserved_time){
    start_time = moment().subtract(preserved_time, 'months');
    update_timeline(0, start_time, moment(), 'A');
}

/**
 * @brief Updates the timeline with ajax request
 * @param user User id selected from menu, 0 for all
 * @param start Start of time when the begin event search
 * @param end End of time when to finish event search
 * @param event_type Type of event 'D' for Denied 'A' for Approved 'B' Both
 */
function update_timeline(user, start, end, event_type){
    var url = '/logs/events/' + user +
        '?start_time=' + start.format('YYYY-MM-DD HH:mm:ss') +
        '&end_time=' + end.format('YYYY-MM-DD HH:mm:ss') +
        '&event_type=' + event_type;
    $.ajax({
        url: url,
        success: function(response){
            items.clear();
            items.add(response);
        },
        error: function(response){
            console.log('Error ' + response);
        }
    });
}
