
new Vue({
    delimiters: ['[[', ']]'],
    data () {
        return {
            showVerificationWarning: true
        }
    },
    'el': "gc-grant-detail",
    "methods": {
        twitterVerification(handle) {
            if (handle == ''){
                _alert('Please add a twitter account to your grant!', 'error', 5000);
                return;
            }
            const response = await fetchData('/grants/v1/api/{{grant.id}}/verify');

            if (!response.ok) {
              _alert(response.msg, 'error');
              return;
            }
            if (response.verified) {
              _alert('Congratulations, your grant is now verified!', 'success', 5000)
              this.showVerificationWarning = false
              $('#startTwitterVerification .close').click()
            }
      
            if (!response.has_text) {
              _alert('Unable to verify tweet from {{ grant.twitter_handle_1 }}.  Is the twitter post live?  Was it sent from {{ grant.twitter_handle_1 }}?', 'error', 5000)
              return;
            }
      
            if (!response.has_code) {
              _alert(`Missing emoji code "{{ user_code }}", please don't remove this unique code before validate your grant.`, 'error', 5000)
              return;
            }
      
        }
    }
})