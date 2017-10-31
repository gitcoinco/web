$(document).ready(function(){
    $(".leaderboard_entry").each(function(){
        $(this).changeElementType('a'); // hack so that users can right click on the element
    });
    $("#key").change(function(){
        var val = $(this).val();
        document.location.href = '/leaderboard/' + val;
    })

});