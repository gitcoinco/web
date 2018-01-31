/* eslint-disable no-invalid-this */

$( document ).ready( () => {
  $( '.leaderboard_entry .progress-bar' ).each( () => {
    const max = parseInt( $( this ).attr( 'aria-valuemax' ) );
    const now = parseInt( $( this ).attr( 'aria-valuenow' ) );
    const width = ( now * 100 ) / max;

    $( this ).css( 'width', `${width}%` )
  })

  $( '.clickable-row' ).click( () => {
    window.location = $( this ).data( 'href' )
  });

  $( '#key' ).change( () => {
    const val = $( this ).val();

    document.location.href = `/leaderboard/${val}`
  });
});
