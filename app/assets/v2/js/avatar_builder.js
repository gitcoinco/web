let openSection;
const options = {
  SkinTone: '{{ defaultTone }}',
  HairColor: '{{ defaultHairColor }}',
  Accessories: new Set()
};

function changeSection(section) {
  openSection = openSection || section;

  [ '#title-', '#nav-', '#options-' ].forEach(function(prefix) {
    $(prefix + openSection).removeClass('open');
    $(prefix + section).addClass('open');
  });

  openSection = section;
}

function changeColor(className, color) {
  $(className).each(function(idx, elem) {
    if (elem.classList.contains('empty')) {
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
  const elem = $('#preview-' + option);

  if (path) {
    elem.attr('src', path).removeClass('empty');
  } else {
    elem.addClass('empty');
  }
}

function setOption(option, value, target) {
  $('#nav-' + option).addClass('complete');
  switch (option) {
    case 'Face':
    case 'Eyes':
    case 'Nose':
    case 'Ears':
    case 'Mouth':
    case 'Clothing':
      changeImage(option, $(target).children()[0].src);
      options[option] = value;
      break;
    case 'Accessories':
      // TODO: this doesn't clear earringback when only front is used
      var valueArray = JSON.parse(value.replace(/'/g, '"'));

      valueArray.forEach((value, idx) => {
        const category = value.split('-')[0];

        changeImage(category, $(target).children()[idx].src);
      });
      if (options.Accessories.size < 3) {
        // options.Accessories.add(value);
      }
      break;
    case 'HairStyle':
      changeImage('HairShort', $(target).children()[1].src);
      changeImage('HairLong', $(target).children()[0].src);
      options[option] = value.slice(1, value.length - 2).split(', ');
      break;
    case 'FacialHair':
      var layer = value.split('-')[0];

      changeImage(layer, $(target).children()[0].src);
      break;
    case 'HairColor':
      changeColor('.hair-color-dependent', value);
      options[option] = value;
      break;
    case 'SkinTone':
      changeColor('.tone-dependent', value);
      options[option] = value;
      break;
    case 'Background':
      $('#avatar-preview').css('background-color', '#' + value);
      options[option] = value;
      break;
  }
}

changeSection('Face');
