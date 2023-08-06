from urllib import request
from urllib.parse import quote as encode

def translate(text_to_translate, to_languages='auto', from_language='auto'):
  agents = {'User-Agent':"Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 1.1.4322; .NET CLR 2.0.50727; .NET CLR 3.0.04506.30)"}
  translation_locator = 'class="t0">'

  text_to_translate = text_to_translate if isinstance(text_to_translate, list) else [text_to_translate]
  to_languages = to_languages if isinstance(to_languages, list) else [to_languages]
  from_language = from_language[0] if isinstance(from_language, list) else from_language

  result = {}

  for to_language in to_languages:
    result[to_language] = []
    print('translating to: ' + to_language + ' ...' )

    for text in text_to_translate:
      req = request.Request(
        "http://translate.google.com/m?hl=%s&sl=%s&q=%s" % (to_language, from_language, encode(text).replace(" ", "+")),
        headers=agents)

      page = request.urlopen(req)
      encoding = page.headers['content-type'].split('charset=')[-1]
      content = str(page.read(), encoding=encoding)

      word_translation = content[content.find(translation_locator) + len(translation_locator):].split("<")[0]

      result[to_language].append( word_translation )

  return result
