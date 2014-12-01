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

  $("#pdb-model").change(function() {
    $('.range-control-header').show();
    clearRange(".range-control-group");
    $(".range-control-group").hide();
    $(".range-control-group").first().show();
  });

  $(".add-range").on('click', addRangeControl);
  $(".remove-range").on('click', removeRangeControl);

});
