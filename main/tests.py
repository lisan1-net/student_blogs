from django.test import TestCase
from django.shortcuts import reverse
from django.apps import apps
from django.core.management import call_command


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
        query = 'فاتحة'
        response = self.client.get('/', {'search_query': query, 'blog': blog.pk})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'main/search/search.html')
        self.assertTemplateUsed(response, 'main/search/result_card.html')
        self.assertContains(response, query)
        self.assertContains(response, reverse('text', args=[blog.text_set.first().pk]))

    def test_no_results_search(self):
        query = 'Invalid query'
        response = self.client.get('/', {'search_query': query})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'main/search/search.html')
        self.assertTemplateNotUsed(response, 'main/search/result_card.html')
        self.assertContains(response, query, count=1)

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
        self.assertContains(response, blog.text_set.first().word_set.first().content)

    def test_text_popup(self):
        text = self.Text.objects.first()
        start = 10
        end = 20
        highlighted = text.content_normalized[start:end]
        response = self.client.get(
            f"{reverse('text', args=[text.pk])}?start={start}&end={end}"
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'main/popups/text.html')
        self.assertContains(response, text.title)
        self.assertContains(response, '<span class="text-warning">' + highlighted + '</span>')
