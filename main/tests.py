from django.apps import apps
from django.core.management import call_command
from django.shortcuts import reverse
from django.test import TestCase

from main.templatetags.search import replace_custom_tags_with_popovers, wrap_with_popover, TagMerger


class TestWebApp(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.Blog = apps.get_model('main', 'Blog')
        cls.Text = apps.get_model('main', 'Text')
        call_command('indexwords')
        call_command('indexbigrams')
        call_command('indextrigrams')

    def test_search_page(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'main/search/search.html')
        self.assertTemplateUsed(response, 'main/search/search_form.html')
        self.assertContains(response, '$(')

    def test_perform_search(self):
        blog = self.Blog.objects.first()
        query = 'العَظِيمُ'
        response = self.client.get('/', {'search_query': query, 'blog': blog.pk})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'main/search/search.html')
        self.assertContains(response, query)

    def test_no_results_search(self):
        query = 'العظيم'
        response = self.client.get('/', {'search_query': query, 'blog': self.Blog.objects.last().pk})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'main/search/search.html')
        self.assertTemplateNotUsed(response, 'main/search/result_card.html')
        self.assertContains(response, query, count=1)

    def test_vocabulary_page(self):
        response = self.client.get(reverse('vocabulary'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'main/vocabulary/vocabulary.html')

    def test_blog_vocabulary(self):
        blog = self.Blog.objects.first()
        response = self.client.get(f"{reverse('vocabulary')}?blog={blog.pk}")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'main/vocabulary/vocabulary.html')

    def test_text_popup(self):
        text = self.Text.objects.first()
        start = 10
        end = 20
        highlighted = text.content[start:end]
        response = self.client.get(
            f"{reverse('text', args=[text.pk])}?start={start}&end={end}"
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'main/detail/text.html')
        self.assertContains(response, text.title)
        self.assertContains(response, '<span class="text-warning">' + highlighted + '</span>')


class TestTemplateTags(TestCase):

    def setUp(self):
        self.SemanticTag = apps.get_model('main', 'SemanticTag')
        self.MorphologicalTag = apps.get_model('main', 'MorphologicalTag')

    def test_merge_nested_tags(self):
        merger = TagMerger()
        merger.feed('هذا <b><u>نص</u></b> للتجريب')
        self.assertEqual(merger.result, ['هذا ', '<b|u>نص</b|u>', ' للتجريب'])

    def test_wrap_with_popover(self):
        title = 'عنوان تجريبي'
        content = 'هذا هو المحتوى الموافق للعنوان التجريبي'
        result = wrap_with_popover(title, content, wrap_element='b')
        self.assertIn(f'title="{title}"', result)
        self.assertIn('<b>' + title + '</b>', result)
        self.assertIn('<ul><li>' + content + '</li></ul>', result)

    def test_replace_custom_tags_with_popovers(self):
        text = 'هذا <semantic>نص</semantic> تجريبي و<morphological>نص</morphological> آخر'
        semantic = self.SemanticTag.objects.create(symbol='semantic', content='هذا هو المحتوى الموافق للعنوان التجريبي')
        morphological = self.MorphologicalTag.objects.create(symbol='morphological', content='هذا هو المحتوى الموافق للعنوان الآخر')
        result = replace_custom_tags_with_popovers(text)
        self.assertEqual(
            result,
            f'هذا {wrap_with_popover("نص", semantic.content, "b")} تجريبي و{wrap_with_popover("نص", morphological.content, "b")} آخر'
        )

    def test_replace_custom_tags_with_popovers_nested_tags(self):
        text = 'هذا <semantic><morphological>نص</morphological></semantic> تجريبي'
        semantic = self.SemanticTag.objects.create(symbol='semantic', content='هذا هو المحتوى الموافق للعنوان التجريبي')
        morphological = self.MorphologicalTag.objects.create(symbol='morphological', content='هذا هو المحتوى الموافق للعنوان الآخر')
        result = replace_custom_tags_with_popovers(text)
        self.assertIn('<li>' + semantic.content + '</li>', result)
        self.assertIn('<li>' + morphological.content + '</li>', result)
        self.assertIn('نص', result)

    def test_replace_custom_tags_with_popovers_non_existing_tags(self):
        text = 'هذا <semantic>نص</semantic> تجريبي'
        result = replace_custom_tags_with_popovers(text)
        expected = 'هذا نص تجريبي'
        self.assertEqual(result, expected)
