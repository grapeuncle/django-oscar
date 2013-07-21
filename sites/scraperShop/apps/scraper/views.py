from django.http import HttpResponse
from django.views.generic.base import View
from django.views.decorators.csrf import csrf_exempt


class RunView(View):
    @csrf_exempt
    def dispatch(self, *args, **kwargs):
        return super(RunView, self).dispatch(*args, **kwargs)
    def post(self, request):
        print request
        return HttpResponse(str(request.POST.get('cmd', 'null')))
    def get(self, request):
        print request
        return HttpResponse(str(request))
