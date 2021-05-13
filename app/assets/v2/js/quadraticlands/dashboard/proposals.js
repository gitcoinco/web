document.addEventListener('DOMContentLoaded', function() {

  // snapshot
  const snapshot_api = 'https://hub.snapshot.page/api/gitcoindao/proposals';

  fetch(snapshot_api).then(res => res.json()).then(data => updateSnapshotStats(data));

  // compound
  updateCompoundStats();

  // discourse
  updateDiscourseStats();

});


// count active snapshot proposals
// @ALL still needs to be tested - i can not create proposals!
// @ALL maybe theres an easyer way tho via api to find just the ACTIVES and sum up ?
function updateSnapshotStats(data) {
  x = 0;
  const now = Math.floor(Date.now() / 1000);
  // loop through all proposals

  for (const [ key, value ] of Object.entries(data)) {
    // just count actives
    if (value.msg.payload.end >= now) {
      x++;
    }
  }

  const stats_snapshot = document.getElementById('stats-snapshot');

  stats_snapshot.innerHTML = x;
  if (x >= 1) {
    stats_snapshot.classList.add('aqua');
  }
}


// count active compound proposals
function updateCompoundStats() {
  x = 1337;
  const stats_compound = document.getElementById('stats-compound');

  stats_compound.innerHTML = x;
  if (x >= 1) {
    stats_compound.classList.add('aqua');
  }
}


// count active compound proposals
function updateDiscourseStats() {
  x = 23;
  const stats_discourse = document.getElementById('stats-discourse');

  stats_discourse.innerHTML = x;
  if (x >= 1) {
    stats_discourse.classList.add('aqua');
  }
}