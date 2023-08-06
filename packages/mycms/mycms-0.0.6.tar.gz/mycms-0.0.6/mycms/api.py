from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import

from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from rest_framework import serializers

from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework import status
from rest_framework.views import APIView

from rest_framework.decorators import detail_route
from rest_framework.decorators import list_route





from mycms.serializers import CMSPageTypesSerializer
from mycms.serializers import CMSContentsSerializer
from mycms.serializers import CMSEntrySerializer
from mycms.serializers import CMSMarkUpSerializer
from mycms.serializers import CMSTemplatesSerializer
from mycms.serializers import CMSPathsSerializer
from mycms.serializers import CMSEntryExpandedSerializer
from mycms.serializers import LoremIpsumSerializer
from mycms.serializers import CMSChildEntrySerializer

from mycms.models import CMSContents
from mycms.models import CMSMarkUps
from mycms.models import CMSTemplates
from mycms.models import CMSPageTypes
from mycms.models import CMSEntries
from mycms.models import CMSPaths

__all__ = [ "CMSContentsViewSet", 
            "CMSFormatterContent",
            "CMSEntriesViewSet"]

class CMSContentsViewSet(viewsets.ModelViewSet):
    
    permission_classes = (IsAuthenticated,)
    
    queryset = CMSContents.objects.all()
    serializer_class =  CMSContentsSerializer
    
    @detail_route(methods=["get"])
    def html(self, request, pk=None):

        content_obj =CMSContents.objects.get(id=pk)
        data = { "html": content_obj.html} 
        return Response( data, status=status.HTTP_200_OK)
    
        
class CMSFormatterContent(APIView):
    
    def get(self, request, **kwargs):
        
        content_id = kwargs.get("content_id")
        
        content_obj =CMSContents.objects.get(id=content_id)
        data = { "html": content_obj.html} 
        data = { "html": "Use the new html action of CMSContents."}
        return Response( data, status=status.HTTP_200_OK)
    
class CMSEntriesViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    
    queryset = CMSEntries.objects.all()
    serializer_class =  CMSEntrySerializer    


    @detail_route(methods=["get"])
    def get_categories(self, request, pk=None):
        parent_obj = CMSEntries.objects.get(id=pk)
        print(parent_obj)
        c = CMSEntries.objects.filter(path__parent=parent_obj.path, page_type__page_type="CATEGORY")
        serializer =  CMSEntrySerializer(c, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @detail_route(methods=["post"])
    def create_child(self, request, pk=None):
        """
        A utility function to create an article including path information. 
        """

        serializer = CMSChildEntrySerializer(data=request.data)
       
        if serializer.is_valid():
            print(serializer.data)
            vd = serializer.validated_data
            
            
            #The CMSChildEntrySerializer expects to get the pk of 
            #the parent.
            child_obj = serializer.create(vd, pk)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            print(serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)            
        
        
        
class CMSPathsViewSet(viewsets.ModelViewSet):
    
    permission_classes = (IsAuthenticated,)
    queryset = CMSPaths.objects.all()
    serializer_class =  CMSPathsSerializer    
    


