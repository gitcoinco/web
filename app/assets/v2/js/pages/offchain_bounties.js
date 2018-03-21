$(document).ready(function() {
  $('.checkbox .checkbox-label').click(function() {
    if ($(this).parents('.checkbox').find('.checkbox-input').is(':checked')) {
      $(this).parents('.checkbox').find('.checkbox-input').prop('checked', false);
      $('.bounties-container a.bounty').each(function() {
        $(this).removeClass('hidden');
      });
      return false;
    }
    $('.checkbox .checkbox-input:checked').prop('checked', false);

    var text = $(this).text().toLowerCase();
    var isSelected = $(this).parents('.checkbox').find('.checkbox-input:checked').length;

    if (isSelected) {
      $('.bounties-container a.bounty').each(function() {
        $(this).removeClass('hidden');
      });
    } else {
      $('.bounties-container a.bounty').each(function() {
        var this_text = $(this).text().toLowerCase();
        var does_contain_text = this_text.toLowerCase().indexOf(text) != -1;

        if (does_contain_text) {
          $(this).removeClass('hidden');
        } else {
          $(this).addClass('hidden');
        }
      });
    }
  });


  $('.gc-round-text-input').keydown(function() {
    var text = $(this).val();
    var is_empty = text == '';

    $('.bounties-container a.bounty').each(function() {
      var this_text = $(this).text().toLowerCase();
      var does_contain_text = this_text.toLowerCase().indexOf(text) != -1;

      if (does_contain_text || is_empty) {
        $(this).removeClass('hidden');
      } else {
        $(this).addClass('hidden');
      }
    });
  });
});
