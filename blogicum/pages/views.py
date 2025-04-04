from django.shortcuts import render
from django.views.generic import TemplateView

class StaticPageView(TemplateView):
    extra_context = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.extra_context:
            context.update(self.extra_context)
        return context
    
class AboutView(StaticPageView):
    template_name = 'pages/about.html'

class RulesView(StaticPageView):
    template_name = 'pages/rules.html'


def page_not_found(request, exception):
    template = 'pages/404.html'
    return render(request, template, status=404)

def csrf_failure(request, reason=''):
    template = 'pages/403csrf.html'
    return render(request, template, status=403)

def server_failure(request):
    template = 'pages/500.html'
    return render(request, template)