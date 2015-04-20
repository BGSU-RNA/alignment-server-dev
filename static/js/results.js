var VIEWER = null;

$(document).ready( function () {
  var viewer = pv.Viewer(document.getElementById("viewer"), {
    width : 'auto',
    height: 400,
    antialias : true,
    outline : true,
    quality : 'medium',
    background : '#f2f2f2',
    animateTime: 500,
  });
  VIEWER = viewer;

  window.addEventListener('resize', function() {
    viewer.fitParent();
  });

  function loadCollection() {
    var units = $("#viewer").data("units"),
        request = {
          url: "http://rna.bgsu.edu/rna3dhub/rest/getCoordinates",
          type: "post",
          data: {coord: units}
        };

    $.ajax(request).done(function(data) {
      var structure = pv.io.pdb(data),
          labels = [];
      viewer.clear();
      viewer.ballsAndSticks('structure', structure, {});
      viewer.autoZoom();
      structure.eachResidue(function(residue) {
        var atom = residue.centralAtom(),
            name = residue.qualifiedName();
        viewer.label("label-" + name, name, atom.pos(), {fontSize: 14});
      });
    });

  }

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
    "language": {
      "searchPlaceholder": "Filter records (all fields)"
    },
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
    "language": {
      "searchPlaceholder": "Filter records (all fields)"
    },
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


  viewer.addListener('viewerReady', loadCollection);

  $("#hide-labels").click(function() {
    var target = $(this);
    if (!target.hasClass('active')) {
      viewer.hide('label-*');
      target.text("Show Labels");
    } else {
      viewer.show('label-*');
      target.text("Hide Labels");
    }
    viewer.requestRedraw();
  });

} );
