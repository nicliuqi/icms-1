from django.shortcuts import render
from rest_framework.generics import GenericAPIView


class VulnerabilitiesView(GenericAPIView):
    def get(self, request, *args, **kwargs):
        return render(request, 'index.html')
