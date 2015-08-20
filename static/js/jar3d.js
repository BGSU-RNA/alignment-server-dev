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
    var parts = sequence.split(',')

    // A sequence is valid if it is only composed of A, C, G, U, N or -
    if (sequence.search(/[^ACGUN-]/)) {
      return false;
    }

    // A sequence is valid if each part does not start or end with -
    var flanking_gaps = parts.filter(function(p) {
      var chars = p.split('')
      return chars[0] === '-' || chars[chars.length - 1] === '-'
    });

    if (flanking_gaps.length === 0) {
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
    return $(parent)
      .select('.sequence')
      .contents()
      .map(function(str) { return str.toUpperCase(); })
      .filter(validSequence);
  }

  $(".jar3d-all").on('click', function(event) {
    var sequences = getAllChildSequences("#sequence_summary");
    if (sequences.length == 0) {
      showMessage({valid: false, msg: "No valid sequences found"});
    }

    $.ajax({
      type: 'POST',
      url: 'https://rna.bgsu.edu/jar3d',
      contentType: 'application/json; charset=utf8',
      traditional: false,
      data: formatRequest(sequences),
    }).done(function(data) {
      if (data.redirect) {
        window.location.href = data.redirect;
      } else if (data.error) {
        console.log(data.error);
        showMessage({valid: false, msg: data.error});
      } else {
        showMessage({valid: false, msg: "Unknown Error occurred"});
      }
    });
  });

});
