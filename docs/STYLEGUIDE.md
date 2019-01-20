# Styleguide

This is a WIP in order to standardize and unify the look and feel of the product
All Gitcoin UI styled classes are prefixed with `g-` to distincly identify them.

## Typography

- `g-font-muli` (Muli - Default)
- `g-font-futura` (Futura - For Marketing Pages)

The font variations used in Gitcoin can be found in
[typography.css](https://github.com/gitcoinco/web/blob/master/app/assets/v2/css/lib/typography.css)

## Forms

### Mutiselect (using select2)

_usage_
```
<div class="g-multiselect">
    <select class="js-select2" multiple>
    </select>
</div>
```

The form styling used in Gitcoin can be found in
[select.css](https://github.com/gitcoinco/web/blob/master/app/assets/v2/css/forms/select.css)

_Note: All pages within gitcoin are expected to reuse these classes as applicable as opposed to declaring the `font` within the templates `css` file._
