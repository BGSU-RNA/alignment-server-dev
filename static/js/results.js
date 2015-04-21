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
      var parts = data.split("ENDMDL").map(function(m) { return m + "ENDMDL\n"; }),
          region = pv.io.pdb(parts[0]),
          nearNA = pv.io.pdb(parts[1]),
          nearAA = pv.io.pdb(parts[2]);

      viewer.clear();
      viewer.ballsAndSticks('selected', region, {});
      viewer.ballsAndSticks('near-na', nearNA, {color: pv.color.uniform('grey')});
      viewer.ballsAndSticks('near-aa', nearAA, {color: pv.color.uniform('purple')});
      viewer.hide('near-*');
      viewer.autoZoom();

      region.eachResidue(function(residue) {
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

  $("#toggle-labels").click(function() {
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

  $("#toggle-neighborhood").click(function() {
    var target = $(this);
    if (target.hasClass('active')) {
      viewer.hide('near-*');
      target.text("Show Neighborhood");
    } else {
      viewer.show('near-*');
      target.text("Hide Neighborhood");
    }
    viewer.requestRedraw();
  });

} );
