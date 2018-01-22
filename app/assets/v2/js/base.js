$(document).ready(function() {
    $( document ).tooltip();

    $(".nav-link.dropdown-toggle").click(function(e){
      if($(".dropdown-menu").css('display') == 'block'){
        $(".dropdown-menu").css('display', 'none');        
      } else {
        $(".dropdown-menu").css('display', 'block');        
      }
      e.preventDefault();
    });

    //get started modal
    $("a[href='/get']").click(function(e) {
      e.preventDefault();
      var url = $(this).attr('href');
      setTimeout(function(){
        $.get(url, function(newHTML){
            console.log('got' + newHTML);
            $(newHTML).appendTo('body').modal();
        });
      },300);
    });

    //preload hover image
    var url = $("#logo").data('hover');
    $.get(url,function(){});

    $("#logo").mouseover(function(e){
      $(this).attr('old-src', $(this).attr('src'));
      var new_src = $(this).data('hover');
      $(this).attr('src', new_src);
      e.preventDefault();
    });

    $("#logo").mouseleave(function(e){
      $(this).attr('src', $(this).attr('old-src'));
    });

    $(".navbar-toggler").click(function(){
      $(".navbar-collapse").toggleClass('show')
    });

    //get started modal
    $("body").delegate('.iama','click', function(){
        document.location.href = $(this).find('a').attr('href');
    });

    //pulse animation on click
    $('.pulseClick').click(function(e){
      var ele = $(this);
      ele.addClass("pulseButton");
      var callback = function(){
        ele.removeClass("pulseButton");
      };
      setTimeout(callback,300);
    });

    $('.faq_item h5').click(function(){
      $(this).parents('.faq_parent').find('.answer').toggleClass('hidden');
    });

    //mixpanel integration
    setTimeout(function(){
      var web3v = (typeof web3 == 'undefined' || typeof web3.version == 'undefined') ? 'none' : web3.version.api;
      var params = {
        page: document.location.pathname,
        web3: web3v,
      }
      mixpanel.track("Pageview", params);
    },300);

    var tos = [
      'slack',
      'btctalk',
      'reddit',
      'twitter',
      'fb',
      'medium',
      'gitter',
      'github',
      'youtube',
      'extension',
      'get',
      'watch',
      'unwatch',
      'save_search',
      'help/repo',
      'help/dev',
      'help/portal',
      'help/faq',
    ]

    for(var i=0;i<tos.length;i++) {
      var to = tos[i]
      var callback = function(e) {
        var _params = {
          'to': $(this).attr('href'),
        };
        mixpanel.track("Outbound", _params);
      };
      $('body').delegate("a[href='/"+to+"']",'click', callback);
    }

    $('body').delegate("a[href^='https://github.com/']", 'click', function(e) {
        var _params = {
          'to_domain': 'github.com',
          'to': $(this).attr('href'),
        };
        mixpanel.track("Outbound", _params);
      });

    // To be deprecrated with #newsletter-subscribe
    $("#mc-embedded-subscribe").click(function() {
        mixpanel.track("Email Subscribe");
    });

    $("#newsletter-subscribe").click(() => {
        mixpanel.track("Email Subscribe");
    });

    $("body.whitepaper .btn-success").click(function() {
        mixpanel.track("Whitepaper Request");
    });
});

$(window).scroll(function(){
    var scrollPos = $(document).scrollTop();
});
