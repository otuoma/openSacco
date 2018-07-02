from django import template
# import cStringIO, base64, urllib
#
# register = template.Library()
#
# @register.filter
# def get64(url):
#
#     if url.startswith('http'):
#         image = cStringIO.StringIO(urllib.request.urlopen(url=url).read())
#
#         return 'data:imge/jpepg;base64,' + base64.b64encode(image.read())
#
#     return url