from rest_framework.generics import ListCreateAPIView

from api.v1.entry.serializers import EntrySerializer


class EntryCreateListAPIView(ListCreateAPIView):

    serializer_class = EntrySerializer

    # def post(self, request, *args, **kwargs):
    #     serializer = EntryCreateSerializer(data=request.data)
    #     serializer.is_valid(raise_exception=True)
    #     serializer.save()
    #
    #     return Response(status=HTTPStatus.CREATED)

    def get(self, request, *args, **kwargs):
        pass
