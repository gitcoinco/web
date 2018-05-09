let openSection;
const layers = [
  'HatLong', 'HairLong', 'EarringBack', 'Clothing',
  'Ears', 'Head', 'HairShort', 'Earring', 'Beard', 'HatShort',
  'Mustache', 'Mouth', 'Nose', 'Eyes', 'Glasses'
];
const requiredLayers = [ 'Clothing', 'Ears', 'Head', 'Mouth', 'Nose', 'Eyes', 'Background' ];
const colorOptions = {
  SkinTone: [ 'F8D5C2', 'D8BF82', 'D2946B', 'AE7242', '88563B', '715031', '593D26', '3F2918' ],
  HairColor: [
    '000000', '4E3521', '8C3B28', 'B28E28', 'F4EA6E', 'F0E6FF',
    '4D22D2', '8E2ABE', '3596EC', '0ECF7C'
  ],
  Background: [
    '25E899', '9AB730', '00A55E', '3FCDFF',
    '3E00FF', '8E2ABE', 'D0021B', 'F9006C',
    'FFCE08', 'F8E71C', '15003E', 'FFFFFF'
  ],
  ClothingColor: [
    'CCCCCC', '684A23', 'FFCC3B', '4242F4', '43B9F9', 'F48914'
  ]
};
const sectionPalettes = {
  Head: 'SkinTone', Eyes: 'SkinTone', Ears: 'SkinTone', Nose: 'SkinTone', Mouth: 'SkinTone',
  HairStyle: 'HairColor', HairShort: 'HairColor', HairLong: 'HairColor',
  FacialHair: 'HairColor', Beard: 'HairColor', Mustache: 'HairColor',
  Clothing: 'ClothingColor'
};

layers.forEach(name => {
  options[name] = null;
});

function changeColorPicker(section) {
  const palette = sectionPalettes[section];
  const colorPicker = $('#color-picker').empty();

  if (palette) {
    colorOptions[palette].forEach(c => {
      colorPicker.append($(`<button
      id="picker-${c}" type="button"
      class="options-Background__option p-0 ${(options[palette] === c) ? 'selected' : ''}"
      style="background-color: #${c}" onclick="changeColor('${palette}', '${c}')" />
      `));
    });
  }
}

function changeSection(section) {
  openSection = openSection || section;

  [ '#title-', '#nav-', '#options-' ].forEach(function(prefix) {
    $(prefix + openSection).removeClass('open');
    $(prefix + section).addClass('open');
  });

  openSection = section;
  changeColorPicker(section);
}

function changeColor(palette, color) {
  $(`#picker-${options[palette]}`).removeClass('selected');
  options[palette] = color;
  $(`#picker-${options[palette]}`).addClass('selected');

  $(`.${palette}-dependent`).each(function(idx, elem) {
    const background = $(elem).css('background-image');
    const url = background.split('"')[1];
    const pathSegments = url.split('/');
    const filename = pathSegments.pop();
    const baseOption = filename.split('-').slice(0, -1).join('-');

    pathSegments.push(baseOption + '-' + color + '.svg');
    $(elem).css('background-image', `url(${pathSegments.join('/')})`);
  });
}

function changeImage(option, path) {
  if (options[option] !== null) { // option was previously selected
    const elem = $('#preview-' + option);

    if (path) {
      elem.css('background-image', `url(/static/${path})`);
      options[option] = path;
    } else {
      elem.remove();
      options[option] = null;
    }
  } else if (path) { // option was previously blank
    const newEl = $.parseHTML(`<div id="preview-${option}"
    alt="${option} Preview"
    style="z-index: ${layers.indexOf(option)}; background-image: url(/static/${path})"
    class="preview-section ${
  (sectionPalettes.hasOwnProperty(option) &&
    [ 'Eyes', 'Mouth', 'Nose' ].indexOf(option) < 0) ?
    `${sectionPalettes[option]}-dependent` : ''
}" ></div>`);

    $('#avatar-preview').append(newEl);
    options[option] = path;
  }
}

function setOption(option, value, target) {
  const section = $(`#options-${option}`);
  let deselectingFlag = true;

  $('#nav-' + option).addClass('complete');
  // Removing an optional layer
  if (target.classList.contains('selected') && requiredLayers.indexOf(option) < 0) {
    $(target).removeClass('selected');
    deselectingFlag = null;
  }
  // Clear selected class for categories that allow only one option
  if (option !== 'Accessories' && option !== 'FacialHair') {
    $('.selected', section).removeClass('selected');
  }

  switch (option) {
    case 'Head':
    case 'Eyes':
    case 'Nose':
    case 'Ears':
    case 'Mouth':
    case 'Clothing':
      changeImage(option, deselectingFlag && $(target).children().data('path'));
      break;
    case 'Accessories':
      // TODO: this doesn't clear earringback when only front is used
      var valueArray = JSON.parse(value.replace(/'/g, '"'));

      valueArray.forEach((value, idx) => {
        const category = value.split('-')[0];
        const optionDiv = $(target).children()[idx];

        $(`button[id*="${category}"]`, section).removeClass('selected');
        changeImage(category, deselectingFlag && $(optionDiv).data('path'));
      });
      break;
    case 'HairStyle':
      [ 'HairLong', 'HairShort' ].forEach((layer, idx) => {
        let found = false;

        $(target).children().each((elemIdx, elem) => {
          if (idx === parseInt(elem.classList[0])) {
            changeImage(layer, deselectingFlag && $(elem).data('path'));
            found = true;
          }
        });

        if (!found) {
          changeImage(layer);
        }
      });
      break;
    case 'FacialHair':
      var layer = value.split('-')[0];
      var optionDiv = $(target).children()[0];

      $(`button[id*="${layer}"]`, section).removeClass('selected');
      changeImage(layer, deselectingFlag && $(optionDiv).data('path'));
      break;
    case 'Background':
      $('#avatar-preview').css('background-color', '#' + value);
      options['Background'] = value;
      break;
  }

  // If target is newly selected, mark it
  if (deselectingFlag) {
    $(target).addClass('selected');
  }

  // Check for completion
  const complete = requiredLayers.
    reduce((complete, name) => !!options[name] && complete, true);

  if (complete) {
    $('#complete-notification').removeClass('d-none');
    $('#save-button').removeAttr('disabled');
  }
}

function saveAvatar() {
  fetch('/set_avatar', {
    method: 'POST',
    body: JSON.stringify(options)
  });
}

changeSection('Head');
