from django.views.generic import TemplateView


class RootView(TemplateView):
    template_name = 'socialchef/index.html'
