from django.urls import reverse

SLUG = 'test-slug'

CREATE_URL = reverse('notes:add')


def home_url():
    return reverse('notes:home')


def login_url():
    return reverse('users:login')


def logout_url():
    return reverse('users:logout')


def signup_url():
    return reverse('users:signup')


def list_url():
    return reverse('notes:list')


def add_url():
    return reverse('notes:add')


def success_url():
    return reverse('notes:success')


def detail_url():
    return reverse('notes:detail', args=[SLUG])


def edit_url():
    return reverse('notes:edit', args=[SLUG])


def delete_url():
    return reverse('notes:delete', args=[SLUG])
