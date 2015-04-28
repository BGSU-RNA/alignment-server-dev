/*globals pv */

$(document).ready( function () {
  'use strict';

  var viewer = pv.Viewer(document.getElementById("viewer"), {
    width : 'auto',
    height: 'auto',
    antialias : true,
    outline : true,
    quality : 'medium',
    background : '#f2f2f2',
    animateTime: 500,
  });

  window.addEventListener('resize', function() {
    viewer.fitParent();
  });

  function asModels(raw) {
    return raw.
      split("\n").
      filter(function(line) { return !(/\dH\d/.test(line)); }).
      join("\n").
      split("ENDMDL").
      map(function(raw) { return raw + "ENDMDL\n"; });
  }

  function loadCollection() {
    var units = $("#viewer").data("units"),
        request = {
          url: "http://rna.bgsu.edu/rna3dhub/rest/getCoordinates",
          type: "post",
          data: {coord: units}
        };

    $.ajax(request).done(function(data) {
      var models = asModels(data),
          region = pv.io.pdb(models[0]),
          nearNA = pv.io.pdb(models[1]),
          nearAA = pv.io.pdb(models[2]);

      viewer.clear();
      viewer.ballsAndSticks('selected', region, {});
      viewer.ballsAndSticks('near-na', nearNA,
          {color: pv.color.uniform('grey')});
      viewer.ballsAndSticks('near-aa', nearAA,
          {color: pv.color.uniform('purple')});
      viewer.hide('near-*');
      viewer.autoZoom();

      region.eachResidue(function(residue) {
        var atom = residue.centralAtom(),
            parts = [residue.chain().name(), residue.name(), residue.num(),
                     residue.insCode()],
            config = {
              fontSize: 14,
              fontStyle: 'bold'
            };

        if (parts[3]) {
          parts.pop(3);
        }

        viewer.label("label-" + name, parts.join('|'), atom.pos(), config);
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
