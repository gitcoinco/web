import {INIT_APP_COMPLETE, WEB3_INIT_COMPLETE} from "./types";
import Web3 from "web3";
import PaymentChannelsArtifact from "../truffle-build/PaymentChannels";



// TODO move to utils
function generateDelegateAccount(web3) {
  let account = web3.eth.accounts.create();
  return {
    address: account.address,
    privateKey: account.privateKey
  }
}

// TODO utils
export function getContract(web3Context) {
  // set up the deployed state channel contract
  const networkId = web3Context.networkId;
  if (PaymentChannelsArtifact.networks[networkId] === undefined) {
    throw new Error('Contract not deployed to network ' + networkId);

  }
  const deployedAddress = PaymentChannelsArtifact.networks[networkId].address;
  return web3Context.library.eth.Contract(PaymentChannelsArtifact.abi, deployedAddress);

}


export const initApp = (sessionId, channelManager) => {
  return (dispatch, getState, api) => {


    // TODO confirm this is ok - using web3 outside of web3-react
    let web3 = new Web3(Web3.givenProvider);

    // set up the delegate wallet if it does not exist
    let delegateAccount = localStorage.getItem('delegateAccount');
    if (delegateAccount === null) {
      delegateAccount = generateDelegateAccount(web3);
      localStorage.setItem('delegateAccount', JSON.stringify(delegateAccount))
    } else {
      delegateAccount = JSON.parse(delegateAccount)
    }

    api.getAppInit(sessionId).then((res) => {
      dispatch({
        type: INIT_APP_COMPLETE, data: {
          session: res.data.session,
          user: res.data.profile,
          delegateAccount: delegateAccount,
          channelManager: channelManager
        }
      })

    })
  };
};


export const requestSessionTicket = (ticketRequest) => {
  return (dispatch, getState, api) => {
    api.requestSessionTicket(ticketRequest)
  };
};


export const sendSessionTicket = (ticket) => {
  return (dispatch, getState, api) => {
    api.sendSessionTicket(ticket)
  };
};


export const endSession = (sessionId) => {
  return (dispatch, getState, api) => {
    api.endSession(sessionId)
  };
};


export const sendJoinRequest = (joinRequest) => {
  return (dispatch, getState, api) => {
    api.sendJoinRequest(joinRequest)
  };
};

export const acceptJoinRequest = (joinRequest) => {
  return (dispatch, getState, api) => {
    api.acceptJoinRequest(joinRequest)
  };
};


export const cancelJoinRequest = (joinRequest) => {
  return (dispatch, getState, api) => {
    api.cancelJoinRequest(joinRequest)
  };
};

export const startSession = (sessionId, txHash) => {
  // host wants to broadcast the tx to start the session
  return (dispatch, getState, api) => {
    api.startSession(sessionId, txHash)
  };
};


export const startSessionConfirmed = (sessionId, txHash, sessionAddress) => {
  // start tx has been confirmed
  return (dispatch, getState, api) => {
    api.startSessionConfirmed(sessionId, txHash, sessionAddress)
  };
};


export const fundsClaimed = (sessionId, txHash) => {
  // host has broadcast tx to start the session
  return (dispatch, getState, api) => {
    api.fundsClaimed(sessionId, txHash)
  };
};


export const createSession = (sessionDetails, history) => {
  // host has broadcast tx to start the session

  // hackily passing in history here - refactor if needed in other actions
  return (dispatch, getState, api) => {
    api.createSession(sessionDetails).then((res) => {
      history.push('/experts/sessions/' + res.data.id + '/')
    }).catch((err) => {
      throw new Error(err)
    })
  };
};


