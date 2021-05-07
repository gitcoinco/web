document.addEventListener('DOMContentLoaded', function() {

  updateInterface('enabled');

  const mode_toggle = document.getElementById('mode_toggle');

  mode_toggle.addEventListener('click', () => {

    mode = mode_toggle.getAttribute('data-mode');

    if (mode == 'disabled') {
      mode_toggle.setAttribute('data-mode', 'enabled');
      mode_toggle.classList.remove('disabled');
      mode_toggle.classList.add('enabled');
      updateInterface('enabled');
      window.kinetics.set({ particles: { toColor: '#6F3FF5' } });
    } else {
      mode_toggle.setAttribute('data-mode', 'disabled');
      mode_toggle.classList.remove('enabled');
      mode_toggle.classList.add('disabled');
      updateInterface('disabled');
      window.kinetics.set({ particles: { toColor: '#02E2AC' } });
    }

    console.debug('mode: ', mode);

  });

});


/** ********* VIEWS */
function updateInterface(status) {

  const explain_text = document.getElementById('explain_text');
  const btn_continue = document.getElementById('btn_continue');

  // ENABLED
  if (status == 'enabled') {
    explain_text.innerHTML = 'I prefer to delegate my voting power to a Gitcoin Steward who will be active and represent my views. You can always change this in your dashboard settings.';
    btn_continue.href = '/quadraticlands/mission/use/delegate';
    console.debug('INTERFACE:ENABLED');
  }

  // DISABLED
  if (status == 'disabled') {
    explain_text.innerHTML = 'I want to use my voting power to actively participate in Gitcoin’s governance. You can always change this in your dashboard settings.';
    btn_continue.href = '/quadraticlands/mission/use/vote';
    console.debug('INTERFACE:ENABLED');
  }

}
