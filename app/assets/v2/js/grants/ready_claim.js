Vue.component('matching-claim', {
  delimiters: [ '[[', ']]' ],
  props: [ 'match', 'grant' ],
  methods: {
    filterMatchingPayout(matches) {
      return matches.filter(match => match.grant_payout);
    }
  },
  computed: {
    status() {
      return this.match.grant_payout.status;
    },
    activeClaimPeriod() {
      if (this.status === 'ready' && this.match.ready_for_payout) {
        return true;
      }

      return this.status === 'pending';
    },
    isKYCPending() {
      return !this.match.ready_for_payout && this.match.grant_payout.status == 'ready';
    },
    claimStartDate() {
      return this.match.grant_payout.grant_clrs[0].claim_start_date;
    },
    claimEndDate() {
      return this.match.grant_payout.grant_clrs[0].claim_end_date;
    }
  }
});
