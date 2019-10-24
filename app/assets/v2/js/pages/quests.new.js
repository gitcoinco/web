
$(document).ready(function() {

  $(document).on('form#newkudos', 'submit', function(e) {
    // e.preventDefault();
    // console.log($(this).formdata);
    // alert('hi');
  });
  
  $(document).on('click', '.add_answer', function(e) {
    e.preventDefault();
    var dupe_me = $(this).parents('.form-group').find('span:last');
    var clone = dupe_me.clone();

    dupe_me.after(clone);
  });

  $(document).on('click', '.add_question', function(e) {
    e.preventDefault();
    var dupe_me = $('.form-group.question:last');
    var clone = dupe_me.clone();

    dupe_me.after(clone);
  });


  $(document).on('click', '.close_answer', function(e) {
    e.preventDefault();
    if ($(this).parents('.question').find('span').length <= 1) {
      alert('you cannot have 0 answers per question');
      return;
    }
    var ele = $(this).parents('span');

    ele.remove();
  });
  $(document).on('click', '.remove', function(e) {
    e.preventDefault();
    $(this).parents('.form-group').find('.hidden').removeClass('hidden');
    $(this).parents('.form-group').find('.default_kudos').remove();
    $(this).parents('.form-group').find('input[name=enemy]').remove();
    $(this).parents('.form-group').find('[name=enemy2]').attr('name', 'enemy');
    $(this).parents('.form-group').find('[name=reward2]').attr('name', 'reward');
    $(this).remove();
  });

  var update_total_amount = function() {
    var total = parseFloat($('#token_amount').val()) * parseInt($('#max_winners').val());

    $('#total_tokens').val(total);
  };

  $('#token_amount').keyup(update_total_amount);
  $('#max_winners').keyup(update_total_amount);

  $('#myTab a').click(function(e) {
    e.preventDefault();
    var target = $(this).data('href');

    $('.target_tab').addClass('hidden');
    $('.nav-link').removeClass('active');
    $(this).addClass('active');
    $('.target_tab.' + target).removeClass('hidden');
    $('#token_reward').val(target);
    $('html,body').animate({
      scrollTop: '+=1px'
    });
  });

  load_tokens();
  $('select[name=denomination]').select2();
  setTimeout(function() {
    if (document.denomination) {
      $('select[name=denomination] option[value="' + document.denomination + '"]').prop('selected', 'selected').change();
      $('select[name=denomination]').trigger('select2');
    }
  }, 1500);

  $(document).on('click', '.close_question', function(e) {
    e.preventDefault();
    if ($('div.question').length <= 1) {
      alert('you cannot have 0 questsions');
      return;
    }
    var ele = $(this).parents('div.question');

    ele.remove();
  });

});
