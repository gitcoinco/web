var mentors = (function() {

  var pageIdx = 1;
  var pageSize = 10;

  var init = function() {
    $('#save_search, #search_sort').hide();
    var chekcbox_filter_tmpl = $.templates('#mentor_checkbox_filter');

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

    function debounce(func, wait, immediate) {
      var timeout;

      return function() {
        var context = this;
        var args = arguments;
        var later = function() {
          timeout = null;
          if (!immediate)
            func.apply(context, args);
        };
        var callNow = immediate && !timeout;

        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
        if (callNow)
          func.apply(context, args);
      };
    }

    $('#keywords').keyup(debounce(function() {
      $('#mentor_search_results').html('');
      fetchMentors(1, 10);
    }, 500));

    $('#load_more').on('click', function() {
      fetchMentors(++pageIdx, pageSize);
    });
    console.log($('.mentor_checkbox_filter'));
    $('.mentor_checkbox_filter').change(function() {
      $('#mentor_search_results').html('');
      fetchMentors(1, 10);
    });
  };

  fetchMentors(1, pageSize);

  function fetchMentors(page, size) {
    var term = $('#keywords').val();

    var exp = $('.mentor_checkbox_filter:checked').map(function() {
      return this.id;
    }).get().join(',');

    $.get('fetch', { page, size, term, exp }, (result) => {
      var mentor_tmpl = $.templates('#mentor');

      result.mentors.forEach((mentor) => {
        var html = mentor_tmpl.render(mentor);

        $('#mentor_search_results').append(html);
        $('#open_mentor_' + mentor.id).click(function() {
          window.location = '' + mentor.id;
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

