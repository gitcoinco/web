$(document).ready(function() {

    var time_difference_broken_down = function(difference){
        let remaining = "Available now.. Refresh to view offer!";
        let prefix = "Offer available in ";

        if (difference > 0) {
          const parts = {
            days: Math.floor(difference / (1000 * 60 * 60 * 24)),
            hours: Math.floor((difference / (1000 * 60 * 60)) % 24),
            minutes: Math.floor((difference / 1000 / 60) % 60),
            seconds: Math.floor((difference / 1000) % 60)
          };

          remaining = Object.keys(parts)
            .map(part => {
              if (!parts[part]) return;
              return `${parts[part]} ${part}`;
            })
            .join(" ");
        } else {
            return remaining;
        }
        return prefix + remaining;
    };

    var updateTimers = function(){
        $(".timer").each(function(){
            var time = $(this).data('time');
            $(this).html(time_difference_broken_down(new Date(time) - new Date()))
        });
    };
    setInterval(updateTimers, 1000);


}(jQuery));