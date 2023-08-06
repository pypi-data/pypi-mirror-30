# -*- coding: utf-8 -*-
from plone.app.textfield import RichText
from plone.autoform.interfaces import IFormFieldProvider
from plone.dexterity.interfaces import IDexterityContent
from zope.component import adapter
from zope.interface import Interface
from zope.interface import implementer
from zope.interface import provider

from collective.behavior.richdescription import _


@provider(IFormFieldProvider)
class IRichDescription(Interface):

    rich_description = RichText(
        title=_(u'Rich description'),
        description=_('This description will be displayed above the content '
                      'body'),
        required=False,
    )


@implementer(IRichDescription)
@adapter(IDexterityContent)
class RichDescription(object):

    def __init__(self, context):
        self.context = context

    @property
    def rich_description(self):
        return getattr(self.context, 'rich_description', None)

    @rich_description.setter
    def rich_description(self, value):
        self.context.rich_description = value
