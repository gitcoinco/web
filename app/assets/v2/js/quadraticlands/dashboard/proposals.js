document.addEventListener('DOMContentLoaded', function() {

  // docs : https://docs.snapshot.org/hub-api

  const snapshot_api = 'https://hub.snapshot.page/api/gitcoindao/proposals';
  const proposals = document.getElementById('proposals');

  fetch(snapshot_api)
    .then(res => res.json())
    .then(data => updateProposals(data));

});


function updateProposals(data) {

  const now = Math.floor(Date.now() / 1000);

  // loop through all proposals
  for (const [ key, value ] of Object.entries(data)) {

    // just show actives
    if (value.msg.payload.end >= now) {

      // awesome new template way of doing things :)
      proposal_template = document.getElementById('proposal_template').content;
      copy = document.importNode(proposal_template, true);
      copy.querySelector('.name').textContent = value.msg.payload.name;
      copy.querySelector('.name').href = 'https://snapshot.org/#/gitcoindao/proposal/' + value.authorIpfsHash;
      document.getElementById('proposals').appendChild(copy);

      // console.log(value)

    }

  }

}
