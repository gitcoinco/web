
$(document).ready(function() {
  $("a").click(function(e){
    var href = $(this).attr('href');
    if (href=='#'){
      alert("Coming soon!");
      e.preventDefault();
      return;
    }
  })

});
