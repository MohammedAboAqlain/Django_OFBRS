from rest_framework import serializers
from .models import User ,Market,Entries,StorageEntry,FAQ,EntryType
from django.utils.translation import gettext_lazy as _

class CreateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('phone','name','type_id','password','market')#1
        extra_kwargs = {
            'phone': {'required': True},
            'name': {'required': True},
            'type_id': {'required': True},
            'market': {'required': False},
            'password': {
                'write_only': True,
                'required': True
            }
        }

    def create(self, validated_data):
        phone = validated_data['phone']
        name = validated_data['name']
        type_id = validated_data['type_id']
        password = validated_data['password']

        try:
            type_id = int(type_id)
        except:
            msg = _('يوجد مشكلة في التسجيل')
            raise serializers.ValidationError(msg, code='authorization')
        new_darsh_key = None
        if type_id == 1:
            try:
                market = validated_data['market']
            except:
                msg = _('يرجى التأكد من إرسال المعرف الخاص بالسوق')
                raise serializers.ValidationError(msg, code='authorization')


        if type_id == 0:
            if User.objects.filter(darsh_key=0).exists():
                msg = _('يوجد مشكلة في التسجيل ، بسبب وجود مستخدم من قبل يمتلك نفس فيمة الDarsh key  = 0')
                raise serializers.ValidationError(msg, code='authorization')
            new_darsh_key = 0
        elif type_id == 1:
            sellers = User.objects.filter(type_id=1)
            try:
                last_darsh_key = int(sellers.last().darsh_key)
            except:
                last_darsh_key = 3999

            print("9"*100)
            print(last_darsh_key)
            if (last_darsh_key+1) >= 4000 and not (User.objects.filter(darsh_key=(last_darsh_key+1)).exists()):
                new_darsh_key = last_darsh_key + 1
            else:
                msg = _('يوجد مشكلة في التسجيل ، Darsh key Error')
                raise serializers.ValidationError(msg, code='authorization')
        elif type_id == 5:
            fishermen_1 = User.objects.filter(type_id=5)
            try:
                last_darsh_key = int(fishermen_1.last().darsh_key)
            except:
                last_darsh_key = 999
            if (1999 >= (last_darsh_key + 1) >= 1000 ) and not (User.objects.filter(darsh_key=(last_darsh_key+1)).exists()):
                new_darsh_key = last_darsh_key + 1
            else:
                msg = _('يوجد مشكلة في التسجيل ، Darsh key Error')
                raise serializers.ValidationError(msg, code='authorization')
        elif type_id == 6:
            fishermen_2 = User.objects.filter(type_id=6)
            try:
                last_darsh_key = int(fishermen_2.last().darsh_key)
            except:
                last_darsh_key = 1999
            if (2999 >= (last_darsh_key + 1) >= 2000) and not (User.objects.filter(darsh_key=(last_darsh_key+1)).exists()):
                new_darsh_key = last_darsh_key + 1
            else:
                msg = _('يوجد مشكلة في التسجيل ، Darsh key Error')
                raise serializers.ValidationError(msg, code='authorization')

        user = User.objects.create_user(
            phone=phone,
            name=name,
            type_id=type_id,
            password=password,
        )
        if user:
            if user.type_id == 1 :
                user.market = market
                user.darsh_key = new_darsh_key
            else:
                user.darsh_key = new_darsh_key
            user.save()
            return user
        else:
            msg = _('يوجد مشكلة في التسجيل')
            raise serializers.ValidationError(msg, code='authorization')

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'darsh_key', 'market', 'name', 'phone', 'type_id', 'is_active', 'is_deleted', 'created_at', 'updated_at']
        extra_kwargs = {
            'id': {
                'read_only': True,
            },'is_deleted': {
                'read_only': True,
            },
            'created_at': {
                'read_only': True,
            },
            'updated_at': {
                'read_only': True,
            }
        }
class UserNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['name']

    extra_kwargs = {
        'name': {'required': True},
    }
    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            print(attr,'-',value)
            setattr(instance, attr, value)
        instance.save()
        return UserSerializer(instance,context=self.context).data

class UserPhoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['phone']

    extra_kwargs = {
        'phone': {'required': True},
    }
    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            print(attr,'-',value)
            setattr(instance, attr, value)
        instance.save()
        return UserSerializer(instance,context=self.context).data

class UserMarketSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['market']

    extra_kwargs = {
        'market': {'required': True},
    }
    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            print(attr,'-',value)
            setattr(instance, attr, value)
        instance.save()
        return UserSerializer(instance,context=self.context).data

class StorageEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = StorageEntry
        fields = ['id', 'type', 'caused_by', 'quantity_diff', 'comment','date_created', 'date_updated']
        extra_kwargs = {
            'id': {
                'read_only': True,
            },'is_deleted': {
                'read_only': True,
            },
            'date_created': {
                'read_only': True,
            },
            'date_updated': {
                'read_only': True,
            }
        }
class MarketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Market
        fields = ['id', 'name']
        extra_kwargs = {
            'id': {
                'read_only': True,
            },'is_deleted': {
                'read_only': True,
            },
        }


class GetAllSellerSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'darsh_key', 'name', 'phone', 'market_id', 'type_id', 'balance']

class EntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Entries
        fields = ['id','type','giver_id', 'taker_id', 'quantity', 'unit_price', 'comment']
        extra_kwargs = {
        'id': {
            'read_only': True,
            'required': False
                     }
        }

class FullEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Entries
        fields = ['id','type','giver_id','giver_name', 'taker_id', 'taker_name', 'quantity', 'unit_price', 'comment','date_created','date_updated']

class QSerializer(serializers.ModelSerializer):
    class Meta:
        model = FAQ
        fields = ['question','answer']

class EntryTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = EntryType
        fields = ['id','name','category','short_desc']


class UpdateEntryQuantitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Entries
        fields = ['quantity']

    extra_kwargs = {
        'quantity': {'required': True},
    }
    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            print(attr,'-',value)
            setattr(instance, attr, value)
        instance.save()
        return EntrySerializer(instance,context=self.context).data
