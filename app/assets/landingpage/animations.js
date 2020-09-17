$(document).ready(function(){

	// add on each h1, h2, p, button 
	// some sal data attributes
	// to fade in all elements with some delay

	$( "h1" ).each(function( index) {
	  	$(this).attr('data-sal', 'zoom-in');
	  	$(this).attr('data-sal-delay', '0');
	  	$(this).attr('data-sal-duration', '300');
	});

	$( "h2" ).each(function( index) {
	  	$(this).attr('data-sal', 'zoom-in');
	  	$(this).attr('data-sal-delay', '100');
	  	$(this).attr('data-sal-duration', '400');
	});

	$( "p" ).each(function( index) {
	  	$(this).attr('data-sal', 'zoom-in');
	  	$(this).attr('data-sal-delay', '200');
	  	$(this).attr('data-sal-duration', '500');
	});

	$( "a.btn" ).each(function( index) {
	  	$(this).attr('data-sal', 'zoom-in');
	  	$(this).attr('data-sal-delay', '300');
	  	$(this).attr('data-sal-duration', '600');
	});

	$( "figure" ).each(function( index) {
	  	$(this).attr('data-sal', 'fade');
	  	$(this).attr('data-sal-delay', '100');
	  	$(this).attr('data-sal-duration', '700');
	});

	x = 100;
	$( "#twitter figure" ).each(function( index) {
		x = x + 100;
	  	$(this).attr('data-sal', 'zoom-in');
	  	$(this).attr('data-sal-delay', x);
	  	$(this).attr('data-sal-duration', '500');
	});

	x = 100;
	$( "#partners figure" ).each(function( index) {

		x = x + 100;
	  	$(this).attr('data-sal', 'zoom-in');
	  	$(this).attr('data-sal-delay', x);
	  	$(this).attr('data-sal-duration', '500');
	});


	x = 100;
	$( "#footersocial figure" ).each(function( index) {

		x = x + 100;
	  	$(this).attr('data-sal', 'zoom-in');
	  	$(this).attr('data-sal-delay', x);
	  	$(this).attr('data-sal-duration', '500');
	});



	// init sal ( observer based animation framework )

	sal({
	  threshold: 0.3,
	  once: false
	});




	// custom scroll based behaviours
	// do not know how to do this with observer
	// so i do classic style ...

	$(window).scroll(function() {

		// current height of page
	    var height = $(window).scrollTop();

	    // y1 = a bit when whatisgitcoin section starts - then dim town down
		y1 = $('#whatisgitcoin').offset().top / 2;

		// y2 = a bit when fotter navigation is in view - then bring back full opacity to town
		y2 = $('#footernavigation').offset().top - 500;

		// console.log("currentheight:" + height + " dim-start:" + y1 + " dim-end:" + y2);

	    if(height  > y1 && height < y2 ) {
	        $( "#town" ).addClass("dim");
	        $( "#fixed-signup-button" ).addClass("show");

	    }
	    else{
	    	$( "#town" ).removeClass("dim");
	    	$( "#fixed-signup-button" ).removeClass("show");
	    }


	});



});




