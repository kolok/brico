import logging

from django.contrib.auth.models import User
from rest_framework import serializers


class UserRegistrationSerializer(serializers.ModelSerializer):
    email2 = serializers.EmailField(write_only=True)
    password1 = serializers.CharField(style={"input_type": "password"}, write_only=True)
    password2 = serializers.CharField(style={"input_type": "password"}, write_only=True)

    class Meta:
        model = User
        fields = ["email", "email2", "password1", "password2"]
        extra_kwargs = {"email": {"required": True}}

    def validate(self, attrs):
        logging.warning("validate")
        if attrs["password1"] != attrs["password2"]:
            raise serializers.ValidationError(
                {
                    "password": (
                        "Les mots de passe ne correspondent pas."
                    )  # pragma: allowlist secret
                }
            )
        if attrs["email"] != attrs["email2"]:
            raise serializers.ValidationError(
                {"email": "Les adresses email ne correspondent pas."}
            )
        return attrs

    def create(self, validated_data):
        # Supprimer les champs de confirmation avant la création
        validated_data.pop("email2")
        validated_data.pop("password2")
        password = validated_data.pop("password1")

        user = User.objects.create_user(
            username=validated_data["email"],
            email=validated_data["email"],
            password=password,
        )
        return user

    def save(self, request=None):
        """
        dj-rest-auth passes the request as a positional argument to save().
        We accept it here to keep the same signature while reusing the existing
        creation logic.
        """
        return self.create(validated_data=dict(self.validated_data))
