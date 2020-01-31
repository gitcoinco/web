let questions = {};
let answers = {};
let authProfile = document.contxt.profile_id;
let network = document.contxt.env === 'prod' ? 'mainnet' : 'rinkeby';

// Vue.use(VueAxios, axios)
let csrftoken = $("#questions-board input[name='csrfmiddlewaretoken']").val();
axios.defaults.xsrfCookieName = csrftoken;
axios.defaults.xsrfHeaderName = "X-CSRFTOKEN";

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
    answer: function() {
      let vm = this;
      let answer = 'my answer is the right one!';
      let apiUrlSubmitAnswer = `/questions/1/answers/`;
      fetch(apiUrlSubmitAnswer, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json; charset=utf-8',
          'X-CSRFToken': csrftoken},
        body: JSON.stringify({
          question_id: 1,
          text: answer,
          owner: authProfile
        })
      });
    },
    ask: function() {},
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
