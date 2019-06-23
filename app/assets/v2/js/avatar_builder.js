let openSection;
const layers = [
  'Wallpaper',
  'HatLong', 'HairLong', 'EarringBack', 'Clothing',
  'Ears', 'Head', 'Makeup', 'HairShort', 'Earring', 'Beard', 'HatShort',
  'Mustache', 'Mouth', 'Nose', 'Eyes', 'Glasses', 'Masks', 'Extras'
];
const requiredLayers = [ 'Clothing', 'Ears', 'Head', 'Mouth', 'Nose', 'Eyes', 'Background' ];
const colorOptions = {
  SkinTone: [ 'FFFFF6', 'FEF7EB', 'F8D5C2', 'EEE3C1', 'D8BF82', 'D2946B', 'AE7242', '88563B', '715031', '593D26' ],
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
const parentLayers = {
  HairShort: 'HairStyle', HairLong: 'HairStyle', Beard: 'FacialHair', Mustache: 'FacialHair',
  EarringBack: 'Accessories', Earring: 'Accessories', HatLong: 'Accessories', HatShort: 'Accessories',
  Glasses: 'Accessories', Masks: 'Accessories', Extras: 'Accessories'
};

var localStorage;

try {
  localStorage = window.localStorage;
} catch (e) {
  localStorage = {};
}

layers.concat('Background').forEach(name => {
  options[name] = null;
  if (localStorage[name] && localStorage[name] !== 'null' && localStorage[name + 'Id'] && localStorage[name + 'Id'] !== 'null') {
    let optionName = name;

    if (parentLayers[optionName]) {
      optionName = parentLayers[optionName];
    }
    if (name === 'EarringBack') {
      return true;
    }
    const targetId = localStorage[name + 'Id'].replace(/(['"])/g, '\\$1');
    const color = getColorFromPath(localStorage[name], optionName);
    let palette = null;

    $($("[id='" + targetId + "']")).trigger('click');
    if ($('#preview-' + optionName).attr('class')) {
      palette = $('#preview-' + optionName).attr('class').replace('preview-section ', '').replace('-dependent', '');
    }

    if (color && palette) {
      changeColor(palette, color);
    }
    options[name] = localStorage[name];
  }
});

function getIdFromPath(path, option) {
  let optionChoice = '';

  if (option === 'FacialHair' || option === 'Accessories') {
    optionChoice = path.split('.')[0].split('/').slice(-1)[0].split('-')[1];
  } else {
    optionChoice = path.split('.')[0].split('/').slice(-1)[0].split('-')[0];
  }

  return '#avatar-option-' + option + '-' + optionChoice;
}

function getColorFromPath(path, option) {
  let color = '';

  // filename without path and extension
  const basename = path.split('.').slice(-2)[0].split('/').slice(-1)[0];

  if (option === 'FacialHair' || option === 'Accessories') {
    color = basename.split('-')[2];
  } else {
    color = basename.split('-')[1];
  }

  return color;
}

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

function getStaticPath(url, color) {
  const pathSegments = url.split('/');
  const filename = pathSegments.pop();
  const baseOption = filename.split('-').slice(0, -1).join('-');

  pathSegments.push(baseOption + '-' + color + '.svg');
  return pathSegments.join('/');
}

function changeColor(palette, color) {
  $(`#picker-${options[palette]}`).removeClass('selected');
  options[palette] = color;
  $(`#picker-${options[palette]}`).addClass('selected');

  $(`.${palette}-dependent`).each(function(idx, elem) {
    const background = $(elem).css('background-image');
    const url = background.split('"')[1];
    const backgroundNewPath = getStaticPath(url, color);

    $(elem).css('background-image', `url(${backgroundNewPath})`);

    if ($(elem).data('path')) {
      const pathData = $(elem).data('path');
      const pathNewData = getStaticPath(pathData, color);

      $(elem).data('path', pathNewData);
      if ($(elem).parent().hasClass('selected')) {
        $(elem).parent().trigger('click').trigger('click');
      }
    }
  });
}

function changeImage(option, path) {
  if (options[option] !== null) { // option was previously selected
    const elem = $('#preview-' + option);

    if (path) {
      elem.css('background-image', `url(${path})`);
      options[option] = path;
      localStorage[option] = path;
    } else {
      elem.remove();
      options[option] = null;
      localStorage[option] = null;
    }
  } else if (path) { // option was previously blank
    const newEl = $.parseHTML(`<div id="preview-${option}"
    alt="${option} Preview"
    style="z-index: ${layers.indexOf(option)}; background-image: url(${path})"
    class="preview-section ${
  (sectionPalettes.hasOwnProperty(option) &&
    [ 'Eyes', 'Mouth', 'Nose' ].indexOf(option) < 0) ?
    `${sectionPalettes[option]}-dependent` : ''
}" ></div>`);

    $('#avatar-preview').append(newEl);
    options[option] = path;
    localStorage[option] = path;
  }
}

function purchaseOption(option, value, target) {
  if (document.web3network == 'mainnet') {
    _alert('You will now be prompted via Metamask to purchase this avatar item.', 'info');
    var ele = $('#' + target.id.replace("'", '').replace("'", ''));
    var cost = null;

    if (ele.data('cost')) {
      cost = ele.data('cost');
    } else {
      cost = ele.find('div').data('cost');
    }
    var cost_eth = parseFloat(cost.replace('ETH', ''));
    var cost_wei = web3.toWei(cost_eth);

    to_address = '0x00De4B13153673BCAE2616b67bf822500d325Fc3'; // TODO: make dynamic
    indicateMetamaskPopup();
    web3.eth.sendTransaction({
      'from': web3.eth.coinbase,
      'to': to_address,
      'value': cost_wei
    }, function(error, result) {
      indicateMetamaskPopup(true);
      if (error) {
        _alert('There was an error.', 'error');
        return;
      }
      showBusyOverlay();
      _alert('Waiting for tx to mine...', 'info');
      callFunctionWhenTransactionMined(result, function() {
        var request_url = '/revenue/attestations/new';
        var txid = result;
        var data = {
          'txid': txid,
          'amount': cost_eth,
          'network': document.web3network,
          'from_address': web3.eth.coinbase,
          'to_address': to_address,
          'type': 'avatar',
          'option': option,
          'value': value
        };

        $.post(request_url, data).then(function(result) {
          hideBusyOverlay();
          _alert('Success ✅ Loading your purchase now.', 'success');
          setTimeout(function() {
            location.reload();
          });
        });
      });
    });
  } else if (document.web3network == 'locked') {
    if (document.ready) {
      _alert('This is a premium avatar item.  In order to purchase it, please unlock your web3 wallet.', 'info');
    }
  } else if (document.ready) {
    _alert('This is a premium avatar item.  In order to purchase it, please switch to the mainnet.', 'info');
  }
  return;
}

function setOption(option, value, target) {
  if (target.classList.contains('not_paid')) {
    return purchaseOption(option, value, target);
  }
  return setOptionHelper(option, value, target);
}

function setOptionHelper(option, value, target) {

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
    case 'Makeup':
    case 'Eyes':
    case 'Nose':
    case 'Ears':
    case 'Mouth':
    case 'Wallpaper':
    case 'Clothing':
      localStorage[option + 'Id'] = $(target).attr('id');
      changeImage(option, deselectingFlag && $(target).children().data('path'));
      break;
    case 'Accessories':
      // TODO: this doesn't clear earringback when only front is used
      var valueArray = JSON.parse(value.replace(/'/g, '"'));

      valueArray.forEach((value, idx) => {
        const category = value.split('-')[0];
        const optionDiv = $(target).children()[idx];

        $(`button[id*="${category}"]`, section).removeClass('selected');
        localStorage[category + 'Id'] = $(target).attr('id');
        changeImage(category, deselectingFlag && $(optionDiv).data('path'));
      });
      break;
    case 'HairStyle':
      [ 'HairLong', 'HairShort' ].forEach((layer, idx) => {
        let found = false;

        $(target).children().each((elemIdx, elem) => {
          if (idx === parseInt(elem.classList[0])) {
            localStorage[layer + 'Id'] = $(target).attr('id');
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
      localStorage[layer + 'Id'] = $(target).attr('id');
      changeImage(layer, deselectingFlag && $(optionDiv).data('path'));
      break;
    case 'Background':
      $('#avatar-preview').css('background-color', '#' + value);
      options['Background'] = value;
      localStorage['Background'] = value;
      localStorage['BackgroundId'] = $(target).attr('id');
      break;
  }

  // If target is newly selected, mark it
  if (deselectingFlag) {
    $(target).addClass('selected');
  }
  if ($('#options-' + option).find('.selected').length === 0) {
    $('#nav-' + option).removeClass('complete');
  }

  // Check for completion
  const complete = requiredLayers.
    reduce((complete, name) => !!options[name] && complete, true);

  if (complete) {
    $('#complete-notification').removeClass('d-none');
    $('#save-button').removeAttr('disabled');
  }
}

function setRandomColor(section) {
  let palette = sectionPalettes[section];
  let availableColors = colorOptions[palette];
  let randomChoice = Math.floor(Math.random() * availableColors.length);

  changeColor(palette, availableColors[randomChoice]);
}

function randomAvatar(sections, optionalSections) {

  // Random skin color
  setRandomColor('Head');
  // Random clothing color
  setRandomColor('Clothing');
  // Random hair color
  setRandomColor('HairStyle');

  // Random avatar components
  sections.forEach((section, idx) => {
    const paidOptions = Object.keys(section.paid_options);
    let options = section.options.filter((option) => !paidOptions.includes(option));
    let totalOpts = options.length;
    let componentName = section.name.replace(' ', '');
    let optional = optionalSections.includes(componentName) ? 0 : 1;

    randomChoice = Math.floor(Math.random() * totalOpts) + optional;

    if (randomChoice != 0) {
      let option = options[randomChoice - 1];
      let htmlComponent = null;

      switch (componentName) {
        case 'HairStyle':
          option = option.join('-');
          htmlComponent = $(`#avatar-option-${componentName}-${option}`)[0];
          setOptionHelper(componentName, option, htmlComponent);
          break;
        case 'Accessories':
          // removing previously selected accesories
          $('button[id^="avatar-option-Accessories-"].selected').each((idx, component) => {
            let id = component.id.replace('avatar-option-Accessories-', '');

            setOptionHelper(componentName, JSON.stringify([id]), component);
          });
          option.forEach((part, idx) => {
            htmlComponent = $(`#avatar-option-${componentName}-${part}`)[0];
            setOptionHelper(componentName, JSON.stringify(option), htmlComponent);
          });
          
          break;
        default:
          htmlComponent = $(`#avatar-option-${componentName}-${option}`)[0];
          setOptionHelper(componentName, option, htmlComponent);
          break;
      }
    }
  });
  
}

function saveAvatar() {
  $(document).ajaxStart(function() {
    loading_button($('#save-avatar'));
    $('#do-later').attr('disabled', 'disabled');
  });

  $(document).ajaxStop(function() {
    unloading_button($('#save-avatar'));
  });

  $('#later-button').hide();

  var request = $.ajax({
    url: '/avatar/custom/save',
    type: 'POST',
    data: JSON.stringify(options),
    dataType: 'json',
    contentType: 'application/json; charset=utf-8',
    success: function(response) {
      _alert({ message: gettext('Your Avatar Has Been Saved To your Gitcoin Profile!')}, 'success');
      changeStep(1);
    },
    error: function(response) {
      let text = gettext('Error occurred while saving. Please try again.');

      if (response.responseJSON && response.responseJSON.message) {
        text = response.responseJSON.message;
      }
      $('#later-button').show();
      _alert({ message: text}, 'error');
    }
  });
}

changeSection('Head');

$(document).ready(function() {
  document.ready = true;
});
