/* eslint-disable no-console */

let anchors = document.getElementsByTagName( 'a' );

for ( let i = 0; i < anchors.length; i++ ) {
  if ( anchors[i].getAttribute( 'target' ) === '_blank' && ~anchors[i].getAttribute( 'rel' ) ) {
    anchors[i].setAttribute( 'rel', 'noopener noreferrer' );
  }

  if ( ~anchors[i].getAttribute( 'href' ).indexOf( 'http://' ) ) {
    let secure = anchors[i].href.split( '/' );

    anchors[i].href = `https://${secure[2]}`;
  }
}
