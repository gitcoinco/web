# Widgets

## Why

These widgets will help you advertise your support for Gitcoin bounties.

We support both *image* widgets (see below) and dynamically resizing *javascript* widgets (see directly below)

## Dynamic Javascript Widget

### Preview

The JS image is responsive.  Here are some screenshots of it:

<img src='imgs/example.png' width="300">
<img src='imgs/example2.png' width="300">

### Example

[Click here to see an example JSFiddle widget](https://jsfiddle.net/j73nqdg2/)

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
  data-orginisation="MetaMask"
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
  orginisation: 'MetaMask',
  repository: 'metamask-extension',
  selector: '.gitcoin-widget',
});
```

## Static Image Widget

### Example

```html
<a href="https://gitcoin.co/explorer?q=gitcoinco">
    <img src="https://gitcoin.co/funding/embed?repo=https://github.com/gitcoinco/web">
</a>
```

### Results

Repos that have this widget can expect to see 35% more interest in their repo's bounties

### Code

Place the following code into your repo readme:
```
<a href="https://gitcoin.co/explorer?q=YOUR_REPO_NAME">
    <img src="https://gitcoin.co/funding/embed?repo=https://github.com/YOUR_ORG_NAME/YOUR_REPO_NAME">
</a>
```

Make sure to replace the `YOUR_ORG_NAME` and `YOUR_REPO_NAME` text with your org and repo names!

Example:

```html
<a href="https://gitcoin.co/explorer?q=gitcoinco">
    <img src="https://gitcoin.co/funding/embed?repo=https://github.com/gitcoinco/web">
</a>
```

### More Examples

<a href="https://gitcoin.co/explorer?q=metamask">
    <img src="https://gitcoin.co/funding/embed?repo=https://github.com/MetaMask/metamask-extension/issues/2350">
</a>

<a href="https://gitcoin.co/explorer?q=web3">
    <img src="https://gitcoin.co/funding/embed?repo=https://github.com/ethereum/web3.py">
</a>

<a href="https://gitcoin.co/explorer?q=MARKETProtocol">
    <img src="https://gitcoin.co/funding/embed?repo=https://github.com/MARKETProtocol/MARKETProtocol">
</a>
