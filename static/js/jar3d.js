$(window).load(function() {
  'use strict';

  function formatRequest(sequences, counts, percent) {
    var headers = [];
    counts.forEach(function(c) { headers.push('Count: ' + c); });
    percent.forEach(function(p) { headers.push('Percent: ' + p); });
    headers = headers.map(function(h) { h.join(' ') });

    var fasta = sequences.map(function(s, i) {
      return headers[i] + '\n' + s;
    }).join("\n");

    return {
      valid: true,
      query_type: "isFastaMultipleLoops",
      fasta: headers,
      data: sequences,
      ss: null,
      parsed_input: fasta
    }
  }

  function showMessage(data) {
    console.log(data);
  }

  function invalidPart(sequence) {
      var chars = sequence.split('')
      // Check that sequence is only valid characters
      return sequence.search(/[^ACGU-]/i) !== -1 &&
        // Check that it does not end in gaps
        chars[0] === '-' || chars[chars.length - 1] === '-' &&
        // Check that the sequence is not all gaps between flanking
        (sequence.length === 3 ? p.search(/^[^-].*[^-]$/) !== -1 : p.search(/^[^-].*[^-].*[^-]$/) !== -1)
      ;
  }

  function validSequence(sequence) {
    var parts = sequence.split('*')
    if (parts.length > 2) {
      return false;
    }

    var invalid = parts.filter(invalidPart)
    return invalid.length !== 0
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
