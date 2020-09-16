$(document).ready(function(){
	$("span, div").click(function(e){
		let href = $(this).attr('href');
		if(href){
			document.location.href= href;
			e.preventDefault();
		}
	});

});




