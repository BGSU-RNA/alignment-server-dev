$( window ).load(function() {
  'use strict';

  function rangeDiv(btn) {
    return $(btn).parents(".range-control-group");
  }

  function addRangeControl() {
    var $parent = rangeDiv(event.target),
        $next = $parent.nextAll(".range-control-group:hidden").first();
    $next.show();
  }

  function removeRangeControl() {
    var $parent = rangeDiv(event.target);
    clearRange($parent);
    return $parent.hide();
  }

  function clearRange(selector) {
    $(selector).find("input").val("");
    $(selector).find(":selected").removeAttr("selected");
  }

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

        var cvalue = $(c).val();
        var bvalue = ( jQuery.trim($(b).val()).length == 0 ) ? 0 : $(b).val();
        var evalue = ( jQuery.trim($(e).val()).length == 0 ) ? 0 : $(e).val();
        //  jQuery.trim in two lines directly above to eliminate whitespace

        //  WORKING ABOVE THIS COMMENT

        var bi = 0;
        var bc = "";
        var ei = 0;
        var ec = "";

        //
        //  If the input value is already an integer, pass it through;
        //  otherwise, split the string on '|', set the integer value, and
        //  hold onto the string portion.
        //
        //  bi and ei can be used for numeric tests now.
        //

        if ( +bvalue === parseInt(bvalue) ){
          bi = bvalue;
        } else {
          var barray = bvalue.split('|');
          bi = parseInt(barray[0]);
          bc = barray[1];
        }

        if ( +evalue === parseInt(evalue) ){
          ei = evalue;
        } else {
          var earray = evalue.split('|');
          ei = parseInt(earray[0]);
          ec = earray[1];
        }

        alert("bi: " + bi + "\nei: " + ei ); // DEBUG

        //
        //  This block needs more work.  Won't properly handle insertion codes
        //  as written.  The fourth element of the conditional is failing (the
        //  other four parts work together correctly), not sure why.
        //
        //  Blake has code that can test this, but only after submission.  When
        //  is the best time to test these conditions?
        //
        //  Still TO DO:  get this to the point where it will submit the form
        //  with only the units argument, and not the individual form element
        //  values (which is what it's doing now, if I weren't either
        //  suppressing the submit behavior or making syntax errors that allow
        //  the code to pass that statement).
        //
        //  FOR NOW:  only validate that nonzero inputs were assigned.
        //
        if (
                ( 0 < bi )
            &&  ( 0 < ei )
            &&  ( cvalue != "" )
            //&&  ( bi <= ei )          // PROBLEM IS HERE
            //&&  ( ev <= ( bv + 50 ) ) // PROBLEM IS HERE
          ) {
          range[i] = true; // debugging variable

          if ( units ) {
            units += ",";
          }

          var bout = ( bc == "" ) ? bi : bi + "|||" + bc;
          var eout = ( ec == "" ) ? ei : ei + "|||" + ec;

          units += cvalue + "|A|" + bout;

          if ( bout != eout ) {
            units += ":" + cvalue + "|A|" + eout;
          }
          //
          //  Manual testing shows that strings produced by this string
          //  builder do produce output without errors.
          //
        }

        alert("Range " + i + " validates " + range[i] + "\nChain: " + cvalue + "\nStart: " + bout + "\nStop: " + eout); // DEBUG

        if ( range[i] == false ) {
          break;
        }
      }

      //
      //  Build units from form elements; submit via window.location.
      //
      var http_str = jQuery.param({units: units});
      //window.location = "?" + http_str;

      //  WORKING BELOW THIS COMMENT

      var alert_str = ( units ) ? "units is set to: " + units : "units not set!";

      alert(alert_str); // DEBUG

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

  $("#pdb-model").change(function() {
    $('.range-control-header').show();
    clearRange(".range-control-group");
    $(".range-control-group").hide();
    $(".range-control-group").first().show();
  });

  $(".add-range").on('click', addRangeControl);
  $(".remove-range").on('click', removeRangeControl);

});
