from django.utils.encoding import force_text

from rest_framework import status

from mayan.apps.documents.permissions import permission_document_view
from mayan.apps.documents.tests.mixins.document_mixins import DocumentTestMixin
from mayan.apps.events.tests.mixins import EventTestCaseMixin
from mayan.apps.rest_api.tests.base import BaseAPITestCase

from ..events import (
    event_tag_attach, event_tag_created, event_tag_edited, event_tag_removed
)
from ..models import Tag
from ..permissions import (
    permission_tag_attach, permission_tag_create, permission_tag_delete,
    permission_tag_edit, permission_tag_remove, permission_tag_view
)

from .mixins import TagAPIViewTestMixin, TagTestMixin


class TagAPIViewTestCase(
    EventTestCaseMixin, TagAPIViewTestMixin, TagTestMixin, BaseAPITestCase
):
    _test_event_object_name = 'test_tag'

    def test_tag_create_view_no_permission(self):
        tag_count = Tag.objects.count()

        response = self._request_test_tag_create_api_view()
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.assertEqual(Tag.objects.count(), tag_count)

        event = self._get_test_object_event()
        self.assertEqual(event, None)

    def test_tag_create_view_with_permission(self):
        self.grant_permission(permission=permission_tag_create)

        tag_count = Tag.objects.count()

        response = self._request_test_tag_create_api_view()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertEqual(Tag.objects.count(), tag_count + 1)

        event = self._get_test_object_event()
        self.assertEqual(event.verb, event_tag_created.id)

    def test_tag_delete_view_no_permission(self):
        self._create_test_tag()

        tag_count = Tag.objects.count()

        response = self._request_test_tag_delete_api_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self.assertEqual(Tag.objects.count(), tag_count)

    def test_tag_delete_view_with_access(self):
        self._create_test_tag()

        self.grant_access(obj=self.test_tag, permission=permission_tag_delete)

        tag_count = Tag.objects.count()

        response = self._request_test_tag_delete_api_view()
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        self.assertEqual(Tag.objects.count(), tag_count - 1)

    def test_tag_detail_api_view_no_permission(self):
        self._create_test_tag()

        response = self._request_test_tag_detail_api_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_tag_detail_view_api_with_access(self):
        self._create_test_tag()
        self.grant_access(
            obj=self.test_tag, permission=permission_tag_view
        )

        response = self._request_test_tag_detail_api_view()
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(response.data['label'], self.test_tag.label)

    def test_tag_edit_via_patch_no_permission(self):
        self._create_test_tag()

        tag_label = self.test_tag.label
        tag_color = self.test_tag.color

        response = self._request_test_tag_edit_api_view(verb='patch')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self.test_tag.refresh_from_db()
        self.assertEqual(self.test_tag.label, tag_label)
        self.assertEqual(self.test_tag.color, tag_color)

        event = self._get_test_object_event()
        self.assertEqual(event.verb, event_tag_created.id)

    def test_tag_edit_via_patch_with_access(self):
        self._create_test_tag()

        self.grant_access(obj=self.test_tag, permission=permission_tag_edit)

        tag_label = self.test_tag.label
        tag_color = self.test_tag.color

        response = self._request_test_tag_edit_api_view(verb='patch')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.test_tag.refresh_from_db()
        self.assertNotEqual(self.test_tag.label, tag_label)
        self.assertNotEqual(self.test_tag.color, tag_color)

        event = self._get_test_object_event()
        self.assertEqual(event.verb, event_tag_edited.id)

    def test_tag_edit_via_put_no_permission(self):
        self._create_test_tag()

        tag_label = self.test_tag.label
        tag_color = self.test_tag.color

        response = self._request_test_tag_edit_api_view(verb='put')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self.test_tag.refresh_from_db()
        self.assertEqual(self.test_tag.label, tag_label)
        self.assertEqual(self.test_tag.color, tag_color)

        event = self._get_test_object_event()
        self.assertEqual(event.verb, event_tag_created.id)

    def test_tag_edit_via_put_with_access(self):
        self._create_test_tag()

        self.grant_access(obj=self.test_tag, permission=permission_tag_edit)

        tag_label = self.test_tag.label
        tag_color = self.test_tag.color

        response = self._request_test_tag_edit_api_view(verb='put')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.test_tag.refresh_from_db()
        self.assertNotEqual(self.test_tag.label, tag_label)
        self.assertNotEqual(self.test_tag.color, tag_color)

        event = self._get_test_object_event()
        self.assertEqual(event.verb, event_tag_edited.id)

    def test_tag_list_api_view_no_permission(self):
        self._create_test_tag()
        response = self._request_test_tag_list_api_view()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 0)

    def test_tag_list_api_view_with_access(self):
        self._create_test_tag()
        self.grant_access(
            obj=self.test_tag, permission=permission_tag_view
        )

        response = self._request_test_tag_list_api_view()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data['results'][0]['label'],
            self.test_tag.label
        )


class TagDocumentAPIViewTestCase(
    DocumentTestMixin, EventTestCaseMixin, TagAPIViewTestMixin, TagTestMixin,
    BaseAPITestCase
):
    _test_event_object_name = 'test_tag'
    auto_upload_test_document = False

    def setUp(self):
        super().setUp()
        self._upload_test_document()
        self._create_test_tag()

    def test_tag_document_list_view_no_permission(self):
        self.test_tag.documents.add(self.test_document)

        response = self._request_test_tag_document_list_api_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_tag_document_list_view_with_tag_access(self):
        self.test_tag.documents.add(self.test_document)

        self.grant_access(obj=self.test_tag, permission=permission_tag_view)

        response = self._request_test_tag_document_list_api_view()
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(response.data['count'], 0)

    def test_tag_document_list_view_with_document_access(self):
        self.test_tag.documents.add(self.test_document)

        self.grant_access(
            obj=self.test_document, permission=permission_document_view
        )
        response = self._request_test_tag_document_list_api_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_tag_document_list_view_with_access(self):
        self.test_tag.documents.add(self.test_document)

        self.grant_access(obj=self.test_tag, permission=permission_tag_view)
        self.grant_access(
            obj=self.test_document, permission=permission_document_view
        )
        response = self._request_test_tag_document_list_api_view()
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(
            response.data['results'][0]['uuid'],
            force_text(s=self.test_document.uuid)
        )

    def test_document_attach_tag_view_no_permission(self):
        response = self._request_test_document_attach_tag_api_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self.assertTrue(self.test_tag not in self.test_document.tags.all())

        event = self._get_test_object_event()
        self.assertEqual(event.verb, event_tag_created.id)

    def test_document_attach_tag_view_with_document_access(self):
        self.grant_access(
            obj=self.test_document, permission=permission_tag_attach
        )

        response = self._request_test_document_attach_tag_api_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self.assertTrue(self.test_tag not in self.test_document.tags.all())

        event = self._get_test_object_event()
        self.assertEqual(event.verb, event_tag_created.id)

    def test_document_attach_tag_view_with_tag_access(self):
        self.grant_access(
            obj=self.test_tag, permission=permission_tag_attach
        )

        response = self._request_test_document_attach_tag_api_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self.assertTrue(self.test_tag not in self.test_document.tags.all())

        event = self._get_test_object_event()
        self.assertEqual(event.verb, event_tag_created.id)

    def test_document_attach_tag_view_with_full_access(self):
        self.grant_access(
            obj=self.test_document, permission=permission_tag_attach
        )
        self.grant_access(
            obj=self.test_tag, permission=permission_tag_attach
        )

        response = self._request_test_document_attach_tag_api_view()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertTrue(self.test_tag in self.test_document.tags.all())

        event = self._get_test_object_event()
        self.assertEqual(event.verb, event_tag_attach.id)

    def test_document_tag_detail_view_no_permission(self):
        self.test_tag.documents.add(self.test_document)

        response = self._request_test_document_tag_detail_api_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_document_tag_detail_view_with_document_access(self):
        self.test_tag.documents.add(self.test_document)

        self.grant_access(
            obj=self.test_document, permission=permission_document_view
        )

        response = self._request_test_document_tag_detail_api_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_document_tag_detail_view_with_tag_access(self):
        self.test_tag.documents.add(self.test_document)

        self.grant_access(obj=self.test_tag, permission=permission_tag_view)

        response = self._request_test_document_tag_detail_api_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_document_tag_detail_view_with_full_access(self):
        self.test_tag.documents.add(self.test_document)

        self.grant_access(obj=self.test_tag, permission=permission_tag_view)
        self.grant_access(
            obj=self.test_document, permission=permission_tag_view
        )

        response = self._request_test_document_tag_detail_api_view()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['label'], self.test_tag.label)

    def test_document_tag_list_view_no_permission(self):
        self.test_tag.documents.add(self.test_document)

        response = self._request_test_document_tag_list_api_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_document_tag_list_view_with_document_access(self):
        self.test_tag.documents.add(self.test_document)

        self.grant_access(
            obj=self.test_document, permission=permission_tag_view
        )

        response = self._request_test_document_tag_list_api_view()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 0)

    def test_document_tag_list_view_with_tag_access(self):
        self.test_tag.documents.add(self.test_document)

        self.grant_access(obj=self.test_tag, permission=permission_tag_view)

        response = self._request_test_document_tag_list_api_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_document_tag_list_view_with_full_access(self):
        self.test_tag.documents.add(self.test_document)

        self.grant_access(
            obj=self.test_document, permission=permission_tag_view
        )
        self.grant_access(obj=self.test_tag, permission=permission_tag_view)

        response = self._request_test_document_tag_list_api_view()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'][0]['label'], self.test_tag.label)

    def test_document_tag_remove_view_no_permission(self):
        self.test_tag.documents.add(self.test_document)

        response = self._request_test_document_tag_remove_api_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self.assertTrue(self.test_tag in self.test_document.tags.all())

        event = self._get_test_object_event()
        self.assertEqual(event.verb, event_tag_created.id)

    def test_document_tag_remove_view_with_document_access(self):
        self.test_tag.documents.add(self.test_document)

        self.grant_access(
            obj=self.test_document, permission=permission_tag_remove
        )

        response = self._request_test_document_tag_remove_api_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self.assertTrue(self.test_tag in self.test_document.tags.all())

        event = self._get_test_object_event()
        self.assertEqual(event.verb, event_tag_created.id)

    def test_document_tag_remove_view_with_tag_access(self):
        self.test_tag.documents.add(self.test_document)

        self.grant_access(obj=self.test_tag, permission=permission_tag_remove)

        response = self._request_test_document_tag_remove_api_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self.assertTrue(self.test_tag in self.test_document.tags.all())

        event = self._get_test_object_event()
        self.assertEqual(event.verb, event_tag_created.id)

    def test_document_tag_remove_view_with_full_access(self):
        self.test_tag.documents.add(self.test_document)

        self.grant_access(
            obj=self.test_document, permission=permission_tag_remove
        )
        self.grant_access(obj=self.test_tag, permission=permission_tag_remove)

        response = self._request_test_document_tag_remove_api_view()
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        self.assertFalse(self.test_tag in self.test_document.tags.all())

        event = self._get_test_object_event()
        self.assertEqual(event.verb, event_tag_removed.id)


class TagDocumentStubAPIViewTestCase(TagDocumentAPIViewTestCase):
    auto_upload_document = False

    def setUp(self):
        super().setUp()
        self._create_test_document_stub()
        self.test_document = self.test_document_stub
