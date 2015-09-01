$(window).load(function() {
  'use strict';

  function formatRequest(sequences) {
    var fasta = sequences.join('\n');
    var headers = [];
    var request = {
      valid: true,
      query_type: "isNoFastaMultipleLoops",
      fasta: headers,
      data: sequences,
      ss: null,
      parsed_input: fasta
    }
  }

  function showMessage(data) {
    console.log(data);
  }

  function validSequence(sequence) {
    var parts = sequence.split('*')

    // A sequence is valid if it is only composed of A, C, G, U or -
    var bad_parts = parts.filter(function(p) {
      return sequence.search(/[^ACGU-]/i) !== -1;
    });
    if (bad_parts.length !== 0) {
      return false;
    }

    // A sequence is valid if each part does not start or end with -
    var flanking_gaps = parts.filter(function(p) {
      var chars = p.split('')
      return chars[0] === '-' || chars[chars.length - 1] === '-'
    });

    if (flanking_gaps.length !== 0) {
      return false;
    }

    // A sequence is valid if each part has at least 1 internal sequence if it
    // is long enough and each part does not start or end with '*'.
      var long_enough = parts.filter(function(p) {
      if (p.length === 3) {
        return p.search(/^[^-].*[^-]$/) !== -1
      }

        return p.search(/^[^-].*[^-].*[^-]$/) !== -1
    });

    if (long_enough.length === 0) {
      return false;
    }

    return true;
  }

  function getAllChildSequences(parent) {
    var sequences = []
    $(parent)
      .find('.sequence')
      .each(function() {
        sequences.push($(this).text());
      });

    return sequences.filter(validSequence);
  }

  $(".jar3d-all").on('click', function(event) {
    var sequences = getAllChildSequences("#sequence_summary");
    if (sequences.length == 0) {
      return showMessage({valid: false, msg: "No valid sequences found"});
    }

    var url = 'http://' + window.location.host + '/jar3d/process_input';

    $.ajax({
      type: 'POST',
      url: url,
      contentType: 'application/json; charset=utf8',
      traditional: false,
      data: formatRequest(sequences),
    }).done(function(raw) {
      var d = JSON.parse(raw)
      if (d.redirect) {
        window.location.href = d.redirect;
      } else if (d.error) {
        showMessage({valid: false, msg: data.error});
      } else {
        showMessage({valid: false, msg: "Unknown Error occurred"});
      }
    });
  });

});
