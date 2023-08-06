# -*- coding: utf-8 -*-
from lxml import etree
from plone.app.users.browser.schemaeditor import get_schema
import plone.app.users.browser.schemaeditor as ttw
import logging
logger = logging.getLogger(__name__)

snew_schema = '''
<model xmlns:easyform="http://namespaces.plone.org/supermodel/easyform"
       xmlns:form="http://namespaces.plone.org/supermodel/form"
       xmlns:i18n="http://xml.zope.org/namespaces/i18n"
       xmlns:lingua="http://namespaces.plone.org/supermodel/lingua"
       xmlns:marshal="http://namespaces.plone.org/supermodel/marshal"
       xmlns:security="http://namespaces.plone.org/supermodel/security"
       xmlns:users="http://namespaces.plone.org/supermodel/users"
       xmlns="http://namespaces.plone.org/supermodel/schema"
       i18n:domain="plone">
  <schema name="member-fields">
    <field name="personal_bookmarks"
           type="zope.schema.Text"
           users:forms="In User Profile">
      <description/>
      <required>False</required>
      <title>Personal bookmarks</title>
    </field>
  </schema>
</model>
'''

def import_various(context):
    if context.readDataFile('mybookmarksportlet-various.txt') is None:
        return
    updateMemberSchema()


def updateMemberSchema():
    """
    we need to manually add the schema in this way because otherwise old schema
    will be replaced by the new in userschema.xml
    """
    new_xml = etree.fromstring(snew_schema)
    old_xml = etree.fromstring(get_schema())
    new_fields = new_xml.findall(
        './/{http://namespaces.plone.org/supermodel/schema}field')
    old_schema = old_xml.findall(
        './/{http://namespaces.plone.org/supermodel/schema}schema')[0]
    for new_field in new_fields:
        old_schema.append(new_field)
    ttw.applySchema(etree.tostring(old_xml))
    logger.info('Add personal_bookmarks in member-fields')
