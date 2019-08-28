$(document).ready(function() {
  let file_name = '';

  $('body').on('click', 'img.picky', function() {
    $('.selected').removeClass('selected');
    $(this).addClass('selected');
    file_name = $(this).attr('src');

  });

  const banner = document.querySelector('.profile-banner');

  function setBanner() {
    const data = new FormData();

    data.append('banner', file_name);
    data.append(
      'csrfmiddlewaretoken',
      $('input[name="csrfmiddlewaretoken"]').attr('value')
    );
    fetch('/api/v0.1/profile/banner', {
      method: 'post',
      body: data
    }).then(response => {
      if (response.status === 200) {
        location.reload();
        _alert(
          { message: gettext('User profile banner has been updated.') },
          'success'
        );
      } else {
        _alert(
          { message: gettext('An error occured. Please try again.') },
          'error'
        );
      }
    });
  }

  function fetchSystemBanners() {
    fetch('/api/v0.1/banners', {
      method: 'GET'
    })
      .then(response => response.json())
      .then(response => {
        if (response.status === 200) {
          const content = $.parseHTML(`
            <div class="modal fade" id="bannerUpdateModal" tabindex="-1">
            <div class="modal-dialog modal-dialog-centered modal-lg">
                <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">${gettext('Select a banner')}</h5>
                    <button type="button" class="close" data-dismiss="modal" aria-label="Close">
                    <span aria-hidden="true">&times;</span>
                    </button>
                </div>
                <div class="modal-body">
                    <div class="d-flex">
                        <div class="row" id="banner-images">
                        ${response.banners
    .map(
      index =>
        `<div class="col-lg-3">
                            <img class="img-fluid picky" height="100%" src="/static/wallpapers/${index}" alt="${index}" />
                          </div>`
    )
    .join('')}
                        </div>
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button" id="use-banner" class="btn btn-sm btn-primary">${gettext(
    'Use Banner'
  )}</button>
                    <button type="button" class="btn btn-sm btn-secondary" data-dismiss="modal">${gettext(
    'Cancel'
  )}</button>
                </div>
            </div>
          </div>
          `);

          $(content).appendTo('body');
          $('#bannerUpdateModal').bootstrapModal('show');
        } else {
          _alert(
            {
              message: gettext(
                'Failed to load list of banner images. Try refreshing your browser'
              )
            },
            'error'
          );
        }
      });
  }


  $(document).on('click', '#use-banner', function() {
    setBanner();
  });

  if (banner) {
    banner.addEventListener(
      'click',
      function() {
        fetchSystemBanners();
      },
      false
    );
  }
});
