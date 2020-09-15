$(document).ready(function(){

	// init town assets on start
	initTown();

	// on resize, re-init assets
	$(window).resize(function() {
	  initTown();
	});

	// scroll timer
	setInterval(scrollTown, 60);




});



function initTown() {

	width = $(window).width();
	height = $(window).height();

	$( "#town figure" ).each(function( index) {

		// set a random x position
		var x = Math.floor(Math.random() * width);
	  	$(this).css('transform', 'translateX(' + x + 'px)');

	  	// set height of object based on attribute data-height
	  	height = $(this).attr("data-height");
	  	$(this).css('height', height);

	  


	});


}



function scrollTown(){


	$( "#town figure" ).each(function( index) {

		// get current ypos
		var currTrans = $(this).css('-webkit-transform').split(/[()]/)[1];
		var posx = currTrans.split(',')[4];

		// set new pos based on data-speed
		speed = $(this).attr("data-speed");
	  	posx = posx - speed;

	  	// out of view on left side - bring it back to the right
	  	if (posx < -1000)
	  	{
	  		posx = width;
	  	}

	  	// set new posx
	  	$(this).css('transform', 'translateX(' + posx + 'px)');


	});


}










