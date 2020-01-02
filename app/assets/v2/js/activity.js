$(document).ready(function() {

    // delete activity
    $(document).on('click', '.delete_activity', function(e){
        e.preventDefault()
        if (!document.contxt.github_handle) {
        _alert('Please login first.', 'error');
        return;
        }

        // update UI
        $(this).parents('.row.box').remove();

        // remote post
        var params = {
          'method': 'delete',
        };
        var url = '/api/v0.1/activity/' + $(this).data('pk');
        $.post(url, params, function(response) {
            // no message to be sent
        });

    });

    // like activity
    $(document).on('click', '.like_activity', function(e){
        e.preventDefault()
        if (!document.contxt.github_handle) {
        _alert('Please login first.', 'error');
        return;
        }

        var is_unliked = $(this).data('state') == 'unliked';
        if(is_unliked){ // like
            $(this).find('span.action').html('👎');
            $(this).data('state', 'liked');
            var num = $(this).find('span.num').html();
            num = parseInt(num) + 1;
            $(this).find('span.num').html(num);
        }else{ // unlike
            $(this).find('span.action').html('👍');
            $(this).data('state', 'unliked');
            var num = $(this).find('span.num').html();
            num = parseInt(num) - 1;
            $(this).find('span.num').html(num);
        }

        // remote post
        var params = {
          'method': 'like',
          'direction': $(this).data('state'),
        };
        var url = '/api/v0.1/activity/' + $(this).data('pk');
        $.post(url, params, function(response) {
            // no message to be sent
        });


    });

    var post_comment = function($parent){
        if (!document.contxt.github_handle) {
            _alert('Please login first.', 'error');
            return;
        }

        // user input
        var comment = prompt('What is your comment?', 'Comment: ');

        // validation
        if(!comment){
            return;
        }

        // increment number
        var num = $parent.find('span.num').html();
        num = parseInt(num) + 1;
        $parent.find('span.num').html(num);
        
        // remote post
        var params = {
          'method': 'comment',
          'comment': comment
        };
        var url = '/api/v0.1/activity/' + $parent.data('pk');
        $.post(url, params, function(response) {
            view_comments($parent);
        });
    }

    var view_comments = function($parent){

        // remote post
        var params = {
          'method': 'comment'
        };
        var url = '/api/v0.1/activity/' + $parent.data('pk');
        $.get(url, params, function(response) {
            var $target = $parent.parents('.row.box').find('.comment_container');
            $target.addClass('filled');
            $target.html('');
            for(var i=0;i<response['comments'].length;i++){
                var comment = sanitizeAPIResults(response['comments'])[i];
                var timeAgo = timedifferenceCvrt(new Date(comment['created_on']));
                var html = "<li><a href=/profile/"+comment['profile_handle']+"><img src=/dynamic/avatar/"+comment['profile_handle']+"></a> <a href=/profile/"+comment['profile_handle']+">" + comment['profile_handle'] + "</a>, " + timeAgo + ": " + comment['comment'] + "</li>";
                $target.append(html);
            }
            $target.append("<a href=# class=post_comment>Post comment &gt;</a>")
        });
    }

    // post comment activity
    $(document).on('click', '.comment_activity', function(e){
        e.preventDefault()
        var num = $(this).find('span.num').html();
        if(parseInt(num) == 0){
            post_comment($(this));
        } else {
            view_comments($(this));
        }
    });

    // post comment activity
    $(document).on('click', '.post_comment', function(e){
        e.preventDefault()
        var $target = $(this).parents('.row.box').find('.comment_activity');
        post_comment($target);
    });


}(jQuery));