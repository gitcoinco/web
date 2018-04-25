let openSection;
const layers = [
  'HatLong', 'HairLong', 'EarringBack', 'Clothing',
  'Ears', 'Face', 'HairShort', 'HatShort', 'Earring', 'Beard',
  'Mustache', 'Mouth', 'Nose', 'Eyes', 'Glasses'
];
const requiredLayers = [ 'Clothing', 'Ears', 'Face', 'Mouth', 'Nose', 'Eyes' ];
const options = {};
const colorOptions = {
  SkinTone: [ 'F8D5C2', 'D8BF82', 'D2946B', 'AE7242', '88563B', '715031', '593D26', '3F2918' ],
  HairColor: [ '000000', '4E3521', '8C3B28', 'B28E28', 'F4EA6E', 'F0E6FF' ],
  Background: [
    '25E899', '9AB730', '00A55E', '3FCDFF',
    '3E00FF', '8E2ABE', 'D0021B', 'F9006C',
    'FFCE08', 'F8E71C', '15003E', 'FFFFFF'
  ]
};

layers.forEach(name => {
  options[name] = null;
});

function changeColorPicker(section) {
  let colorPallete;
  const colorPicker = $('#color-picker').empty();

  if ([ 'Face', 'Eyes', 'Nose', 'Mouth', 'Ears' ].indexOf(section) >= 0) {
    colorPallete = 'SkinTone';
  } else if ([ 'HairStyle', 'FacialHair' ].indexOf(section) >= 0) {
    colorPallete = 'HairColor';
  } else if (section === 'Background') {
    colorPallete = 'Background';
  } else {
    return;
  }

  colorOptions[colorPallete].forEach(c => {
    colorPicker.append($(`<button class="options-Background__option pa-0"
    style="background-color: #${c}" onclick="setOption('${colorPallete}', '${c}')" />
    `));
  });
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

function changeColor(className, color) {
  $(className).each(function(idx, elem) {
    if (elem.classList.contains('d-none')) {
      return;
    }
    const pathSegments = elem.src.split('/');
    const filename = pathSegments.pop();
    const baseOption = filename.split('-').slice(0, -1).join('-');

    pathSegments.push(baseOption + '-' + color + '.svg');
    elem.src = pathSegments.join('/');
  });
}

function changeImage(option, path) {
  if (options[option] !== null) { // option was previously selected
    const elem = $('#preview-' + option);

    if (path) {
      elem.attr('src', path);
      options[option] = path;
    } else {
      elem.remove();
      options[option] = null;
    }
  } else if (path) { // option was previously blank
    const newEl = $.parseHTML(`<img id="preview-${option}"
    src="${path}"
    alt="${option} Preview"
    style="z-index: ${layers.indexOf(option)}"
    class="preview-section ${
  ([ 'Face', 'Ears', 'Clothing' ].indexOf(option) >= 0) ?
    'tone-dependent' : ''
}${
  ([ 'HairShort', 'HairLong', 'Mustache', 'Beard' ].indexOf(option) >= 0) ?
    'hair-color-dependent' : ''
}" />`);

    $('#avatar-preview').append(newEl);
    options[option] = path;
  }
  const complete = requiredLayers.
    reduce((complete, name) => !!options[name] && complete, true);

  if (complete) {
    $('#complete-notification').removeClass('d-none');
  }
}

function setOption(option, value, target) {
  console.log(target);
  $('#nav-' + option).addClass('complete');
  switch (option) {
    case 'Face':
    case 'Eyes':
    case 'Nose':
    case 'Ears':
    case 'Mouth':
    case 'Clothing':
      changeImage(option, $(target).children()[0].src);
      break;
    case 'Accessories':
      // TODO: this doesn't clear earringback when only front is used
      var valueArray = JSON.parse(value.replace(/'/g, '"'));

      valueArray.forEach((value, idx) => {
        const category = value.split('-')[0];

        changeImage(category, $(target).children()[idx].src);
      });
      break;
    case 'HairStyle':
      changeImage('HairShort', $(target).children()[1].src);
      changeImage('HairLong', $(target).children()[0].src);
      break;
    case 'FacialHair':
      var layer = value.split('-')[0];

      changeImage(layer, $(target).children()[0].src);
      break;
    case 'HairColor':
      changeColor('.hair-color-dependent', value);
      break;
    case 'SkinTone':
      changeColor('.tone-dependent', value);
      break;
    case 'Background':
      $('#avatar-preview').css('background-color', '#' + value);
      options['Background'] = value;
      break;
  }
}

changeSection('Face');
