$(document).ready( function () {
  $('#sequence_summary').DataTable( {
    "ordering": true,
    "paging": true,
    "order": [[1, "desc"]]
  } );

  $('#sequence_details').DataTable( {
    "columnDefs": [
      {
        "targets": [5],
        "visible": false,
        "searchable": true
      }
    ],
    "dom": '<"wrapper"<CTfi><t><lrp><"clear">>',
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
      "sSwfPath": "../swf/copy_csv_xls_pdf.swf"
    },
    "ordering": true,
    "paging": false,
    "scrollY": "600px",
    "order": [[0, "asc"]]
  });
} );
