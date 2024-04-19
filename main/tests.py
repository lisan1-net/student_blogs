from django.apps import apps
from django.core.management import call_command
from django.shortcuts import reverse
from django.test import TestCase


class TestWebApp(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.Blog = apps.get_model('main', 'Blog')
        cls.Text = apps.get_model('main', 'Text')
        call_command('indexwords')

    def test_search_page(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'main/search/search.html')
        self.assertTemplateUsed(response, 'main/search/search_form.html')
        self.assertContains(response, self.Blog.objects.last().title)

    def test_perform_search(self):
        blog = self.Blog.objects.first()
        query = 'العَظِيمُ'
        response = self.client.get('/', {'search_query': query, 'blog': blog.pk})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'main/search/search.html')
        self.assertTemplateUsed(response, 'main/search/result_card.html')
        self.assertContains(response, query)
        self.assertGreater(len(response.context['results']), 0)
        self.assertContains(response, reverse('text', args=[blog.text_set.first().pk]))

    def test_no_results_search(self):
        query = 'العظيم'
        response = self.client.get('/', {'search_query': query, 'blog': self.Blog.objects.last().pk})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'main/search/search.html')
        self.assertTemplateNotUsed(response, 'main/search/result_card.html')
        self.assertContains(response, query, count=1)
        self.assertEqual(len(response.context['results']), 0)

    def test_vocabulary_page(self):
        response = self.client.get(reverse('vocabulary'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'main/vocabulary/vocabulary.html')
        self.assertTemplateUsed(response, 'main/vocabulary/vocabulary_form.html')
        self.assertContains(response, self.Blog.objects.last().title)

    def test_blog_vocabulary(self):
        blog = self.Blog.objects.first()
        response = self.client.get(f"{reverse('vocabulary')}?blog={blog.pk}")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'main/vocabulary/vocabulary.html')
        self.assertContains(response, blog.title)
        self.assertContains(response, blog.text_set.first().tokens.first().content)

    def test_text_popup(self):
        text = self.Text.objects.first()
        start = 10
        end = 20
        highlighted = text.content[start:end]
        response = self.client.get(
            f"{reverse('text', args=[text.pk])}?start={start}&end={end}"
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'main/popups/text.html')
        self.assertContains(response, text.title)
        self.assertContains(response, '<span class="text-warning">' + highlighted + '</span>')
