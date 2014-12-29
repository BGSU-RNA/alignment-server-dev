$(document).ready( function () {
  $.extend( $.fn.dataTable.defaults, {
    language: {
      search: "Filter:"
    },
    "ordering": true,
    "paging": true,
    "scrollY": "600px"
  } );

  $('#sequence_summary').DataTable( {
    "dom": '<"wrapper"<flip><t><lirp><"clear">>',
    "lengthMenu": [[25, 50, 100, -1], [25, 50, 100, "All"]],
    "order": [[1, "desc"]]
  } );

  $('#sequence_details').DataTable( {
/*
    "columnDefs": [
      {
        "targets": [5],
        "visible": false,
        "searchable": true
      }
    ],
*/
/*
    //T = TableTools (copy/print/save)
    "dom": '<"wrapper"<CTflip><t><lirp><"clear">>',
*/
    "dom": '<"wrapper"<Cflip><t><lirp><"clear">>',
    "lengthMenu": [[25, 50, 100, 200, -1], [25, 50, 100, 200, "All"]],
/*
    "oTableTools": {
      "aButtons": [
        "copy",
        "print",
        {
          "sExtends": "collection",
          "sButtonText": "Save",
          "aButtons": [ "csv", "xls", "pdf" ]

        }
      ],
      "sSwfPath": "/static/swf/copy_csv_xls_pdf.swf"
    },
*/
    "order": [[0, "asc"]]
  });
} );
