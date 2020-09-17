let hasGeneratedBrightIdQRCode = false;

let brightIDCalls = [];

let show_brightid_connect_modal = function(brightid_uuid) {
  const brightIdLink = `https://app.brightid.org/link-verification/http:%2f%2fnode.brightid.org/Gitcoin/${brightid_uuid}`;
  const brightIdAppLink = `brightid://link-verification/http:%2f%2fnode.brightid.org/Gitcoin/${brightid_uuid}`;

  const content = $.parseHTML(
    `<div id="connect_brightid_modal" class="modal fade" tabindex="-1" role="dialog" aria-hidden="true">
        <div class="modal-dialog">
          <div class="modal-content px-4 py-3">
            <div class="col-12">
              <button type="button" class="close" data-dismiss="modal" aria-label="Close">
                <span aria-hidden="true">&times;</span>
              </button>
            </div>
            <div class="col-12 pt-2 pb-2 text-center">
              <img src="/static/v2/images/project_logos/brightid.png" alt="BrightID Logo" width="100">
              <h2 class="font-title mt-2">Connect With BrightID</h2>
            </div>
            <div class="col-12 pt-2">
              <p>
                BrightID is a digital identity solution that ensures accounts in any application are created by real humans; each user is unique and only has one account.
                <a href="https://www.brightid.org/" target="_blank">Learn More</a>.
              </p>
              <p>
                To increase your Trust Bonus using BrightID, you must first get connected. Follow these steps:
              </p>
              <p>
                <strong>Step 1</strong>: Download the BrightID App on your mobile device<br />
                <a href="https://apps.apple.com/us/app/brightid/id1428946820">
                  <img src="/static/v2/images/app_stores/apple_app_store.svg" width="100">
                </a>
                <a href="https://play.google.com/store/apps/details?id=org.brightid">
                  <img src="/static/v2/images/app_stores/google_play_store.png" width="125">
                </a>
              </p>
              <p>
                <strong>Step 2</strong>: Connect BrightID to Gitcoin by scanning this QR code
                from the BrightID app, or <a href="${brightIdLink}">clicking here</a> from your mobile device.
                <div style="display: flex; justify-content: center; text-align: center;" id="qrcode"></div>
              </p>
              <div class="col-12 my-4 text-center">
                <a href="" class="btn btn-gc-blue px-5 mb-2 mx-2">Done Connecting</a>
              </div>
            </div>
          </div>
        </div>
      </div>`);

  $(content).appendTo('body');
  $('#connect_brightid_modal').bootstrapModal('show');

  // avoid duplicate QR Codes if user presses button multiple times
  if (!hasGeneratedBrightIdQRCode) {
    const element = document.getElementById('qrcode');
    const qrCodeData = {
      text: brightIdAppLink,
      width: 175,
      height: 175
    };

    new QRCode(element, qrCodeData); // eslint-disable-line

    hasGeneratedBrightIdQRCode = true;
  }
};

let show_brightid_verify_modal = function(brightid_uuid) {
  let callsMarkup = '';

  brightIDCalls = calendarData;

  function dateFormatter(date) {
    let options = {hour: 'numeric', minute: 'numeric', dayPeriod: 'short'};

    return new Intl.DateTimeFormat('en-US', options).format(new Date(date));
  }

  for (let index = 0; index < brightIDCalls.length; index++) {
    const call = brightIDCalls[index];
    const callDate = new Date(parseFloat(call.date) * 1000);

    let callsDate = call.dates.map((date) => {
      return `<span>${dateFormatter(date.timeStart)}</span> - <span>${dateFormatter(date.timeEnd)}</span>`;
    }).join(' <b>&</b> ');

    callsMarkup = `${callsMarkup}
        <div class="row mb-3">
          <div class="col-md-8">
            <strong class="d-block">${call.when}</strong>
            <div class="font-caption">
              At ${callsDate}
            </div>
          </div>

          <div class="col-md-4 my-auto">
            <a href="${call.link}" target="_blank" class="btn btn-sm btn-block btn-gc-blue px-4 font-caption font-weight-bold">Register <br> on ${call.platform}</a>
          </div>
        </div>
      `;
  }

  const content = $.parseHTML(
    `<div id="verify_brightid_modal" class="modal fade" tabindex="-1" role="dialog" aria-hidden="true">
        <div class="modal-dialog">
          <div class="modal-content px-4 py-3">
            <div class="col-12">
              <button type="button" class="close" data-dismiss="modal" aria-label="Close">
                <span aria-hidden="true">&times;</span>
              </button>
            </div>
            <div class="col-12 pt-2 pb-2 text-center">
              <img src="/static/v2/images/project_logos/brightid.png" alt="BrightID Logo" width="100">
              <h2 class="font-title mt-2">Verify Your BrightID</h2>
            </div>
            <div class="col-12 pt-2">
              <p>
                BrightID is a digital identity solution that ensures accounts in any application are created by real humans; each user is unique and only has one account.
                <a href="https://www.brightid.org/" target="_blank">Learn More</a>.
              </p>
              <p>
                Now that you've connected your BrightID, you need to get verified by connecting with other real humans.
              </p>
              <p>
                <strong>Join a Gitcoin + BrightID Verification Party</strong><br />
                <small class="text-muted">
                  You can learn more about how BrightID works and make connections that will help you get verified on the verifications parties.
                  Register for one of the events.
                </small>
                ${callsMarkup}
              </p>
            </div>
          </div>
        </div>
      </div>`);

  $(content).appendTo('body');
  $('#verify_brightid_modal').bootstrapModal('show');
};
