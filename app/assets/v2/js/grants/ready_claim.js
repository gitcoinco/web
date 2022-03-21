Vue.component('matching-claim', {
  delimiters: [ '[[', ']]' ],
  props: ['match'],
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
    claimStartDate() {
      return this.match.grant_payout.grant_clrs[0].claim_start_date;
    },
    claimEndDate() {
      return this.match.grant_payout.grant_clrs[0].claim_end_date;
    }
  }
});
