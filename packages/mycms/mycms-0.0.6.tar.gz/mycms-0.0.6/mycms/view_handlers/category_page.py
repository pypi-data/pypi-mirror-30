from mycms.models import CMSEntries
from mycms.models import CMSPageTypes
from mycms.view_handlers.mycms_view import YACMSViewObject

from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.db.utils import OperationalError

import logging
logger = logging.getLogger("mycms.page_handlers")

try:

    try:
        singlepageview_pagetype_obj, c = obj = CMSPageTypes.objects.get_or_create(page_type = "SINGLEPAGE",
                                                     text = "Single Page HTML",
                                                     view_class = "SinglePage",
                                                     view_template = "SinglePage.html")

    except ObjectDoesNotExist as e:
        singlepageview_pagetype_obj = CMSPageTypes( page_type = "SINGLEPAGE",
                                                     text = "Single Page HTML",
                                                     view_class = "SinglePage",
                                                     view_template = "SinglePage.html")
        singlepageview_pagetype_obj.save()

    except MultipleObjectsReturned as e:
        msg = "Got more than 1 CMSPageTypes : SINGLEPAGE. Database is inconsistent, Will return the first one. "
        logger.warn(msg)

        singlepageview_pagetype_obj = CMSPageTypes.objects.filter(page_type="SINGLEPAGE")[0]


    try:
        categorypageview_pagetype_obj = CMSPageTypes.objects.get(page_type="CATEGORY")

    except ObjectDoesNotExist as e:

        msg = "Could not load CATEGORY view object. Going to create it."
        logger.debug(msg)
        pagetype_obj, _ = CMSPageTypes.objects.get_or_create(page_type="CATEGORY",
                                                         text = "Category Page",
                                                         view_class = "CategoryPage",
                                                         view_template = "CategoryPage.html"
                                                         )

    except MultipleObjectsReturned as e:
        msg = "Got more than 1 CMSPageType: CATEGORY. Database is inconsistent. Will return the first one."
        logger.info(msg)

        categorypageview_pagetype_obj = CMSPageTypes.objects.filter(page_type="CATEGORY")[0]

    try:
        multipageview_pagetype_obj = CMSPageTypes.objects.get(page_type="MULTIPAGE")

    except ObjectDoesNotExist as e:

        msg = "Could not load MULTIPAGE view object. Going to create it."
        logger.debug(msg)
        multipageview_pagetype_obj, _ = CMSPageTypes.objects.get_or_create(page_type="MULTIPAGE",
                                                         text = "MultPage Article",
                                                         view_class = "MultiPage",
                                                         view_template = "MultiPage.html"
                                                         )

    except MultipleObjectsReturned as e:
        msg = "Got more than 1 CMSMultiPageType: MULTIPAGE. Database is inconsistent. Will return the first one."
        logger.info(msg)

        multipageview_pagetype_obj = CMSMultiPageTypes.objects.filter(page_type="MULTIPAGE")[0]


    #MULTIPAGE

    try:
        memberpageview_pagetype_obj = CMSPageTypes.objects.get(page_type="MEMBERPAGE")

    except ObjectDoesNotExist as e:

        msg = "Could not load MULTIPAGE view object. Going to create it."
        logger.debug(msg)
        pagetype_obj, _ = CMSPageTypes.objects.get_or_create(page_type="MEMBERPAGE",
                                                         text = "MemberPage Article",
                                                         view_class = "MemberPage",
                                                         view_template = "MemberPage.html"
                                                         )

    except MultipleObjectsReturned as e:
        msg = "Got more than 1 CMSMultiPageType: MULTIPAGE. Database is inconsistent. Will return the first one."
        logger.info(msg)

        memberpageview_pagetype_obj = CMSMultiPageTypes.objects.filter(page_type="MEMBERPAGE")[0]



except OperationalError as e:
    #This can happen only when the database is not yet initialized.
    pass




class CategoryPage(object):

    def __init__(self, page_object):
        self.page_object = page_object


    def articles(self):

        """Here we load all pages that says we are their parent."""

        from django.db.models import Q



        obj_list = CMSEntries.objects.filter((Q(page_type = singlepageview_pagetype_obj) | Q(page_type = multipageview_pagetype_obj)) &
                                             Q(path__parent__id = self.page_object.path.id))
        #wrap the entries of the obj_list into their view_handler representations
        view_list = []
        for obj in obj_list:
            view_list.append(YACMSViewObject(page_object=obj))

        return view_list



    def get_categories(self):
        """Returns a list of all child categories of type: CATEGORY"""

        obj_list = CMSEntries.objects.filter(path__path__parent__id = self.page_object.id,
                                             page_type=page_obj.page_type)

        return obj_list



    def page_types(self):

        """
        Refactor me into a parent class.
        returns a list fo page_types
        """


        pagetype_objs = CMSPageTypes.objects.all()

        return pagetype_objs


    def on_create(self):
        pass
