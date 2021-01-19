/**
 * @notice Vue component for ingesting contributions that were missed during checkout
 * @dev See more at: https://github.com/gitcoinco/web/issues/7744
 */

let appIngestContributions;

Vue.component('grants-ingest-contributions', {
  delimiters: [ '[[', ']]' ],

  data: function() {
    return {};
  }
});

if (document.getElementById('gc-grants-ingest-contributions')) {

  appIngestContributions = new Vue({
    delimiters: [ '[[', ']]' ],
    el: '#gc-grants-ingest-contributions'
  });
}
