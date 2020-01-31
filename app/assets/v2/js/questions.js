let questions = {};
let answers = {};
let authProfile = document.contxt.profile_id;
let network = document.contxt.env === 'prod' ? 'mainnet' : 'rinkeby';

let csrftoken = $("#questions-board input[name='csrfmiddlewaretoken']").val();

Vue.mixin({
  methods: {
    fetchQuestions: function() {
      let vm = this;
      let apiUrlQuestions = `/questions/`;
      let getQuestions = fetchData(apiUrlQuestions, 'GET');

      $.when(getQuestions).then(function(response) {
        console.log('questions loaded');
        vm.$set(vm.questions, 'questions', response);
        vm.isLoading['questions'] = false;
        console.log(questions);
      }).catch(function() {
        vm.isLoading['questions'] = false;
        vm.error[type] = 'Error fetching questions. Please contact founders@gitcoin.co';
      });
    },
    fetchAnswers: function(question_id) {
      let vm = this;
      let apiUrlAnswers = `/questions/${question_id}/answers/`;
      let getAnswers = fetchData(apiUrlAnswers, 'GET');

      $.when(getAnswers).then(function(response) {
        vm.$set(vm.answers, 'answers', response);
        vm.isLoading[`${question_id}Answers`] = false;
      }).catch(function() {
        vm.isLoading[`${question_id}Answers`] = false;
      });
    },
    answer: function(question_id) {
      let vm = this;
      let answer = prompt('Enter your answer');
      let amount_in_eth = prompt
      let apiUrlSubmitAnswer = `/questions/${question_id}/answers/`;
      fetch(apiUrlSubmitAnswer, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json; charset=utf-8',
          'X-CSRFToken': csrftoken},
        body: JSON.stringify({
          question_id: question_id,
          text: answer,
          owner: authProfile
        })
      }).then(response => {
        vm.fetchQuestions();
      });
    },
    selectAnswer: function(question_id) {
      let vm = this;
      let answer = prompt('Enter your answer');
      let apiUrlSubmitAnswer = `/questions/${question_id}/answers/`;
      fetch(apiUrlSubmitAnswer, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json; charset=utf-8',
          'X-CSRFToken': csrftoken},
        body: JSON.stringify({
          question_id: question_id,
          text: answer,
          owner: authProfile
        })
      }).then(response => {
        vm.fetchQuestions();
      });
    },
    ask: function() {
      let vm = this;
      var question_text = prompt('Ask a question:');
      var value_in_eth = prompt('How much ETH for the right answer?');
      if (value_in_eth < 0.001) {
        _alert('Amount must be 0.001 or more.', 'error');
        return;
      }
      let apiUrlSubmitQuestion = `/questions/ask/`;
      fetch(apiUrlSubmitQuestion, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json; charset=utf-8',
          'X-CSRFToken': csrftoken},
        body: JSON.stringify({
          text: question_text,
          owner: authProfile,
          value_in_eth: value_in_eth
        })
      }).then(response => {
        vm.fetchQuestions();
      });
    },
    onLoad() {
      let vm = this;
      vm.fetchQuestions();
    },
  }
});

if (document.getElementById('questions-board')) {
  var app = new Vue({
    delimiters: [ '[[', ']]' ],
    el: '#questions-board',
    data: {
      network: network,
      questions: questions,
      answers: answers,
      disabledBtn: false,
      authProfile: authProfile,
      isLoading: {
        'questions': true,
      },
      error: {
        'questions': false,
      }
    },
    mounted() {
      this.onLoad();
    }
  });
}

function sendTip() {
  if (!document.contxt.github_handle) {
    _alert('Please login first.', 'error');
    return;
  }
  if (!web3) {
    _alert('Please enable and unlock your web3 wallet.', 'error');
    return;
  }

  const from_name = document.contxt['github_handle'];
  const username = $(this).data('username');
  const accept_tos = (confirm("Do you accept Gitcoin's terms of service at gitcoin.co/terms ?"));
  const from_email = '';
  const tokenAddress = '0x0';
  const expires = 9999999999;
  var $parent = $(this);
  var success_callback = function(txid) {
    const url = 'https://' + etherscanDomain() + '/tx/' + txid;
    const msg = 'This payment has been sent 👌 <a target=_blank href="' + url + '">[Etherscan Link]</a>';

    var new_amount = Math.round(100 * parseFloat(old_amount) + parseFloat(amountInEth)) / 100;

    _alert(msg, 'info', 1000);
  };

  var failure_callback = function() {
    $.noop(); // do nothing
  };

  return sendTip(
    email,
    github_url,
    from_name,
    username,
    amountInEth,
    comments_public,
    comments_priv,
    from_email,
    accept_tos,
    tokenAddress,
    expires,
    success_callback,
    failure_callback,
    false
  );
}
