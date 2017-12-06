$(document).ready(function () {
  $('.leaderboard_entry .progress-bar').each(function () {
    var max = parseInt($(this).attr('aria-valuemax'))
    var now = parseInt($(this).attr('aria-valuenow'))
    var width = (now * 100) / max
    $(this).css('width', width + '%')
  })

  $('.clickable-row').click(function () {
    window.location = $(this).data('href')
  })

  $('#key').change(function () {
    var val = $(this).val()
    document.location.href = '/leaderboard/' + val
  })
})
