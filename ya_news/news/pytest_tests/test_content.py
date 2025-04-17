import pytest
from django.conf import settings

from news.forms import CommentForm

pytestmark = pytest.mark.django_db


def test_news_count_limit_on_home_page(client, news_bulk, home_url):
    response = client.get(home_url)
    news = response.context['object_list']
    assert len(news) == settings.NEWS_COUNT_ON_HOME_PAGE


def test_comments_sorted_by_date(client, news_detail_url, comments_bulk):
    response = client.get(news_detail_url)
    comments = response.context['object'].comment_set.all()
    created_dates = [comment.created for comment in comments]
    assert created_dates == sorted(created_dates)


def test_comment_form_for_authorized_user(author_client, news_detail_url):
    response = author_client.get(news_detail_url)
    assert 'form' in response.context
    assert isinstance(response.context['form'], CommentForm)


def test_comment_form_for_anonymous_user(client, news_detail_url):
    response = client.get(news_detail_url)
    assert 'form' not in response.context
