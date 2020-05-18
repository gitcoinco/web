$(document).ready(function () {
  $(document, "#buy_ptoken_modal").on("hidden.bs.modal", function (e) {
    $("#buy_ptoken_modal").remove();
    $("#buy_ptoken_modal").bootstrapModal("dispose");
  });
});
