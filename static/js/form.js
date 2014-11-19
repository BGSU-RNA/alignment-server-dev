$(function () {
  'use strict';

  var apdb = document.getElementById("autopdb");
  var x = [];
  var y = [];

  for ( var i = 0; i < apdb.options.length; i++ )
  {
    x[i] = apdb.options[i].value;
    if ( x[i] == "" ) continue;
    y[i] = apdb.options[i].text;
    //alert("(i: " + i + ") " + x[i] + " keys " + y[i]); // DEBUG
  }

  $("#pdbmod").change(function() {
    var pdbmod = $("#pdbmod").val();
    var arrpdbmod = pdbmod.split("|");
    var pdb = arrpdbmod[0];
    var mod = arrpdbmod[1];
    $("input[name=selected_pdb]").val(pdb);
    $("input[name=selected_mod]").val(mod);
    //alert( "pdbmod new value: " + pdbmod + "\npdb: " + pdb + "\nmod: " + mod ); // DEBUG

    // iterate change for all chain selectors
    var chainsel = [ "#autopdb", "#chain1", "#chain2", "#chain3", "#chain4", "#chain5" ];
    for ( var k = 0; k < chainsel.length; k++ ) {
      var select = $(chainsel[k]);
      
      select.empty().append('{{ null_option() }}}');

      for ( var j = 0; j < y.length; j++ ){
        if ( y[j] == "" ) continue; // default case handled above
        
        var arrx = x[j].split("|");
        
        if ( arrx[0] == pdb && arrx[1] == mod ){
          select.append('<option value="' + x[j] + '">' + y[j] + '</option>');
        }
      }
    }

    // build new options here

    show_block("jquery_test");
  });
});

function show_block(id) {
  var e = document.getElementById(id);
  if(e != null) { // prevent bugs in IE
    if(e.style.display == 'none') {
      e.style.display = 'block';
    }
  }
}
