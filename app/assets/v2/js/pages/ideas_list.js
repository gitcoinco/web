(function() {
  var pageIdx = 1;
  var pageSize = 2;

  $('document').ready(() => {
    initialIdeasLoad();
    $('#load_more').click(onLoadMoreClick);
    $('#add').click(onAddClick);
    $('#sort_ideas').change(onSortChange);
  });

  function onLoadMoreClick() {
    var listSize = $(this).data('list-size');

    loadMoreIdeas();
  }

  function onAddClick() {
    window.location = 'new';
  }

  function onIdeaClick(data) {
    var ideaId = $(data.currentTarget).data('ideaId');

    window.location = 'idea/' + ideaId + '/show';
  }

  function onSortChange(data) {
    console.log('sort change');
  }

  function initialIdeasLoad(sort) {
    fetchIdeas(1, pageSize, (result) => {
      var ideas = result.ideas;
      var html;

      if (ideas.length > 0) {
        html = getIdeasHtml(ideas);
      } else {
        html = 'No ideas';
      }
      $('#ideas').html(html);
      toggleLoadMore(pageIdx, result.total_pages);
      initIdeasOpenHandlers(ideas);
    });
  }

  function loadMoreIdeas() {
    fetchIdeas(++pageIdx, pageSize, (result) => {
      var ideas = result.ideas;

      if (ideas.length > 0) {
        $('#ideas').append(getIdeasHtml(ideas));
      }
      toggleLoadMore(pageIdx, result.total_pages);
      initIdeasOpenHandlers(ideas);
    });
  }

  function fetchIdeas(page, size, cb) {
    $.get('fetch', { page, size }, (result) => {
      cb(result);
    });
  }

  function getIdeasHtml(ideas) {
    return $.templates('#idea_template').render(ideas);
  }

  function toggleLoadMore(total_pages, actual_page) {
    $('#load_more').removeClass('invisible');
    if (total_pages == actual_page) {
      $('#load_more').hide();
    }
  }

  function initIdeasOpenHandlers(ideas) {
    ideas.forEach((idea) => {
      $('#idea_' + idea.id).click(onIdeaClick);
    });
  }

})();