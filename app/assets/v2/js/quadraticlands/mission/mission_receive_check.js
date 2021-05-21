// checks from <div id="receive_check"> via passed data-atributes
// if a user_profile_id has claimed tokens via isClaimed(user_profile_id) 
// but mission status proof_of_receive is still "false" and if so,
// forward a user to /mission/receive/outro to finish the claim experience
// and update proof_of_receive database to true there.

document.addEventListener('DOMContentLoaded', function() {
  document.addEventListener('dataWalletReady', missionReceiveCheck);
});

async function missionReceiveCheck() {

  try {
    console.debug("Mission Receive Check")

    let receive_check = document.getElementById('receive_check');
    let proof_of_receive = receive_check.dataset.proof_of_receive;
    let user_profile_id = receive_check.dataset.user_profile_id;
    let claimed = await isClaimed(user_profile_id);
    
    //console.debug("proof_of_receive:", proof_of_receive)
    //console.debug("user_profile_id:", user_profile_id)
    //console.debug("claimed:", claimed)

    if ( claimed == true && proof_of_receive =="false" ) {
        window.location = 'mission/receive/outro';
        console.debug("continue finishing proof of receive outro to unlock mission 3")
    }

  } catch (e) {
    console.error(e);
  }

}