#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Created by flytrap
import json
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.contrib.contenttypes.models import ContentType
from .models import Comment

User = get_user_model()


# Create your tests here.

class CommentTestCase(TestCase):
    def setUp(self):
        user1_email = 'test@email.com'
        password = 'x111111'
        self.user = User.objects.filter(email=user1_email).first()
        self.user = User.objects.create_user(user1_email, user1_email, password)

        self.client.login(username='test@email.com', password='x111111')
        # if hasattr(self.user, 'get_authtoken'):
        #     self.client.defaults['HTTP_AUTHORIZATION'] = 'Token {}'.format(self.user.get_authtoken())

    def create_comment(self):
        return Comment.objects.create(author=self.user, comment='comment')

    def test_list(self):
        comment = self.create_comment()
        response = self.client.get(reverse('comments:comments'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(comment.id, response.data.get('results')[0].get('id'))

    def test_create(self):
        content_type = ContentType.objects.filter(model='user').first()
        data = {
            'object_id': self.user.id,
            'content_type': content_type.id,
            'comment': 'test_content',
        }
        response = self.client.post(reverse('comments:comments'), data=json.dumps(data),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 201)

    def test_update(self):
        comment = self.create_comment()
        data = {'comment': 'update', 'content_type': comment.content_type.id, 'object_id': comment.object_id}
        response = self.client.put(reverse('comments:single_comment', kwargs={'pk': comment.id}),
                                   data=json.dumps(data),
                                   content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Comment.objects.filter(id=comment.id).first().comment, data.get('comment'))

    def test_destroy(self):
        comment = self.create_comment()
        response = self.client.delete(reverse('comments:single_comment', kwargs={'pk': comment.id}))
        self.assertEqual(response.status_code, 204)
        self.assertFalse(Comment.objects.filter(id=comment.id, is_valid=True).exists())
