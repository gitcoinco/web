import { combineReducers } from 'redux';
import mainReducer from './main';

export default combineReducers({
    data: mainReducer
});
