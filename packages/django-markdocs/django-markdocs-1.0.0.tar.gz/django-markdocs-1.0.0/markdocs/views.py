import os

from django.http import HttpResponse, Http404
from django.template import loader
from django.conf import settings
from django.views.generic.base import View

from markdocs import util
from markdocs.conf import settings as markdocs_settings


class MarkdocsView(View):
    template_name = "markdocs/md_content.html"
    def get(self, request, *args, **kwargs):
        template = loader.get_template(self.__class__.template_name)
        context = {
            'index': util.get_index(),
            'login_url': settings.LOGIN_URL,
            'doc_title': markdocs_settings.DOC_TITLE,
        }
        if not request.user.is_staff:
            return HttpResponse(template.render(context, request))
        document = kwargs['document'] if 'document' in kwargs else 'index'
        if document == 'index':
            if os.path.isfile(markdocs_settings.DOC_PATH + 'index.md'):
                path = markdocs_settings.DOC_PATH
            else:
                path = os.path.dirname(__file__) + '/mdocs/'
        else:
            path = markdocs_settings.DOC_PATH
        try:
            with open(path + '{}.md'.format(document), 'r') as file:
                markdown = file.read()
                html = util.markdown_to_html(markdown)
        except IOError:
            raise Http404('{} not found.'.format(document))

        table_of_contents = util.generate_toc(request, document)

        context['html'] = html
        context['table_of_contents'] = table_of_contents

        return HttpResponse(template.render(context, request))
