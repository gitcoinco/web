# Gitcoin SDK

## Dynamic Widget

### Example

Step 1: Include the JavaScript SDK on your page once, ideally right after the opening body tag.

```html
<div id="gc-root"></div>
<script>(function(d, s, id) {
  var js, gjs = d.getElementsByTagName(s)[0];
  if (d.getElementById(id)) return;
  js = d.createElement(s); js.id = id;
  js.src = "https://unpkg.com/gitcoin-sdk";
  gjs.parentNode.insertBefore(js, gjs);
}(document, 'script', 'gitcoin-jssdk'));</script>
```

Step 2: Place this code wherever you want the plugin to appear on your page.

```html
<div class="gitcoin-widget"
  data-limit="2"
  data-order-by="-expires_date"
  data-organization="MetaMask"
  data-repository="metamask-extension"
></div>
```

### Autoloading

Importing the SDK into your application will attempt to autoload the widget by searching for '.gitcoin-widget' selectors

```javascript
import 'gitcoin-sdk';
```
or
```javascript
require('gitcoin-sdk');
```

### Programmatically

You can also use the Widget programmatically.

```javascript
import { Widget } from 'gitcoin-sdk';
```
or
```javascript
const { Widget } = require('gitcoin-sdk');
```

Widget can be instantiated by passing a selector option, or an element reference.

```javascript
new Widget({
  limit: 10,
  orderBy: '-expires_date',
  organization: 'MetaMask',
  repository: 'metamask-extension',
  selector: '.gitcoin-widget',
});
```
