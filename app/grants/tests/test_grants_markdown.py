import markdown

from grants.markdown import bDjangoUrlExtension, get_site_domain


md = markdown.Markdown(extensions=[DjangoUrlExtension()])

html = md.convert("[Help](mailto:support@gitcoin.co?subject=I need help!)")
assert html == '<p><a href="mailto:support@gitcoin.co?subject=I need help!">Help</a></p>'

html = md.convert("[Help](mailto:?subject=I need help!)")
assert html == '<p><a href="mailto:?subject=I need help!">Help</a></p>'

try:
    md.convert("[Help](mailto:invalidemail?subject=I need help!)")
except InvalidMarkdown as e:
    assert e.error == 'Invalid email address'
    assert e.value == 'invalidemail'
else:
    assert False, 'Expected "InvalidMarkdown" error'


html = md.convert("Go back to [homepage](home)")
assert html == '<p>Go back to <a href="/">homepage</a></p>'

html = md.convert("Go back to [homepage](home#offers)")
assert html == '<p>Go back to <a href="/#offers">homepage</a></p>'

html = md.convert("Go back to [homepage](home?foo=bar)")
assert html == '<p>Go back to <a href="/?foo=bar">homepage</a></p>'

html = md.convert("Go back to [homepage](home?foo=bar#offers)")
assert html == '<p>Go back to <a href="/?foo=bar#offers">homepage</a></p>'


try:
    md.convert(f'[link](https://{get_site_domain()}/foo)')
except InvalidMarkdown as e:
    assert e.value == f'https://{get_site_domain()}/foo'
    assert "We couldn't find a match to this URL." in e.error
else:
    assert False, 'Expected "InvalidMarkdown" error'

try:
    md.convert(f'[link](https://{get_site_domain()}/)')
except InvalidMarkdown as e:
    assert e.value == f'https://{get_site_domain()}/'
    assert 'Try using the url name' in e.error
else:
    assert False, 'Expected "InvalidMarkdown" error'

html = md.convert('[link](https://gitcoin.co)')
assert html == '<p><a href="https://gitcoin.co">link</a></p>'


try:
    md.convert('[link](external.com)')
except InvalidMarkdown as e:
    assert e.value == 'external.com'
    assert 'Must provide absolute url' in e.error
else:
    assert False, 'Expected "InvalidMarkdown" error'
