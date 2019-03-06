$(document).on('click', '#notify_funder_submit', (event) => {
  event.preventDefault();
  $(document).on('hidden.bs.modal', '#modal', (e) => {
	  notify_funder_submit();
	  e.preventDefault();
  });
});
const notify_funder_submit = () => {
  if ($('#notify_funder_modal_form .form-check-input').is(':checked')) {
    notify_funder(document.result['network'], document.result['standard_bounties_id'], {});
  }
};
