var ideaShared = (function() {
  function prepareIdea(idea) {
    idea.threadIdent = 'idea-' + idea.id;
    idea.posts = 0;
    idea.likes = 0;
  }

  function applyThreadData(idea, thread) {
    idea.posts = thread.posts;
    idea.likes = thread.likes;
  }

  return {
    prepareIdea, applyThreadData
  };
})();