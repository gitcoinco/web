var Cookielaw = {

    createCookie: function (name, value, days) {
        var date = new Date(),
            expires = '';
        if (days) {
            date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
            expires = "; expires=" + date.toGMTString();
        } else {
            expires = "";
        }
        document.cookie = name + "=" + value + expires + "; path=/";
    },

    createCookielawCookie: function () {
        // This function has been altered to record the text of the cookie
        // consent popup
        this.createCookie('cookielaw_accepted', '1', 10 * 365);
        consent_data = {record_notice: jQuery('#CookielawBanner').text()};
        jQuery.ajax({
          type: 'POST',
          url: '/record_consent/',
          data: consent_data,
          dataType: 'json',
          success: function(json) {
          },
          error: function() {
          }
        });
        if (typeof (window.jQuery) === 'function') {
            if(jQuery(".sumome-react-wysiwyg-popup-container").length < 1){
                jQuery('#CookielawBanner').slideUp();
            }
        } else {
            document.getElementById('CookielawBanner').style.display = 'none';
        }
    }

};
