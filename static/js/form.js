//$( document ).ready(function () {
$( window ).load(function() {
  'use strict';

  var apdb = document.getElementById("pdb-chain");
  var x = [];
  var y = [];

  for ( var i = 0; i < apdb.options.length; i++ )
  {
    x[i] = apdb.options[i].value;
    if ( x[i] == "" ) continue;
    y[i] = apdb.options[i].text;
    //alert("(i: " + i + ") " + x[i] + " keys " + y[i]); // DEBUG
  }

  $("#pdb-model").change(function()
  {
    var pdbmod = $("#pdb-model").val();
    var arrpdbmod = pdbmod.split("|");
    var pdb = arrpdbmod[0];
    var mod = arrpdbmod[1];
    $("input[name=selected_pdb]").val(pdb);
    $("input[name=selected_mod]").val(mod);
    //alert( "pdbmod new value: " + pdbmod + "\npdb: " + pdb + "\nmod: " + mod ); // DEBUG

    // iterate change for all chain selectors
    var chainsel = [ "#pdb-chain", "#chain1", "#chain2", "#chain3", "#chain4", "#chain5" ];
    for ( var k = 0; k < chainsel.length; k++ )
    {
      var select = $(chainsel[k]);

      //select.disabled = false;
      select.empty().append('{{ null_option() }}}');

      for ( var j = 0; j < y.length; j++ )
      {
        if ( y[j] == "" ) continue; // default case handled above

        var arrx = x[j].split("|");

        if ( arrx[0] == pdb && arrx[1] == mod )
        {
          select.append('<option value="' + x[j] + '">' + y[j] + '</option>');
        }
      }
    }
  });

  $("#alnsrv").submit(function(event){
    var units = "";


    if ( $("#pdb-model option:selected").val() == "" ){
      //  NULL if no selection made, otherwise value
      alert("Structure not selected!");
      event.preventDefault();
    } else {
      var range = [];
      for ( var i = 1; i <= 5; i++ ){
        range[i] = false;

        var c = "#chain" + i;
        var b = "#beg" + i;
        var e = "#end" + i;

        var cv = $(c).val();
        var bv = ( jQuery.trim($(b).val()).length == 0 ) ? 0 : $(b).val();
        var ev = ( jQuery.trim($(e).val()).length == 0 ) ? 0 : $(e).val();
        //  jQuery.trim in two lines directly above to eliminate whitespace

        //  WORKING ABOVE THIS COMMENT

        //
        //  This block needs more work.  Won't properly handle insertion codes
        //  as written.  The fourth element of the conditional is failing (the
        //  other four parts work together correctly), not sure why.
        //
        //  Blake has code that can test this, but only after submission.  When
        //  is the best time to test these conditions?
        //
        //  Split both bv and ev on the '|' character, so then we can cast the
        //  numerical part of the value to int and range-test it, then
        //  recombine.
        //
        //  Still TO DO:  get this to the point where it will submit the form
        //  with only the units argument, and not the individual form element
        //  values (which is what it's doing now, if I weren't either
        //  suppressing the submit behavior or making syntax errors that allow
        //  the code to pass that statement).
        //

        //
        //  FOR NOW:  only validate that nonzero inputs were assigned.
        //
        if (
                ( 0 < bv )
            //&&  ( bv <= ev )
            &&  ( 0 < ev )
            //&&  ( ev <= ( bv + 50 ) ) // PROBLEM IS HERE
            &&  ( cv != "" )
          ) {
          range[i] = true; // debugging variable

          if ( units ) {
            units += ",";
          }

          units += cv + "|A|" + bv + ":" + cv + "|A|" + ev;
          //
          //  Manual testing shows that strings produced by this string
          //  builder do produce output without errors.
          //
        }

        alert("Range " + i + " validates " + range[i] + "\nChain: " + cv + "\nStart: " + bv + "\nStop: " + ev);
      }

      //
      //  Our case is simpler:  build units from the various form elements and
      //  submit that via window.location.
      //
      var http_str = jQuery.param({units: units});
      //window.location = "?" + http_str;

      //  WORKING BELOW THIS COMMENT

      alert("Help!");
      alert("units is set to: " + units);

      event.preventDefault();

      $("input:submit").attr({
        //  do this only after validation is complete, so the user can fix any
        //  errors and still submit the form
        disabled: "true"
        , value: "Submitting..."
        , style: "color:#ab8b8b; text-shadow: 0px 0px 0px; background-color: #dddddd;"
        // replace with appropriate Bootstrap styles
      });
    }
  });
});
