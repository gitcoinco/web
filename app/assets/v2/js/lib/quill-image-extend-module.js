"use strict";

/**
* https://github.com/NextBoy/quill-image-extend-module
*@description Observer Mode Globally monitor rich text editor
*/

const QuillWatch = {
  watcher: {},
  // Register editor information
  active: null,
  // Currently triggered editor
  on: function (imageExtendId, ImageExtend) {
    // Register to use ImageEXtend's editor
    if (!this.watcher[imageExtendId]) {
      this.watcher[imageExtendId] = ImageExtend;
    }
  },
  emit: function (activeId, type = 1) {
    // Event firing trigger
    this.active = this.watcher[activeId];

    if (type === 1) {
      imgHandler();
    }
  }
};
/**
* @description Picture function expansion: add upload, drag and copy
*/

class ImageExtend {
  /**
  * @param quill {Quill} Rich text example
  * @param config {Object} options
  * config  keys: action, headers, editForm start end error  size response
  */
  constructor(quill, config = {}) {
    this.id = Math.random();
    this.quill = quill;
    this.quill.id = this.id;
    this.config = config;
    this.file = ''; // Image to upload

    this.imgURL = ''; // The map's address

    quill.root.addEventListener('paste', this.pasteHandle.bind(this), false);
    quill.root.addEventListener('drop', this.dropHandle.bind(this), false);
    quill.root.addEventListener('dropover', function (e) {
      e.preventDefault();
    }, false);
    this.cursorIndex = 0;
    QuillWatch.on(this.id, this);
  }
  /**
  * @description Paste
  * @param e
  */

  pasteHandle(e) {
    // e.preventDefault()
    QuillWatch.emit(this.quill.id, 0);
    let clipboardData = e.clipboardData;
    let i = 0;
    let items, item, types;

    if (clipboardData) {
      items = clipboardData.items;

      if (!items) {
        return;
      }

      item = items[0];
      types = clipboardData.types || [];

      for (; i < types.length; i++) {
        if (types[i] === 'Files') {
          item = items[i];
          break;
        }
      }

      if (item && item.kind === 'file' && item.type.match(/^image\//i)) {
      this.file = item.getAsFile();
      let self = this; // If the picture is limited in size

      if (self.config.size && self.file.size >= self.config.size * 1024 * 1024) {
        if (self.config.sizeError) {
          self.config.sizeError();
        }

        return;
      }

      if (this.config.action) {// this.uploadImg()
      } else {// this.toBase64()
      }
    }
  }
}
/**
* Drag
* @param e
*/

dropHandle(e) {
  QuillWatch.emit(this.quill.id, 0);
  const self = this;
  e.preventDefault(); // If the picture is limited in size

  if (self.config.size && self.file.size >= self.config.size * 1024 * 1024) {
    if (self.config.sizeError) {
      self.config.sizeError();
    }

    return;
  }

  self.file = e.dataTransfer.files[0]; // Get the first uploaded file object

  if (this.config.action) {
    self.uploadImg();
  } else {
    self.toBase64();
  }
}
/**
* @description Convert the picture to base64
*/

toBase64() {
  const self = this;
  const reader = new FileReader();

  reader.onload = e => {
    // Return base64
    self.imgURL = e.target.result;
    self.insertImg();
  };

  reader.readAsDataURL(self.file);
}
/**
* @description Upload picture to server
*/

uploadImg() {
  const self = this;
  let quillLoading = self.quillLoading;
  let config = self.config; // Construct form

  let formData = new FormData();
  formData.append(config.name, self.file); // Custom edit form

  if (config.editForm) {
    config.editForm(formData);
  } // Create ajax request


  let xhr = new XMLHttpRequest();
  xhr.open('post', config.action, true); // If there is a request header

  if (config.headers) {
    config.headers(xhr);
  }

  if (config.change) {
    config.change(xhr, formData);
  }

  xhr.onreadystatechange = function () {
    if (xhr.readyState === 4) {
      if (xhr.status === 200) {
        //success
        let res = JSON.parse(xhr.responseText);
        self.imgURL = config.response(res);
        QuillWatch.active.uploadSuccess();
        self.insertImg();

        if (self.config.success) {
          self.config.success();
        }
      } else {
        //error
        if (self.config.error) {
          self.config.error();
        }

        QuillWatch.active.uploadError();
      }
    }
  }; // Start uploading data

  xhr.upload.onloadstart = function (e) {
    QuillWatch.active.uploading(); // let length = (self.quill.getSelection() || {}).index || self.quill.getLength()
    // self.quill.insertText(length, '[uploading...]', { 'color': 'red'}, true)

    if (config.start) {
      config.start();
    }
  }; // Upload process

  xhr.upload.onprogress = function (e) {
    let complete = (e.loaded / e.total * 100 | 0) + '%';
    QuillWatch.active.progress(complete);
  }; // It will be triggered when a network exception occurs, if the process of uploading data has not ended


  xhr.upload.onerror = function (e) {
    QuillWatch.active.uploadError();

    if (config.error) {
      config.error();
    }
  }; // Triggered when uploading data is complete (success or failure)


  xhr.upload.onloadend = function (e) {
    if (config.end) {
      config.end();
    }
  };

  xhr.send(formData);
}
/**
* @description Insert a picture into the rich text editor
*/

insertImg() {
  const self = QuillWatch.active;
  self.quill.insertEmbed(QuillWatch.active.cursorIndex, 'image', self.imgURL);
  self.quill.update();
  self.quill.setSelection(self.cursorIndex + 1);
}
/**
* @description Show upload progress
*/

progress(pro) {
  pro = '[' + 'uploading' + pro + ']';
  QuillWatch.active.quill.root.innerHTML = QuillWatch.active.quill.root.innerHTML.replace(/\[uploading.*?\]/, pro);
}
/**
* Start upload
*/

uploading() {
  let length = (QuillWatch.active.quill.getSelection() || {}).index || QuillWatch.active.quill.getLength();
  QuillWatch.active.cursorIndex = length;
  QuillWatch.active.quill.insertText(QuillWatch.active.cursorIndex, '[uploading...]', {
    'color': 'red'
  }, true);
}
/**
* upload failed
*/

uploadError() {
  QuillWatch.active.quill.root.innerHTML = QuillWatch.active.quill.root.innerHTML.replace(/\[uploading.*?\]/, '[upload error]');
}

uploadSuccess() {
  QuillWatch.active.quill.root.innerHTML = QuillWatch.active.quill.root.innerHTML.replace(/\[uploading.*?\]/, '');
}

}
/**
* @description Click on the picture to upload
*/

function imgHandler() {
  let fileInput = document.querySelector('.quill-image-input');

  if (fileInput === null) {
    fileInput = document.createElement('input');
    fileInput.setAttribute('type', 'file');
    fileInput.classList.add('quill-image-input');
    fileInput.style.display = 'none'; // Monitor selection file

    fileInput.addEventListener('change', function () {
      let self = QuillWatch.active;
      self.file = fileInput.files[0];
      fileInput.value = ''; // If the picture is limited in size

      if (self.config.size && self.file.size >= self.config.size * 1024 * 1024) {
        if (self.config.sizeError) {
          self.config.sizeError();
        }

        return;
      }

      if (self.config.action) {
        self.uploadImg();
      } else {
        self.toBase64();
      }
    });
    document.body.appendChild(fileInput);
  }

  fileInput.click();
}
/**
*@description All toolbars
*/


const container = [
  ['bold', 'italic', 'underline', 'strike'],
  ['blockquote', 'code-block'],
  [
    {'header': 1},
    {'header': 2}
  ],
  [
    {'list': 'ordered'},
    {'list': 'bullet'}
  ],
  [
    {'script': 'sub'},
    {'script': 'super'}
  ],
  [
    {'indent': '-1'},
    {'indent': '+1'}
  ],
  [
    {'direction': 'rtl'}
  ],
  [
    {
      'size': ['small', false, 'large', 'huge']
    }
  ],
  [
    {
      'header': [1, 2, 3, 4, 5, 6, false]
    }
  ],
  [
    {'color': []},
    {'background': []}
  ],
  [
    {'font': []}
  ],
  [
    {'align': []}
  ],
  ['clean'],
  ['link', 'image', 'video']
];
