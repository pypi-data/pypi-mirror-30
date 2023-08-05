import os

from django.urls import reverse
import CommonMark

from markdocs.conf import settings as markdocs_settings


def get_domain(request):
    return request.scheme + '://' + request.get_host()


def markdown_to_html(markdown):
    return CommonMark.commonmark(markdown)


def get_index():
    return reverse('markdocs:index')


def generate_toc(request, document):
    links = []

    class Link:
        def __init__(self, url, title, current):
            self.url = url
            self.title = title
            self.current = current

    for root, dirs, files in os.walk(markdocs_settings.DOC_PATH):
        for file in files:
            if file.endswith('.md'):
                name = file[0:-3]
                url = get_index() + name
                title = name.replace('_', ' ').title()
                current = name == document
                link = Link(url=url, title=title, current=current)
                links.append(link)

    return links
