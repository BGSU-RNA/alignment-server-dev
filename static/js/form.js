$( window ).load(function() {
  'use strict';

  function unitId(unit) {
    if (!unit.number) {
      return null;
    }
    var parts = [unit.pdb, unit.model, unit.chain, unit.unit, unit.number];
    if (unit.insertion_code !== '') {
      parts.push('', '', unit.insertion_code);
    }
    return parts.join('|');
  }

  function unitRange(range) {
    return range.map(unitId).filter(function(a) { return a; }).join(':');
  }

  function collection(ranges) {
    return ranges.map(unitRange).join(',');
  }

  function showError(element, msg) {
    var group = element.parents().first();
    group.addClass('has-error');

    $("#problems").show();
    $("#problems .message[data-message-id='" + msg + "']").show();
  }

  function validateUnit(unit) {
    if (!unit.hasOwnProperty('number')) {
      showError(unit.element, 1);
      return false;
    }

    if (unit.number < 0) {
      showError(unit.element, 1);
      return false;
    }

    return true;
  }

  // Validate range has side effects. It may display error messages on the
  // page as well as determing if the range is valid.
  function validateRange(range) {
    // A range may only have one entry in it. In this case the range is still
    // valid if the single unit is valid. The single unit may be either start or
    // stop.
    var filtered = range.filter(function(unit) { return unit.position; });

    // If we have nothing we can just cal validateUnit as it will complain about
    // missing data.
    if (filtered.length === 0) {
      range.filter(validateUnit);
      return false;
    }

    // Otherwise we use the filtered set as the ranges
    range = filtered;

    var valid = range.filter(validateUnit);
    if (valid.length !== range.length) {
      return false;
    }

    if (range.length === 2) {
      if (range[0].number > range[1].number) {
        showError(range[0].element, 2);
        showError(range[1].element, 2);
        return false;
      } else if (range[0].number === range[1].number) {
        if (range[0].insertion_code > range[1].insertion_code) {
          showError(range[0].element, 2);
          showError(range[1].element, 2);
          return false;
        }
      }

      if (range[1].number - range[0].number > 50) {
        showError(range[0].element, 3);
        showError(range[1].element, 3);
        return false;
      }
    }

    return true;
  }

  function validateRanges() {
    var ranges = [],
        $pdb = $("#pdb-model option:selected"),
        pdb = $pdb.data('pdb'),
        model = $pdb.data('model');

    var count = parseInt($("#range-control-group").data("range-count"));
    for(var i = 0; i < count; i++) {
      ranges.push([{pdb: pdb, model: model, unit: '', point: 'start'},
                  {pdb: pdb, model: model, unit: '', point: 'stop'}]);
    }

    // Pull out all range data
    function setValue(selector, name, pos) {
      $(selector).each(function(_, elem) {
        var $elem = $(elem),
            index = parseInt($elem.data('range'));
        pos.forEach(function(p) {
          ranges[index][p].element = $elem;
          ranges[index][p][name] = $elem.val();
        });
      });
    }

    setValue(".chain-selector option:selected", 'chain', [0, 1]);
    setValue(".start-selector", 'position', [0]);
    setValue(".stop-selector", 'position', [1]);

    // Parse out the number and insertion code from position
    ranges = ranges.map(function(range) {
      return range.map(function(unit) {
        var number_pattern = /^(\d+)\|?([a-z]*)$/i,
            matches = number_pattern.exec(unit.position);

        if (matches !== null && matches.length !== 0) {
          unit.number = parseInt(matches[1]);
          unit.insertion_code = matches[2];
        }

        return unit;
      });
    });

    // Filter ranges to only those that have entries
    ranges = ranges.filter(function(range) {
      if (range[0].element.is(':hidden')) {
        return false;
      }

      var filled = range.filter(function(position) {
        return position.hasOwnProperty('chain') ||
          position.hasOwnProperty('position');
      });
      return filled.length !== 0;
    });

    if (ranges.length === 0) {
      // TODO: Show error message for no ranges
      return;
    }

    // Validate all ranges
    var valid = ranges.filter(validateRange);

    return {ranges: valid, success: ranges.length === valid.length};
  }

  function rangeDiv(btn) {
    return $(btn).parents(".range-control-group");
  }

  function addRangeControl(event) {
    var $parent = rangeDiv(event.target),
        $next = $parent.nextAll(".range-control-group:hidden").first();

    clearErrors();
    if (validateRanges().success) {
      $next.show();
    }
  }

  function removeRangeControl(event) {
    var $parent = rangeDiv(event.target);
    clearRange($parent);
    return $parent.hide();
  }

  function clearErrors() {
    $('div').removeClass('has-error');
    $("#problems").hide();
    $("#problems").children().hide();
  }

  function clearRange(selector) {
    $(selector).find("input").val("");
    $(selector).find(":selected").removeAttr("selected");
    $(selector).find(".alert").hide();
    $(selector).find('div').removeClass('has-error');
  }

  function showFormError(selector, message) {
    alert(selector, message);
  }

  $("#submit-ranges").click(function(event){
    event.preventDefault();
    clearErrors();

    var submit = validateRanges();

    if (submit.success) {
      window.location.search = '?units=' + collection(submit.ranges);
    }
  });

  $("#pdb-model").change(function() {
    $('.range-control-header').show();
    clearRange(".range-control-group");
    clearErrors();
    $(".range-control-group").hide();
    $(".range-control-group").first().show();

    $(".alignment-control").hide();
    $(".alignment").removeAttr('checked');

    var pdb = $("#pdb-model option:selected").data("pdb"),
        selector = ".alignment-control[data-pdb='" + pdb + "']",
        $divs = $(selector),
        $radios = $divs.find('.alignment-radio');

    $divs.show();
    $radios.first().click();
  });

  $(".alignment").click(function(event) {
    var $target = $(event.target),
        $radio = ($target.is("label") ? $target : $target.parents("label")),
        chains = $radio.data('chains').split(',');
    clearRange(".range-control-group");
    clearErrors();

    $(".chain-selector").empty();
    chains.forEach(function(chain, index) {
      var selected = (index === 0 ? 'selected': ''),
          option = '<option value="' + chain + '" ' + selected +
            ' data-range="' + index + '">' + chain + "</option>";
      $(".chain-selector").append(option);
    });
  });

  $(".add-range").on('click', addRangeControl);
  $(".remove-range").on('click', removeRangeControl);

  $("#clear-button").click(function() {
    clearRange(".range-control-group");
    clearErrors();
  });

});
