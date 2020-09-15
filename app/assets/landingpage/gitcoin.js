$(document).ready(function(){
	$("span").click(function(e){
		let href = $(this).attr('href');
		if(href){
			document.location.href= href;
			e.preventDefault();
		}
	});

});




