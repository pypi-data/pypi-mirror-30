# -*- coding: utf-8 -*-

from plone.app.layout.viewlets import common as base


class RichDescriptionViewlet(base.ViewletBase):

    @property
    def can_view(self):
        rich_description = getattr(self.context, 'rich_description', None)
        if getattr(rich_description, 'raw', None):
            return True
        return False
