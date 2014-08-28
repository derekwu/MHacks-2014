from django.shortcuts import render

# Create your views here.

#TODO: Update the base.html navigation to use templated views
def base(request):
    context = {}
    return render(request, 'core/base.html', context)

def about(request):
    context = {}
    return render(request, 'core/about.html', context)

def faq(request):
    context = {}
    return render(request, 'core/faq.html', context)

