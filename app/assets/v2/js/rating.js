$('[data-open-rating] input').on('click', function(e) {
  // e.stopPropagation();

  console.log(this)
  console.log($(this))
  // $('input[name="rating"]').filter('[value="'+ $(this).val() +'"]').prop('checked', true)
  console.log($(this).parent().data('openRating'))
  ratingModal($(this).parent().data('openRating'), $(this))
})

const ratingModal = (bountyId, val) => {
  let modalUrl = `/modal/rating/${bountyId}`;

  console.log(modalUrl, val.id);

  $.ajax({
    url: modalUrl,
    type: 'GET',
    cache: false
  }).done(function(result) {
    $('body').append(result);
    $('#modalRating').bootstrapModal('show');
    $('[data-toggle="tooltip"]').runTooltip();
    $('input[name="rating"]').filter('[value="'+ val.val() +'"]').prop('checked', true)
  });

  // let modalTmp = `
  // <div class="modal fade g-modal" id="modalRating" tabindex="-1" role="dialog" aria-labelledby="modalRatingTitle" aria-hidden="true">
  //   <div class="modal-dialog modal-dialog-centered modal-lg" role="document">
  //     <div class="modal-content">
  //       <div class="modal-header">
  //         <button type="button" class="close" data-dismiss="modal" aria-label="Close">
  //           <span aria-hidden="true">&times;</span>
  //         </button>
  //       </div>
  //       <div class="modal-body text-center center-block w-75">
  //         <h5>
  //           You have successfully approved the contributor to work on your bounty!
  //         </h5>
  //         <div>
  //           <img src="${document.contxt.STATIC_URL}v2/images/repo-instructions.png" class="mw-100 my-4" alt="">
  //         </div>
  //         <p class="mb-4">Now you need to invite the contributor to your private repo on GitHub You can find it under <b>GitHub repository > Settings > Collaborators</b></p>
  //         <div>
  //           <img src="${document.contxt.STATIC_URL}v2/images/repo-settings.png" class="mw-100" alt="">
  //         </div>
  //       </div>
  //       <div class="modal-footer justify-content-center">
  //         <a href="${linkToSettings}" target="_blank" class="button button--primary"><i class="fab fa-github"></i> Go to Repo Settings</a>
  //       </div>
  //     </div>
  //   </div>
  // </div>`;

  // $(modalTmp).bootstrapModal('show');

  $(document, '#modalRating').on('hidden.bs.modal', function(e) {
    // let selected = $('input[name="rating"]:checked').val()
    // console.log('closing', val.parent(), $('input[name="rating"]:checked').val())
    // $('input[name="'+ val[0].name +'"]').filter('[value="'+ $('input[name="rating"]:checked').val() +'"]').prop('checked', true)
    val.closest('.card-rating').hide()
    $('#modalRating').remove();
    $('#modalRating').bootstrapModal('dispose');
  });
};


// let modals = $('#modalInterest');
//   let modalBody = $('#modalInterest .modal-content');
//   let modalUrl = `/interest/modal?redirect=${window.location.pathname}&pk=${document.result['pk']}`;

//    modals.on('show.bs.modal', function() {
//     modalBody.load(modalUrl, ()=> {
//       if (document.result['repo_type'] === 'private') {
//         $('#nda-upload').show();
//         $('#issueNDA').prop('required', true);
//         document.result.unsigned_nda ? $('.nda-download-link').attr('href', document.result.unsigned_nda.doc) : $('#nda-upload').hide();
//       }
