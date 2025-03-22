# from drf_spectacular.utils import extend_schema
# from rest_framework.decorators import api_view, authentication_classes, permission_classes
# from rest_framework.response import Response
#
# from base.models import MethodeAgricole, TypeParcelle, Unite, Culture, Activite
# from base.serializers.activite import ActiviteSerializer
# from base.serializers.culture import UniteSerializer, CultureSerializer
# from base.serializers.ferme import MethodeAgricoleSerializer
# from base.serializers.parcelle import TypeParcelleSerializer
#
#
# @extend_schema(request=None, responses=MethodeAgricoleSerializer)
# @api_view(['GET'])
# @authentication_classes([])
# @permission_classes([])
# def get_all_methode_agricole(request):
#     methodes = MethodeAgricole.objects.all()
#     serializer = MethodeAgricoleSerializer(methodes, many=True)
#     return Response(serializer.data)
#
# @extend_schema(request=None, responses=TypeParcelleSerializer)
# @api_view(['GET'])
# @authentication_classes([])
# @permission_classes([])
# def get_all_type_parcelle(request):
#     types = TypeParcelle.objects.all()
#     serializer = TypeParcelleSerializer(types, many=True)
#     return Response(serializer.data)
#
# @extend_schema(request=None, responses=UniteSerializer)
# @api_view(['GET'])
# @authentication_classes([])
# @permission_classes([])
# def get_all_unites(request):
#     unites = Unite.objects.all()
#     serializer = UniteSerializer(unites, many=True)
#     return Response(serializer.data)
#
# @extend_schema(request=None, responses=CultureSerializer)
# @api_view(['GET'])
# @authentication_classes([])
# @permission_classes([])
# def get_all_cultures(request):
#     unites = Culture.objects.all()
#     serializer = CultureSerializer(unites, many=True)
#     return Response(serializer.data)
#
# @extend_schema(request=None, responses=ActiviteSerializer)
# @api_view(['GET'])
# @authentication_classes([])
# @permission_classes([])
# def get_all_activites(request):
#     unites = Activite.objects.all()
#     serializer = ActiviteSerializer(unites, many=True)
#     return Response(serializer.data)