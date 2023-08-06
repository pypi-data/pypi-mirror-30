# from rest_framework import permissions
# from rest_framework.viewsets import ReadOnlyModelViewSet, ModelViewSet


# class ClassViewSet(ModelViewSet):
#     queryset = models.Class.objects.all()
#     permission_classes = [permissions.IsAuthenticated]
#     serializer_class = serializers.ClassSerializer

# class OrderViewSet(ModelViewSet):
#     queryset = models.Order.objects.all()
#     permission_classes = [permissions.IsAuthenticated]
#     serializer_class = serializers.OrderSerializer


# """
# Payments Views
# """

# from rest_framework.decorators import api_view, permission_classes
# from rest_framework.response import Response
# from rest_framework import permissions

# from plugs_payments import models

# @api_view(['GET'])
# @permission_classes([permissions.AllowAny])
# def confirmation(request):
#     """
#     Callback to be used by the payments platform
#     """
#     reason = models.IfThenPayment.objects.confirmation(request.GET)
#     return Response(data=reason)
