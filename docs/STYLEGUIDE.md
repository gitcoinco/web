# Styleguide

This is a WIP in order to standardize and unify the look and feel of the product
All Gitcoin UI styled classes are prefixed with `g-` to distincly identify them.

_Note: All pages within gitcoin are expected to reuse these classes as applicable as opposed to reinventing the wheel._

## Typography

- `g-font-muli` (Muli - Default)
- `g-font-futura` (Futura - For Marketing Pages)

The font variations used in Gitcoin can be found in
[typography.css](https://github.com/gitcoinco/web/blob/master/app/assets/v2/css/lib/typography.css)

_Note: All pages within gitcoin are expected to reuse these classes as applicable as opposed to declaring the `font` within the templates `css` file._

## Forms

### Mutiselect (using select2)

_usage_
```
<div class="form__select2 g-multiselect">
    <select class="js-select2" multiple>
    </select>
</div>
```

The Multiselect styling used in Gitcoin can be found in
[select.css](https://github.com/gitcoinco/web/blob/master/app/assets/v2/css/forms/select.css)

### Copy to clipboard

_usage_


```
<script src="{% static 'v2/js/clipboard.js' %}"></script>
```

```
<textarea id="matchid">This text will be copied</textarea>
<button data-copyclipboard="#matchid">Copy Text</button>
```
_usage with class_
```

<input type="text" class="matchclass" value="This text will be copied">
<button data-copyclipboard=".matchclass">Copy Text</button>
```
_Note: You can use it with `textarea` or `input` elements._

### Slider

_usage_
```
<label class="g-switch">
    <input id="package-period" type="checkbox">
    <span class="slider"></span>
</label>
```

The Slider styling used in Gitcoin can be found in
[slider.css](https://github.com/gitcoinco/web/blob/master/app/assets/v2/css/lib/slider.css)


## Animations

### FadeIn

Container has a fade in animation when it becomes into viewport.

_values_

`data-fade-direction`: `left` | `mid` | `right` _(defaut: `mid`)_
`data-fade-duration`: `Number` _(default: `1500`)_

_usage_

```<div class="g-fadein" data-fade-duration=1000 data-fade-direction="mid">```