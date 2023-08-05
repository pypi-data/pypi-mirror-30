"use strict";


(function(){
   $('#event_table').DataTable({
       // dom: '<"html5buttons"B>lTfgitp',
       dom: 'tp',
       pageLength: 5,
       lengthChange: true,
       responsive: true,
       order: [[ 2, "desc"]],
       ajax: {
           url: "/events",
           method: 'POST',
           data: {
               action: 'request'
           }
       },
       columnDefs: [
           {
               targets: [0],
               render: function(data, type, row){
                   return data.first_name + ' ' + data.last_name;
               }
           },
           {
               targets: [ 2 ],
               // 2017-01-09T12:29:12+00:00
               render: function( data, type, row ) {
                   return moment(data).format('YYYY-MM-DD HH:mm:ss');
               }
           },
           {
               targets: [1, 3, 4],
               orderable: false
           }
       ],
       columns: [
           {data: null},
           {data: 'event_type'},
           {data: 'event_time'},
           {data: 'location'},
           {data: 'location_direction'}
        ]
   });
})();