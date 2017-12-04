$( '.content-slider__nav--right' ).click( function( e ) {
    var currentSlide = $( '.active-slide' ),
        nextSlide = currentSlide.next();

    e.preventDefault();

    if ( nextSlide.length === 0 ) {
        nextSlide = $( '.content-slider__item' ).first();
    }

    currentSlide.fadeOut( 600 ).removeClass( 'active-slide' );
    nextSlide.fadeIn( 600 ).addClass( 'active-slide' );
});

$( '.content-slider__nav--left' ).click( function( e ) {
    var currentSlide = $( '.active-slide' ),
        prevSlide = currentSlide.prev();

    e.preventDefault();

    if ( prevSlide.length === 0 ) {
        prevSlide = $( '.content-slider__item' ).last();
    }

    currentSlide.fadeOut(600).removeClass( 'active-slide' );
    prevSlide.fadeIn(600).addClass( 'active-slide' );
});

$( window ).on( 'load resize', function() {
    var x = $( '.active-slide img' ).height() + 'px',
        y = window.outerWidth - $( '.content-slider__nav' ).width() - 30 + 'px';


    $( '.content-slider__item' ).css( 'min-height', x );
    $( '.content-slider' ).css( 'min-height', x );
    $( '.content-slider' ).parent().css( 'max-width', y );
});


$( '.content-slider__item:first' ).addClass( 'active-slide' );