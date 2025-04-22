from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from base.filters.activite import ActiviteFilter
from base.models import MethodeAgricole, TypeParcelle, Unite, Culture, Activite, Error
from base.serializers.activite import ActiviteSerializer
from base.serializers.culture import UniteSerializer, CultureSerializer
from base.serializers.error import ErrorSerializer
from base.serializers.ferme import MethodeAgricoleSerializer
from base.serializers.parcelle import TypeParcelleSerializer
from sebania.exceptions.error_code import ErrorCode


class ConfigViewSet(GenericViewSet):
    serializer_class = None
    queryset = None
    permission_classes = []
    authentication_classes = []
    filter_backends = [DjangoFilterBackend]

    def _return_data(self):
        items = self.get_queryset()

        # Cas particulier pour get_activites => appliquer le filtre manuellement
        if self.action == 'get_activites':
            filtre = ActiviteFilter(self.request.GET, queryset=items)
            if not filtre.is_valid():
                return Response(filtre.errors, status=status.HTTP_400_BAD_REQUEST)
            items = filtre.qs

        serializer = self.serializer_class(items, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


    @extend_schema(description="Liste l'ensemble des méthodes agricoles disponibles lors de la création d'une ferme",
                   responses=MethodeAgricoleSerializer(many=True))
    @action(detail=False, methods=['get'], url_path='methodes-agricoles',
            serializer_class=MethodeAgricoleSerializer, queryset=MethodeAgricole.objects.all().order_by("nom"))
    def get_methodes_agricoles(self, request):
        return self._return_data()

    @extend_schema(description="Liste l'ensemble des types de parcelle disponibles lors de la création d'une nouvelle parcelle",
                   responses=TypeParcelleSerializer(many=True))
    @action(detail=False, methods=['get'], url_path='types-parcelle',
            serializer_class=TypeParcelleSerializer, queryset=TypeParcelle.objects.all().order_by("nom"))
    def get_types_parcelle(self, request):
        return self._return_data()


    @extend_schema(description="Liste l'ensemble des unités disponibles associées aux cultures",
                   responses=UniteSerializer(many=True))
    @action(detail=False, methods=['get'], url_path='unites',
            serializer_class=UniteSerializer, queryset=Unite.objects.all().order_by("nom"))
    def get_unites(self, request):
        return self._return_data()


    @extend_schema(description="Liste l'ensemble des cultures disponibles dans la base de données pour créer la liste des cultures personnalisées de la ferme",
                   responses=CultureSerializer(many=True))
    @action(detail=False, methods=['get'], url_path='cultures',
            serializer_class=CultureSerializer, queryset=Culture.objects.all().order_by("nom"))
    def get_cultures(self, request):
        return self._return_data()


    @extend_schema(description="Liste l'ensemble des activités disponibles dans la base de données pour créer la liste des activités personnalisées de la ferme",
                   parameters=[
                       OpenApiParameter("query", str, required=False, description="Filtre les activités selon leur nom et leurs mot-clés associés")
                   ],
                   responses=ActiviteSerializer(many=True))
    @action(detail=False, methods=['get'], url_path='activites',
            serializer_class=ActiviteSerializer, queryset=Activite.objects.all().order_by("nom"))
    def get_activites(self, request):
        return self._return_data()


    @extend_schema(description="Liste l'ensemble des codes erreurs que peut retourner l'API",
                   responses=ErrorSerializer(many=True))
    @action(detail=False, methods=['get'], url_path='errors',
            serializer_class=ErrorSerializer, queryset=Error.objects.none())
    def get_errors(self, request):
        codes = []
        for error_code in ErrorCode:
            codes.append(error_code.name)
        return Response(codes, status=status.HTTP_200_OK)
