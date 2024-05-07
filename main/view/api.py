from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404

from main.forms import SearchForm
from main.models import Blog, Announcement


def blog_ids(request):
    blog_ids = Blog.objects.values_list('id', flat=True)
    return JsonResponse(list(blog_ids), safe=False)


def blog_card(request, pk):
    blog = get_object_or_404(Blog, pk=pk)
    return render(request, 'main/common/blog_card.html', context={'blog': blog})


def advanced_search_form(request):
    form = SearchForm(request.GET or None)
    return render(request, 'main/search/advanced_search_form.html', context={'form': form})


def announcements(request):
    announcements = Announcement.objects.filter(is_active=True).order_by('-posted_on')
    return render(request, 'main/common/announcements.html', context={'announcements': announcements})
