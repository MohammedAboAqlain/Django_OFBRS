from rest_framework import generics
from rest_framework.permissions import AllowAny,IsAuthenticated
from rest_framework.response import Response
from knox.models import AuthToken
from knox.views import LoginView as KnoxLoginView
from rest_framework import serializers
from django.contrib.auth import login, authenticate
from django.utils.translation import gettext_lazy as _
from django.shortcuts import get_object_or_404
from django.db.models import Q
from .models import (
User,
Market,
Entries,
StorageEntry,
EntryType,
FAQ,
)
names = ["محمد",'أحمد',"جمال",'كوثر','محمود','علي','عبد','رباح','جمعة','خميس','نادر','مصطفى']
class RegisterAPI(generics.GenericAPIView):
    from .serializers import CreateUserSerializer
    serializer_class = CreateUserSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        from .serializers import UserSerializer
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({
            "message": "تم تسجيل الإشتراك بنجاح",
            "token": AuthToken.objects.create(user)[1],
            "user": UserSerializer(user, context=self.get_serializer_context()).data,
        })

class MyAuthTokenSerializer(serializers.Serializer):
    phone = serializers.CharField(
        write_only=True
    )
    password = serializers.CharField(
        label=_("Password"),
        style={'input_type': 'password'},
        trim_whitespace=False,
        write_only=True
    )

    def validate(self, attrs):
        phone = attrs.get('phone')
        password = attrs.get('password')

        try:
            check_user = get_object_or_404(User,phone=phone)
        except:
            msg = _('Incorrect phone')
            raise serializers.ValidationError(msg, code='authorization')
        if phone and password:
            user = authenticate(request=self.context.get('request'),
                                phone=phone, password=password)
            if not user:
                msg = _('Incorrect phone or password.')
                raise serializers.ValidationError(msg, code='authorization')
        else:
            msg = _('Please provide password.')
            raise serializers.ValidationError(msg, code='authorization')
        if user.is_deleted:
            msg = _('Incorrect phone or password.')
            raise serializers.ValidationError(msg, code='authorization')
        attrs['user'] = user
        return attrs

class LoginAPI(KnoxLoginView):
    permission_classes = [AllowAny]

    def post(self, request, format=None):
        serializer = MyAuthTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        login(request, user)
        login_api_return_dict = super(LoginAPI, self).post(request, format=None)
        try:
            from .serializers import UserSerializer
            serializer = UserSerializer(user, context={'request': request})
        except:
            raise serializers.ValidationError("NONE TYPE USER", code='authorization')
        login_api_return_dict.data["message"] = "تم تسجيل الدخول بنجاح"
        login_api_return_dict.data["access_token"] = login_api_return_dict.data.pop('token')
        login_api_return_dict.data["expires_at"] = login_api_return_dict.data.pop('expiry')
        login_api_return_dict.data["user"] = serializer.data
        # for i in Market.objects.raw('SELECT * FROM Market'):
        # print()
        return login_api_return_dict

class IndexMarket(generics.ListAPIView):
    from .serializers import MarketSerializer
    serializer_class = MarketSerializer
    permission_classes = [AllowAny]
    pagination_class = None

    def get_queryset(self):
        markets = Market.objects.all()
        return markets

    def list(self, request, *args, **kwargs):
        query = self.get_queryset()
        queryset = self.filter_queryset(query)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'item' :serializer.data,
        })
import random
class GetEntryType(generics.ListAPIView):
    from .serializers import EntryTypeSerializer
    serializer_class = EntryTypeSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        entrys = EntryType.objects.all()
        return entrys

    def list(self, request, *args, **kwargs):
        query = self.get_queryset()
        queryset = self.filter_queryset(query)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        # for i in range(1000):
        #     phone = "059{p}".format(p=(''.join(["{}".format(random.randint(0, 9)) for num in range(0, 7)])))
        #     name = f"{random.choice(names)} {random.choice(names)}"
        #     type_id = random.choice([0,1,5,6])
        #     if type_id == 1:
        #         market_id = random.choice(list(Market.objects.all().values_list("id",flat=True)))
        #
        #     user = User.objects.create_user(
        #         phone=phone,
        #         name=name,
        #         type_id=type_id,
        #         password=phone,
        #     )
        #     if user:
        #         if type_id == 1:
        #             user.market = Market.objects.get(pk=market_id)
        #             user.save()
        return Response({
            'item' :serializer.data,
        })

class AllSeller(generics.ListAPIView):
    from .serializers import GetAllSellerSerializer
    serializer_class = GetAllSellerSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        sellers = User.objects.filter(type_id=1,is_deleted=False,is_active=True).order_by('darsh_key')
        return sellers

    def list(self, request, *args, **kwargs):
        query = self.get_queryset()
        queryset = self.filter_queryset(query)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'data' :serializer.data,
        })

class AllDeletedUsers(generics.ListAPIView):
    from .serializers import UserSerializer
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        deleted_users = User.objects.filter(is_deleted=False,is_active=False)
        return deleted_users

    def list(self, request, *args, **kwargs):
        query = self.get_queryset()
        queryset = self.filter_queryset(query)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'data' :serializer.data,
        })
class AllFAQs(generics.ListAPIView):
    from .serializers import QSerializer
    serializer_class = QSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        qs = FAQ.objects.all()
        return qs

    def list(self, request, *args, **kwargs):
        query = self.get_queryset()
        queryset = self.filter_queryset(query)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'data' :serializer.data,
        })

class AllSellerByMarket(generics.ListAPIView):
    from .serializers import GetAllSellerSerializer
    serializer_class = GetAllSellerSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        try:
            market_id = self.kwargs.get('market_id')
        except:
            market_id = -1
        sellers = User.objects.filter(type_id=1,is_deleted=False,is_active=True,market_id=market_id).order_by('darsh_key')
        return sellers

    def list(self, request, *args, **kwargs):
        query = self.get_queryset()
        queryset = self.filter_queryset(query)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'data' :serializer.data,
        })
class AllStorageEntries(generics.ListAPIView):
    from .serializers import StorageEntrySerializer
    serializer_class = StorageEntrySerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        try:
            from datetime import datetime,timedelta
            From_date_created = datetime.strptime(self.request.GET['From_date_created'],"%Y-%m-%d").date()
            To_date_created = datetime.strptime(self.request.GET['To_date_created'],"%Y-%m-%d").date() + timedelta(days=1)
            From_date_updated = datetime.strptime(self.request.GET['From_date_updated'],"%Y-%m-%d").date()
            To_date_updated = datetime.strptime(self.request.GET['To_date_updated'],"%Y-%m-%d").date() + timedelta(days=1)
        except:
            return 0

        criterion1 = Q(date_created__range=[From_date_created,To_date_created])
        criterion2 = Q(date_updated__range=[From_date_updated,To_date_updated])
        criterion3 = Q(type_id=14)
        StorageEntries = StorageEntry.objects.filter((criterion1|criterion2),~criterion3).order_by("-date_created")
        return StorageEntries

    def list(self, request, *args, **kwargs):
        query = self.get_queryset()
        if query == 0 :
            return Response({
                            'status':False,
                            'msg':"يرجى التأكد من إرسال جميع البيانات المطلوبة",
                            },
                            status=400
                           )
        queryset = self.filter_queryset(query)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'data' :serializer.data,
        })
class AllEntries(generics.ListAPIView):
    from .serializers import FullEntrySerializer
    serializer_class = FullEntrySerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        try:
            from datetime import datetime,timedelta
            From_date_created = datetime.strptime(self.request.GET['From_date_created'],"%Y-%m-%d").date()
            To_date_created = datetime.strptime(self.request.GET['To_date_created'],"%Y-%m-%d").date() + timedelta(days=1)
            From_date_updated = datetime.strptime(self.request.GET['From_date_updated'],"%Y-%m-%d").date()
            To_date_updated = datetime.strptime(self.request.GET['To_date_updated'],"%Y-%m-%d").date() + timedelta(days=1)
        except:
            return 0

        criterion1 = Q(date_created__range=[From_date_created,To_date_created])
        criterion2 = Q(date_updated__range=[From_date_updated,To_date_updated])
        entries = Entries.objects.filter(criterion1|criterion2).order_by("-date_created")
        return entries

    def list(self, request, *args, **kwargs):
        query = self.get_queryset()
        if query == 0 :
            return Response({
                            'status':False,
                            'msg':"يرجى التأكد من إرسال جميع البيانات المطلوبة",
                            },
                            status=400
                           )
        queryset = self.filter_queryset(query)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'data' :serializer.data,
        })
class AllEntriesForUser(generics.ListAPIView):
    from .serializers import FullEntrySerializer
    serializer_class = FullEntrySerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        try:
            user_id = self.kwargs.get('user_id')
            from datetime import datetime,timedelta
            From_date_created = datetime.strptime(self.request.GET['From_date_created'],"%Y-%m-%d").date()
            To_date_created = datetime.strptime(self.request.GET['To_date_created'],"%Y-%m-%d").date() + timedelta(days=1)
            From_date_updated = datetime.strptime(self.request.GET['From_date_updated'],"%Y-%m-%d").date()
            To_date_updated = datetime.strptime(self.request.GET['To_date_updated'],"%Y-%m-%d").date() + timedelta(days=1)
        except:
            return 0

        criterion1 = Q(date_created__range=[From_date_created,To_date_created])
        criterion2 = Q(date_updated__range=[From_date_updated,To_date_updated])
        criterion3 = Q(giver_id_id=user_id)
        criterion4 = Q(taker_id_id=user_id)
        entries = Entries.objects.filter((criterion1|criterion2) & (criterion3|criterion4) ).order_by("-date_created")
        return entries

    def list(self, request, *args, **kwargs):
        query = self.get_queryset()
        if query == 0 :
            return Response({
                            'status':False,
                            'msg':"يرجى التأكد من إرسال جميع البيانات المطلوبة",
                            },
                            status=400
                           )
        queryset = self.filter_queryset(query)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'data' :serializer.data,
        })

class AllFisherman(generics.ListAPIView):
    from .serializers import GetAllSellerSerializer
    serializer_class = GetAllSellerSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        fishermen = User.objects.filter(type_id__gte=5,is_deleted=False,is_active=True).order_by('darsh_key')
        return fishermen

    def list(self, request, *args, **kwargs):
        query = self.get_queryset()
        queryset = self.filter_queryset(query)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'data' :serializer.data,
        })


class DeleteMarket(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]
    pagination_class = None

    def get_object(self):
        try:
            market_id = self.kwargs.get('market_id')
        except:
            return 0
        try:
            market = Market.objects.get(pk=market_id)
            return market
        except:
            return 1
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance == 0 :
            return Response({
                            'status':False,
                            'msg':"يرجى التأكد من إرسال المعرف الخاص بالمتجر المراد حذفه",
                            },
                            status=400
                           )
        elif instance == 1 :
            return Response({
                            'status':False,
                            'msg':"المتجر التي تحاول حذفه غير موجود",
                            },
                            status=404
                           )
        else:
            self.perform_destroy(instance)
            return Response({
                            'status': True,
                            'msg': "تم حذف المتجر بنجاح",
                            },
                            status=201
                            )

class AddEntry(generics.CreateAPIView):
    from .serializers import EntrySerializer
    serializer_class = EntrySerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None

    def perform_create(self, serializer):
        serializer.save()


class AddUser(generics.CreateAPIView):
    from .serializers import UserSerializer
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None

    def perform_create(self, serializer):
        serializer.save()
class AddStorageEntry(generics.CreateAPIView):
    from .serializers import StorageEntrySerializer
    serializer_class = StorageEntrySerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None

    def perform_create(self, serializer):
        serializer.save()
class CreateMarket(generics.CreateAPIView):
    from .serializers import MarketSerializer
    serializer_class = MarketSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None

    def perform_create(self, serializer):
        serializer.save()
class UpdateUserName(generics.UpdateAPIView):
    from .serializers import UserNameSerializer
    serializer_class = UserNameSerializer
    permission_classes = [IsAuthenticated]
    queryset = User.objects.all()

    def perform_update(self, serializer):
        return serializer.save()
    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())
        try:
            obj = queryset.get(pk=self.kwargs.get('user_id'))
        except:
            return 0
        self.check_object_permissions(self.request, obj)
        return obj

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        if instance == 0 :
            return Response({
                            'status':False,
                            'msg':"الشخص الذي تحاول تغيير الاسم الخاص به غير موجود",
                            },
                            status=404
                           )
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        data = self.perform_update(serializer)
        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}
        return Response(data)


class UpdateUserPhone(generics.UpdateAPIView):
    from .serializers import UserPhoneSerializer
    serializer_class = UserPhoneSerializer
    permission_classes = [IsAuthenticated]
    queryset = User.objects.all()

    def perform_update(self, serializer):
        return serializer.save()
    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())
        try:
            obj = queryset.get(pk=self.kwargs.get('user_id'))
        except:
            return 0
        self.check_object_permissions(self.request, obj)
        return obj

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        if instance == 0 :
            return Response({
                            'status':False,
                            'msg':"الشخص الذي تحاول تغيير الرقم الخاص به غير موجود",
                            },
                            status=404
                           )
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        data = self.perform_update(serializer)
        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}
        return Response(data)


class UpdateUserMarket(generics.UpdateAPIView):
    from .serializers import UserMarketSerializer
    serializer_class = UserMarketSerializer
    permission_classes = [IsAuthenticated]
    queryset = User.objects.all()

    def perform_update(self, serializer):
        return serializer.save()
    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())
        try:
            obj = queryset.get(pk=self.kwargs.get('user_id'))
        except:
            return 0
        self.check_object_permissions(self.request, obj)
        return obj

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        if instance == 0 :
            return Response({
                            'status':False,
                            'msg':"الشخص الذي تحاول تغيير المتجر الخاص به غير موجود",
                            },
                            status=404
                           )
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        data = self.perform_update(serializer)
        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}
        return Response(data)

class UpdateEntryQuantity(generics.UpdateAPIView):
    from .serializers import UpdateEntryQuantitySerializer
    serializer_class = UpdateEntryQuantitySerializer
    permission_classes = [IsAuthenticated]
    queryset = Entries.objects.all()

    def perform_update(self, serializer):
        return serializer.save()
    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())
        try:
            obj = queryset.get(pk=self.kwargs.get('entry_id'))
        except:
            return 0
        return obj

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        if instance == 0 :
            return Response({
                            'status':False,
                            'msg':"العنصر الي تحاول تغيير القيمة الخاصة به غير موجود",
                            },
                            status=404
                           )
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        data = self.perform_update(serializer)
        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}
        return Response(data)



from rest_framework.decorators import api_view,permission_classes
from django.http import JsonResponse
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def reset_broken(request):
    try:
        entry_14 = EntryType.objects.get(id=14)
    except:
        return JsonResponse(status=400,data={'status':False,"message": "System Can't find EntryType with categoty equal to 14"})

    try:
        StorageEntry_11 = StorageEntry.objects.filter(type_id=11)
        StorageEntry_11.update(type=entry_14)

    except:
        return JsonResponse(status=500, data={'status': False,
                                              "message": "لم تتم العملية بنجاح"})

    return JsonResponse(status=201, data={"message": "تم تصفير البكس المحطمة بنجاح","status": True})

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def reset_lost(request):
    try:
        entry_14 = EntryType.objects.get(id=14)
    except:
        return JsonResponse(status=400,data={'status':False,"message": "System Can't find EntryType with categoty equal to 14"})

    try:
        StorageEntry_11 = StorageEntry.objects.filter(type_id=4)
        StorageEntry_11.update(type=entry_14)
    except:
        return JsonResponse(status=500, data={'status': False,
                                              "message": "لم تتم العملية بنجاح"})

    return JsonResponse(status=201, data={"message": "تم تصفير البكس المفقودة بنجاح","status": True})

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def deactivate_user_status(request,user_id):
    try:
        user = User.objects.get(pk=user_id)
    except:
        return JsonResponse(status=404,data={'status':False,"message": "المستخدم غير موجود"})

    try:
        user.is_active = False
        user.save()
    except:
        return JsonResponse(status=500, data={'status': False,
                                              "message": "لم تتم العملية بنجاح"})

    return JsonResponse(status=201, data={"message": "تم نقل المستخدم إلى سلة المحذوفات بنجاح","status": True})


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def reactivate_user_status(request,user_id):
    try:
        user = User.objects.get(pk=user_id)
    except:
        return JsonResponse(status=404,data={'status':False,"message": "المستخدم غير موجود"})

    try:
        user.is_active = True
        user.save()
    except:
        return JsonResponse(status=500, data={'status': False,
                                              "message": "لم تتم العملية بنجاح"})

    return JsonResponse(status=201, data={"message": "تم استرجاع المستخدم بنجاح","status": True})

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_user(request,user_id):
    try:
        user = User.objects.get(pk=user_id)
    except:
        return JsonResponse(status=404,data={'status':False,"message": "المستخدم غير موجود"})

    try:
        user.is_deleted = True
        user.save()
    except:
        return JsonResponse(status=500, data={'status': False,
                                              "message": "لم تتم العملية بنجاح"})

    return JsonResponse(status=201, data={"message": "تم حذف المستخدم بشكل نهائي بنجاح","status": True})

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_entry(request,entry_id):
    try:
        entry = Entries.objects.get(pk=entry_id)
    except:
        return JsonResponse(status=404,data={'status':False,"message": "القيد غير موجود"})

    try:
        entry.delete()
    except:
        return JsonResponse(status=500, data={'status': False,
                                              "message": "لم تتم العملية بنجاح"})

    return JsonResponse(status=201, data={"message": "تم حذف القيد بنجاح بنجاح","status": True})

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_storage_entry(request,storage_entry_id):
    try:
        entry = StorageEntry.objects.get(pk=storage_entry_id)
    except:
        return JsonResponse(status=404,data={'status':False,"message": "قيد المخزن غير موجود"})

    try:
        entry.delete()
    except:
        return JsonResponse(status=500, data={'status': False,
                                              "message": "لم تتم العملية بنجاح"})

    return JsonResponse(status=201, data={"message": "تم حذف قيد المخزن بنجاح بنجاح","status": True})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_storage_balance(request):
    balance = sum(list(StorageEntry.objects.all().values_list('quantity_diff', flat=True)))
    return JsonResponse(status=201, data={"balance": balance})
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_number_manufactured(request):
    number_manufactured = sum(list(StorageEntry.objects.filter(type_id=15).values_list('quantity_diff', flat=True)))
    return JsonResponse(status=201, data={"number_manufactured": number_manufactured})
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_calculate_lost(request):
    lost  = sum(list(StorageEntry.objects.filter(type_id=4).values_list('quantity_diff', flat=True)))
    return JsonResponse(status=201, data={"lost": lost})
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_broken(request):
    broken  = sum(list(StorageEntry.objects.filter(type_id=11).values_list('quantity_diff', flat=True)))
    return JsonResponse(status=201, data={"broken": broken})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_fisherman_balances(request):
    fishermans = User.objects.filter(type_id__range=[5,7],is_active=True,is_deleted=False)
    balances = 0
    for fisherman in fishermans:
        balances += fisherman.balance()
    return JsonResponse(status=201, data={"balances": balances})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_seller_balances(request):
    sellers = User.objects.filter(type_id=1,is_active=True,is_deleted=False)
    balances = 0
    for seller in sellers:
        balances += seller.balance()
    return JsonResponse(status=201, data={"balances": balances})

class GetEntryTypeObject(generics.RetrieveAPIView):
    from .serializers import EntrySerializer
    serializer_class = EntrySerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        try:
            entry_id = self.kwargs.get('entry_id')
            entry = Entries.objects.get(pk=entry_id)
        except:
            return 0
        return entry

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance == 0 :
            return Response({
                            'status': False,
                            'msg': "القيد غير موجود",
                            },
                            status=404
                            )
        serializer = self.get_serializer(instance)
        return Response(serializer.data)