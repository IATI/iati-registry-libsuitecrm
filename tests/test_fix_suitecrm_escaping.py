import pytest

from libsuitecrm import SuiteCRM


@pytest.mark.parametrize("input,expected", [
    [{"str": 'SuiteCRM mishandles: &lt;, &gt;, &#39;, &#039;, &quot;'},
     {"str": 'SuiteCRM mishandles: <, >, \', \', "'}],
    [['SuiteCRM mishandles: &lt;, &gt;, &#39;, &#039;, &quot;'], ['SuiteCRM mishandles: <, >, \', \', "']],
    [['SuiteCRM mishandles: &lt;, &gt;, &#39;, &#039;, &quot;',
      'SuiteCRM mishandles: &lt;, &gt;, &#39;, &#039;, &quot;'],
     ['SuiteCRM mishandles: <, >, \', \', "', 'SuiteCRM mishandles: <, >, \', \', "']],
    [{"str": 'SuiteCRM mishandles: &lt;, &gt;, &#39;, &#039;, &quot;',
      "sublist": ['SuiteCRM mishandles: &lt;, &gt;, &#39;, &#039;, &quot;']},
      {"str": 'SuiteCRM mishandles: <, >, \', \', "',
       "sublist": ['SuiteCRM mishandles: <, >, \', \', "']}],
    [{"str": 'SuiteCRM mishandles: &lt;, &gt;, &#39;, &#039;, &quot;',
      "subdict": {"str": 'SuiteCRM mishandles: &lt;, &gt;, &#39;, &#039;, &quot;'}},
      {"str": 'SuiteCRM mishandles: <, >, \', \', "',
       "subdict": {"str": 'SuiteCRM mishandles: <, >, \', \', "'}}],
])
def test_fix_escaped_characters(input, expected):

    crm = SuiteCRM(api_base_url="dummy_url", client_id="dummy", client_secret="dummy", secure=False)

    crm._fix_escaped_chars_in_response(input)

    assert input == expected
