(function() {

  $('document').ready(() => {
    $.get('get', (result) => {
      var idea = result.idea;
      var forumName = result.forum_name;

      renderIdea(idea);

      window.disqus_config = function() {
        this.page.url = window.location.href;
        this.page.identifier = idea.thread_ident;
      };
      // ajax request to load the disqus javascript
      $.ajax({
        type: 'GET',
        url: 'http://' + forumName + '.disqus.com/embed.js',
        dataType: 'script',
        cache: true
      });

    });
  });

  function renderIdea(idea) {
    var html = $.templates('#idea_template').render(idea);

    $('#idea').html(html);
  }

})();
