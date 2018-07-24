/* eslint-disable no-invalid-this */
var technologies = [
  '.NET', 'ASP .NET', 'Angular', 'Backbone', 'Bootstrap', 'C', 'C#', 'C++', 'CSS', 'CSS3',
  'CoffeeScript', 'Dart', 'Django', 'Drupal', 'DynamoDB', 'ElasticSearch', 'Ember', 'Erlang', 'Express', 'Go', 'Groovy',
  'Grunt', 'HTML', 'Hadoop', 'Jasmine', 'Java', 'JavaScript', 'Jekyll', 'Knockout', 'LaTeX', 'Mocha', 'MongoDB',
  'MySQL', 'NoSQL', 'Node.js', 'Objective-C', 'Oracle', 'PHP', 'Perl', 'Polymer', 'Postgres', 'Python', 'R', 'Rails',
  'React', 'Redis', 'Redux', 'Ruby', 'SASS', 'Scala', 'Sqlite', 'Swift', 'TypeScript', 'Websockets', 'WordPress', 'jQuery'
];

var removeFilter = function() {
  document.location.href = '/leaderboard';
};

$(document).ready(function() {
  var keyword_search = document.location.href.split('=');

  if (keyword_search.length > 1) {
    $('.filter-tags').append('<a class="filter-tag tech_stack"><span>' + keyword_search[1] + '</span>' +
      '<i class="fas fa-times" onclick="removeFilter()"></i></a>');
  }

  $('.leaderboard_entry .progress-bar').each(function() {
    const max = parseInt($(this).attr('aria-valuemax'));
    const now = parseInt($(this).attr('aria-valuenow'));
    const width = (now * 100) / max;

    $(this).css('width', `${width}%`);
  });

  $('.clickable-row').click(function(e) {
    if (typeof $(this).data('href') == 'undefined') {
      return;
    }
    window.location = $(this).data('href');
    e.preventDefault();
  });

  $('#key').change(function() {
    const val = $(this).val();

    document.location.href = `/leaderboard/${val}`;
  });

  $('#new_search').click(function(e) {
    var keyword = $('#keywords').val();

    if (!technologies.includes(keyword)) {
      confirm('Please enter a valid technology.');
      return;
    }

    window.location.href = `/leaderboard?keyword=${keyword}`;
  });
});
