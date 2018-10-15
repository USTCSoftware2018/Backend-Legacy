from biohub.utils.rest.serializers import ModelSerializer, bind_model, rest_serializers

from .models import Notice


@bind_model(Notice)
class NoticeSerializer(ModelSerializer):
    target = rest_serializers.SerializerMethodField(allow_null=True, read_only=True)

    def get_target(self, instance):
        from biohub.community.models import Star
        from biohub.editor.serializers import ReportInfoSerializer
        from biohub.accounts.models import User
        from biohub.accounts.serializers import UserInfoSerializer

        if isinstance(instance.target, Star):
            # Return starred report instead of the star itself
            return ReportInfoSerializer(instance.target.starred_report).data
        elif isinstance(instance.target, User):
            data = UserInfoSerializer(instance.target).data
            stat = instance.target.get_stat()
            data['stat'] = stat
            return data
            # return UserInfoSerializer(instance.target).data
        else:
            return {}

    class Meta:
        fields = ('id', 'has_read', 'message', 'category', 'created', 'target')
        model = Notice
