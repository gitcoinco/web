$(document).ready(function() {
  var base_url = '/quadraticlands/mission/postcard/svg?';
  var $target = $('#target');

  $('#text').keyup(function() {
    update_output();
  });
  $('.backgrounds li').click(function() {
    $(this).parents('.parent').find('li').removeAttr('selected');
    $(this).attr('selected', 'selected');
    update_output();
  });
  var update_output = function() {
    let text = $('#text').val();

    text = text.replace(/[\r\n]/gm, ' NEWLINE ');
    const selected = $('li[selected=selected]');
    let attrs = `&text=${text}`;

    for (let i = 0; i < selected.length; i++) {
      const key = $(selected[i]).attr('name');
      const val = $(selected[i]).attr('value');

      attrs += `&${key}=${val}`;
    }
    const url = base_url + attrs;

    $target.attr('src', url);
  };

  update_output();
});
