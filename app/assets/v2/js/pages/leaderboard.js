$(document).ready(function () {
  $('.leaderboard_entry .progress-bar').each(function () {
    var max = parseInt($(this).attr('aria-valuemax'))
    var now = parseInt($(this).attr('aria-valuenow'))
    var width = (now * 100) / max
    console.log(width)
    $(this).css('width', width + '%')
    // $(this).changeElementType('a'); // hack so that users can right click on the element
  })

  $('#key').change(function () {
    var val = $(this).val()
    document.location.href = '/leaderboard/' + val
  })
})
