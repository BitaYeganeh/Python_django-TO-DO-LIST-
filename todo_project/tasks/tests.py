from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .forms import TaskForm
from .models import Task


class TaskModelTests(TestCase):
    def test_new_task_defaults(self):
        user = User.objects.create_user('alice', password='pass12345!')
        task = Task.objects.create(user=user, title='Buy milk')
        self.assertFalse(task.completed)
        self.assertEqual(task.description, '')
        self.assertIsNotNone(task.created_at)
        self.assertEqual(str(task), 'Buy milk')

    def test_tasks_are_deleted_with_their_user(self):
        user = User.objects.create_user('alice', password='pass12345!')
        Task.objects.create(user=user, title='Temporary')
        user.delete()
        self.assertEqual(Task.objects.count(), 0)


class TaskFormTests(TestCase):
    def test_title_is_required(self):
        form = TaskForm(data={'title': '', 'description': 'x'})
        self.assertFalse(form.is_valid())
        self.assertIn('title', form.errors)

    def test_title_longer_than_200_characters_is_rejected(self):
        form = TaskForm(data={'title': 'a' * 201})
        self.assertFalse(form.is_valid())

    def test_valid_task(self):
        self.assertTrue(TaskForm(data={'title': 'Read a book'}).is_valid())


class SignupTests(TestCase):
    def test_signup_creates_user_and_logs_in(self):
        response = self.client.post(reverse('signup'), {
            'username': 'newuser',
            'password1': 'Str0ng-passw0rd!',
            'password2': 'Str0ng-passw0rd!',
        })
        self.assertRedirects(response, reverse('task_list'))
        self.assertTrue(User.objects.filter(username='newuser').exists())
        self.assertEqual(int(self.client.session['_auth_user_id']),
                         User.objects.get(username='newuser').pk)

    def test_signup_rejects_mismatched_passwords(self):
        response = self.client.post(reverse('signup'), {
            'username': 'newuser',
            'password1': 'Str0ng-passw0rd!',
            'password2': 'different-Passw0rd',
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username='newuser').exists())


class LoggedInTaskTests(TestCase):
    def setUp(self):
        self.alice = User.objects.create_user('alice', password='pass12345!')
        self.bob = User.objects.create_user('bob', password='pass12345!')
        self.client.login(username='alice', password='pass12345!')

    def test_add_task(self):
        response = self.client.post(reverse('task_list'), {'title': 'Write tests'})
        self.assertRedirects(response, reverse('task_list'))
        task = Task.objects.get(title='Write tests')
        self.assertEqual(task.user, self.alice)

    def test_empty_title_is_not_saved(self):
        response = self.client.post(reverse('task_list'), {'title': ''})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Task.objects.count(), 0)

    def test_user_sees_only_own_tasks(self):
        Task.objects.create(user=self.alice, title='Alice task')
        Task.objects.create(user=self.bob, title='Bob secret task')
        response = self.client.get(reverse('task_list'))
        self.assertContains(response, 'Alice task')
        self.assertNotContains(response, 'Bob secret task')

    def test_complete_toggles_task(self):
        task = Task.objects.create(user=self.alice, title='Toggle me')
        self.client.post(reverse('complete_task', args=[task.id]))
        task.refresh_from_db()
        self.assertTrue(task.completed)
        self.client.post(reverse('complete_task', args=[task.id]))
        task.refresh_from_db()
        self.assertFalse(task.completed)

    def test_delete_task(self):
        task = Task.objects.create(user=self.alice, title='Delete me')
        self.client.post(reverse('delete_task', args=[task.id]))
        self.assertFalse(Task.objects.filter(id=task.id).exists())

    def test_cannot_complete_another_users_task(self):
        task = Task.objects.create(user=self.bob, title='Bob task')
        response = self.client.post(reverse('complete_task', args=[task.id]))
        self.assertEqual(response.status_code, 404)
        task.refresh_from_db()
        self.assertFalse(task.completed)

    def test_cannot_delete_another_users_task(self):
        task = Task.objects.create(user=self.bob, title='Bob task')
        response = self.client.post(reverse('delete_task', args=[task.id]))
        self.assertEqual(response.status_code, 404)
        self.assertTrue(Task.objects.filter(id=task.id).exists())

    def test_delete_is_not_possible_with_a_plain_link(self):
        """Opening a link (GET) must never delete data; only a form submit (POST) may."""
        task = Task.objects.create(user=self.alice, title='Keep me')
        self.client.get(reverse('delete_task', args=[task.id]))
        self.assertTrue(Task.objects.filter(id=task.id).exists())

    def test_complete_is_not_possible_with_a_plain_link(self):
        task = Task.objects.create(user=self.alice, title='Keep me open')
        self.client.get(reverse('complete_task', args=[task.id]))
        task.refresh_from_db()
        self.assertFalse(task.completed)


class DemoModeTests(TestCase):
    def setUp(self):
        self.demo = User.objects.create_user('demo_user', password='pass12345!')
        Task.objects.create(user=self.demo, title='Demo task one')

    def test_visitors_see_demo_tasks(self):
        response = self.client.get(reverse('task_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Demo task one')
        self.assertTrue(response.context['demo'])

    def test_demo_page_shows_demo_tasks(self):
        response = self.client.get(reverse('demo_tasks'))
        self.assertContains(response, 'Demo task one')

    def test_visitors_cannot_delete_demo_tasks(self):
        task = Task.objects.get(title='Demo task one')
        response = self.client.post(reverse('delete_task', args=[task.id]))
        self.assertRedirects(response, reverse('task_list'))
        self.assertTrue(Task.objects.filter(id=task.id).exists())

    def test_demo_user_account_cannot_edit_tasks(self):
        self.client.login(username='demo_user', password='pass12345!')
        task = Task.objects.get(title='Demo task one')
        self.client.post(reverse('complete_task', args=[task.id]))
        task.refresh_from_db()
        self.assertFalse(task.completed)


class MissingDemoUserTests(TestCase):
    """A fresh database has no demo_user yet; the home page must still work."""

    def test_home_page_works_without_demo_user(self):
        response = self.client.get(reverse('task_list'))
        self.assertEqual(response.status_code, 200)

    def test_demo_page_works_without_demo_user(self):
        response = self.client.get(reverse('demo_tasks'))
        self.assertEqual(response.status_code, 200)
