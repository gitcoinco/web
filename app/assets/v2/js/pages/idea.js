(function(ideaShared, disqus_config) {

  $('document').ready(() => {
    $.get('get', (result) => {
      var idea = result.idea;

      ideaShared.prepareIdea(idea);
      $.get('https://disqus.com/api/3.0/threads/details.json',
        {
          api_key: disqus_config.api_key,
          forum: disqus_config.shortname,
          'thread:ident': idea.threadIdent
        },
        function(result) {
          ideaShared.applyThreadData(idea, result.response);
        }).always(function() {
        renderIdea(idea);
      });

      window.disqus_config = function() {
        this.page.url = window.location.href;
        this.page.identifier = idea.threadIdent;
      };
      // ajax request to load the disqus javascript
      $.ajax({
        type: 'GET',
        url: 'http://' + disqus_config.shortname + '.disqus.com/embed.js',
        dataType: 'script',
        cache: true
      });

    });
  });

  function renderIdea(idea) {
    var html = $.templates('#idea_template').render(idea);

    $('#idea').html(html);
  }

})(ideaShared, disqus_config);