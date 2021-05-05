document.addEventListener('DOMContentLoaded', function() {
  const tweet_button = document.getElementById('tweet_button');
  const twitter_url = 'https://twitter.com/intent/tweet';

  tweet_button.href = twitter_url + '?text=' + tweet_button.dataset.tweet_text + '&url=' + tweet_button.dataset.tweet_url + '&hashtags=' + tweet_button.dataset.tweet_hashtags;
  tweet_button.target = '_blank';
});
