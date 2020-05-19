$(document).ready(function () {
  $("#buy_ptoken").on("click", function () {
    $("#buy_ptoken_modal").bootstrapModal("show");
  });
  $("#redeem_ptoken").on("click", function () {
    $("#redeem_ptoken_modal").bootstrapModal("show");
  });

  $(document, "#buy_ptoken_modal").on("hidden.bs.modal", function (e) {
    $("#redeem_ptoken_modal").remove();
    $("#buy_ptoken_modal").remove();
    $("#buy_ptoken_modal").bootstrapModal("dispose");
    $("#redeem_ptoken_modal").bootstrapModal("dispose");
  });
});
