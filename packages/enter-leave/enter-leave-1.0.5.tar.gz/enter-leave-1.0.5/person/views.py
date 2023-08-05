# coding:utf-8
from __future__ import unicode_literals
import datetime
from django.db.models import Q, Count
from django.utils import timezone
from django.http import Http404
from pytz import utc
from rest_framework import generics, mixins, permissions
from rest_framework.filters import OrderingFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView
from . import serializers, models


class PersonEnterPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    page_query_param = "page"
    max_page_size = 100

    def paginate_queryset(self, queryset, request, view=None):
        if request.query_params.get('page'):
            return super(PersonEnterPagination, self).paginate_queryset(queryset, request, view)
        else:
            return None


class EnterListView(generics.ListCreateAPIView):
    serializer_class = serializers.EnterOrLeaveSerializer
    queryset = models.EnterOrLeaves.objects.all()
    pagination_class = PersonEnterPagination
    filter_backends = (OrderingFilter,)
    ordering_fields = '__all__'
    ordering = ('id',)

    def get_queryset(self):
        id_card = self.request.query_params.get('id_card')
        name = self.request.query_params.get('name')
        gender = self.request.query_params.get('gender')
        native_place = self.request.query_params.get('native_place')
        identity = self.request.query_params.get('identity')
        enter_status = self.request.query_params.get('enter_status')
        enter_time_slice = self.request.query_params.get('enter_time_slice')
        project_unit = self.request.query_params.get('project_unit')
        team = self.request.query_params.get('team')
        work = self.request.query_params.get('work')
        queryset = models.EnterOrLeaves.objects.all()
        if id_card:
            queryset = queryset.filter(person__id_card=id_card)
        if name:
            queryset = queryset.filter(person__name=name)
        if gender:
            queryset = queryset.filter(person__gender=gender)
        if native_place:
            queryset = queryset.filter(person__native_place=native_place)
        if identity:
            queryset = queryset.filter(person__identity=identity)
        if team:
            queryset = queryset.filter(person__team=team)
        if work:
            queryset = queryset.filter(person__work__name=work)
        if enter_status:
            queryset = queryset.filter(enter_status=enter_status)
        if enter_time_slice:
            slice_list = enter_time_slice.replace(' ', '').split(',')
            if len(slice_list) == 2:
                try:
                    enter_time_from = datetime.datetime.strptime(slice_list[0], "%Y-%m-%d").replace(tzinfo=utc)
                    enter_time_to = datetime.datetime.strptime(slice_list[1], "%Y-%m-%d").replace(tzinfo=utc)
                except Exception as e:
                    raise Http404
                else:
                    queryset = queryset.filter(enter_time__range=(enter_time_from, enter_time_to))
        if project_unit:
            queryset.filter(Q(person__project_unit__pk=project_unit) | Q(person__project_unit__name=project_unit))

        return queryset

    def get_permissions(self):
        if self.request.method == "GET":
            return []
        else:
            return [permissions.IsAdminUser()]


class EnterDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = models.EnterOrLeaves.objects.all()
    serializer_class = serializers.EnterOrLeaveSerializer

    def get_object(self):
        try:
            pk = int(self.kwargs['pk'])
            enter_info = models.EnterOrLeaves.objects.get(pk=pk)
        except models.EnterOrLeaves.DoesNotExist:
            raise Http404
        return enter_info

    def get_permissions(self):
        if self.request.method == 'GET':
            return []
        else:
            return [permissions.IsAdminUser()]

    def perform_destroy(self, instance):
        person = instance.person
        person.delete()
        instance.delete()


class PersonLeaveView(APIView):
    permission_classes = (permissions.IsAdminUser,)

    def post(self, request, pk):
        try:
            leave_person = models.EnterOrLeaves.objects.get(pk=pk)
        except models.EnterOrLeaves.DoesNotExist:
            raise Http404
        if self.request.data.get("leave") != 'yes':
            return Response("operation failure")
        if leave_person.leave_time is not None:
            return Response('The personnel have left the field', status=400)
        leave_person.leave_time = timezone.now()
        enter_time = leave_person.enter_time.strftime('%Y-%m-%d %H:%M')
        leave_time = leave_person.leave_time.strftime('%Y-%m-%d %H:%M')
        history = {
            'enter_time': enter_time,
            'leave_time': leave_time
        }
        # if not leave_person.enter_status:
        leave_person.history.append(history)
        leave_person.enter_status = 1
        leave_person.save()
        serializer = serializers.EnterOrLeaveSerializer(leave_person)
        return Response(serializer.data)


class PersonEnterBulkView(APIView):
    permission_classes = (permissions.IsAdminUser,)

    def post(self, request):
        res = []
        if type(self.request.data) != list:
            return Response('you should post a list') 
        for index, data in enumerate(self.request.data):
            serializer = serializers.EnterOrLeaveSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                res.append({"index": index, "status": "seccess"})
            else:
                res.append({"index": index, "error": serializer.errors, "status": "failed"})
        return Response(res, status=201)


class PersonEnterLeaveCalculation(APIView):
    
    def get(self, request):
        keyword = self.request.query_params.get('keyword')
        status = self.request.query_params.get('status', None)
        enter_time_slice = self.request.query_params.get('enter_time_slice')
        queryset = models.Persons.objects.all()
        if enter_time_slice:
            slice_list = enter_time_slice.replace(' ', '').split(',')
            if len(slice_list) == 2:
                try:
                    enter_time_from = datetime.datetime.strptime(slice_list[0], "%Y-%m-%d").replace(tzinfo=utc)
                    enter_time_to = datetime.datetime.strptime(slice_list[1], "%Y-%m-%d").replace(tzinfo=utc)
                except Exception as e:
                    raise Http404
                if status == 'enter':
                    queryset = queryset.filter(enterorleaves__enter_time__range=(enter_time_from, enter_time_to),
                                               enterorleaves__enter_status=0)
                if status == 'leave':
                    queryset = queryset.filter(enterorleaves__enter_time__range=(enter_time_from, enter_time_to),
                                               enterorleaves__enter_status=1)
                else:
                    queryset = queryset.filter(enterorleaves__enter_time__range=(enter_time_from, enter_time_to))
            return Response({'count': queryset.count(), 'info': queryset.values()})
        if status == 'enter':
            queryset = queryset.filter(enterorleaves__enter_status=0)
        if status == 'leave':
            queryset = queryset.filter(enterorleaves__enter_status=1)
        if not keyword:
            raise Http404
        return Response(queryset.values(keyword).annotate(count=Count(keyword)))


class PersonEnterLeaveCalculationYear(APIView):

    def get(self, request):
        from collections import OrderedDict
        year = self.request.query_params.get('year')
        try:
            year = int(year)
        except TypeError:
            return Response("year should be integer")
        res = OrderedDict()
        queryset = models.EnterOrLeaves.objects.all()
        for i in range(12):
            res[i+1] = {
                'enter_num': queryset.filter(enter_time__year=year, enter_time__month=i+1).count(),
                'leave_num': queryset.filter(enter_time__year=year, leave_time__month=i+1).count(),
                'present_num': queryset.filter(enter_status=0).count()
            }
        return Response(res)
