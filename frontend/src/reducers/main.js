import {INIT_APP_COMPLETE, SESSION_UPDATE_RECEIVED, WEB3_INIT_COMPLETE} from "../actions/types";


export default function mainReducer(state = [], action) {
  switch (action.type) {
    case INIT_APP_COMPLETE:
      return action.data;

    case SESSION_UPDATE_RECEIVED:
      return Object.assign({}, state, {
        session: action.data
      });

    default:
      return state;
  }
}
