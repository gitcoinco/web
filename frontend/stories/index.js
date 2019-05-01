import React from 'react';

import {storiesOf} from '@storybook/react';
import {action} from '@storybook/addon-actions';
import {linkTo} from '@storybook/addon-links';

import {Button, Welcome} from '@storybook/react/demo';
import {ExpertSession, ExpertSessionContext} from "../src/App";
import 'bootstrap/dist/css/bootstrap.min.css';
import {waitingToStart} from "./sampleData";

storiesOf('Welcome', module).add('to Storybook', () => <Welcome showApp={linkTo('Button')}/>);


// storiesOf('ExpertSession', module)
//   .add('waiting to start - host', () => <ExpertSessionContext.Provider value={{session: waitingToStart}}>
//       <ExpertSession
//         foo={"bar"}
//         // handleStartSession={action('click')}
//       >test</ExpertSession>
//     </ExpertSessionContext.Provider>
//   )
//   .add('waiting to start - guest', () => <p>test</p>)
//   .add('in progress - host', () => <p>test</p>)
//   .add('in progress - guest', () => <p>test</p>)
//   .add('finished - host', () => <p>test</p>)
//   .add('finished - guest', () => <p>test</p>);
