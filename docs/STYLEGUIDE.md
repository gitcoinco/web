# Styleguide

This is a WIP in order to standardize and unify the look and feel of the product
All Gitcoin UI styled classes are prefixed with `g-` to distincly identify them.

_Note: All pages within gitcoin are expected to reuse these classes as applicable as opposed to reinventing the wheel._

## Typography

- `g-font-muli` (Muli - Default)
- `g-font-futura` (Futura - For Marketing Pages)

The font variations used in Gitcoin can be found in
[typography.css](https://github.com/gitcoinco/web/blob/master/app/assets/v2/css/lib/typography.css)

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