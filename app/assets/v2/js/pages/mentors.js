var mentors = (function() {

  var pageIdx = 1;
  var pageSize = 10;

  var init = function() {
    $('#save_search, #search_sort').hide();
    var chekcbox_filter_tmpl = $.templates('#mentor_checkbox_filter');

    var organization_filters = [
      {
        id: 'gitcoin_filter',
        value: 'Gitcoin'
      },
      {
        id: 'diligence_filter',
        value: 'Diligence'
      },
      {
        id: 'ultradark_filter',
        value: 'UltraDark'
      },
      {
        id: 'truffle_filter',
        value: 'Truffle'
      },
      {
        id: 'digital_lizard_printing_filter',
        value: 'Digital Lizard Printing'
      }
    ];

    organization_filters.forEach((filter) => {
      var html = chekcbox_filter_tmpl.render(filter);

      $('#mentors_organization_filters').append(html);
    });

    var experience_filters = [
      {
        id: '1_5',
        value: '1 - 5'
      },
      {
        id: '5_10',
        value: '5 - 10'
      },
      {
        id: '10_15',
        value: '10 - 15'
      },
      {
        id: '15_20',
        value: '15 - 20'
      },
      {
        id: '20_',
        value: '20+'
      }
    ];

    experience_filters.forEach((filter) => {
      var html = chekcbox_filter_tmpl.render(filter);

      $('#mentors_experience_filters').append(html);
    });

    var skills_filters = [
      {
        id: 'python',
        value: 'Python'
      },
      {
        id: 'haskell',
        value: 'Haskell'
      },
      {
        id: 'solidity',
        value: 'Solidity'
      },
      {
        id: 'docker',
        value: 'Docker'
      },
      {
        id: 'machine_learning',
        value: 'Machine Learning'
      }
    ];

    skills_filters.forEach((filter) => {
      var html = chekcbox_filter_tmpl.render(filter);

      $('#mentors_skills_filters').append(html);
    });
  };

  fetchMentors(1, pageSize);

  $('#load_more').click(function() {
    fetchMentors(++pageIdx, pageSize);
  });

  function fetchMentors(page, size) {
    $.get('fetch', { page, size }, (result) => {
      var mentor_tmpl = $.templates('#mentor');

      result.mentors.forEach((mentor) => {
        var html = mentor_tmpl.render(mentor);

        $('#mentor_search_results').append(html);
        $('#open_mentor_' + mentor.id).click(function() {
          window.location = '' + mentor.id + '/profile';
        });
      });
      if (result.total_pages > pageIdx) {
        $('#load_more').removeClass('invisible');
      } else {
        $('#load_more').hide();
      }
    });
  }
  $(document).ready(init);
}());

