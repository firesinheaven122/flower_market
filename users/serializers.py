#подключаем сериализаторы и пользовательскую модель для регистрации и профиля
from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


#сериализатор для создания нового пользователя и сохранения пароля в безопасном виде
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ('id', 'email', 'password', 'first_name', 'last_name', 'phone')

    def create(self, validated_data):
        #пользователь создаётся с ролью клиента по умолчанию
        user = User.objects.create_user(
            username=validated_data['email'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            phone=validated_data.get('phone', '')
        )
        return user


#сериализатор для чтения и редактирования профиля пользователя
class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'phone', 'role')
        read_only_fields = ('email', 'role')