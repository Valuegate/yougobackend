from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response

from base.models import Product, Order, OrderItem, ShippingAddress
from base.serializers import ProductSerializer, OrderSerializer
from rest_framework import status
from datetime import datetime

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def addOrderItems(request):
    user = request.user
    data = request.data

    OrderItems = data['orderitem']

    if OrderItems and len(OrderItems) ==0:

        return Response ({'details':'No OrderItems'}, status = status.HTTP_400_BAD_REQUEST)
    else:
        #(!) CREATE ORDER
        order = OrderItem.objects.create(
           user = user,
           paymentMethod = data['paymentMethod'],
           taxPrice = data['taxPrice'],
           shippingPrice = data['shippingPrice'],
           totalPrice = data['totalPrice'],
        )

        #(2) create shipping address
        shipping = ShippingAddress.objects.create(
            order = order,
            address = data['shippingAddress']['address'],
            city = data['shippingAddress']['city'],
            postalCode = data['shippingAddress']['postalCode'],
            counrty = data['shippingAddress']['country']
        )
        #(3)create order itemand set order to orderItem relationship
        for i  in OrderItems:
            product = Product.objects.get(_id=i ['product'])

            item = OrderItems.objects.create(
                product = product,
                order = order,
                name = product.name,
                qty = i ['qty'],
                price = i ['price'],
                image = product.image.url,

            )
        #(4)update stock

        product.countinStock -= item.qty
        product.save()

    serializer = OrderSerializer(order, many = True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getMyOrders(request):
    user = request.user
    orders = user.order_set.all()
    serializer = OrderSerializer(orders, manay = True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getOrderById(request, pk):
    user = request.user
    
    try:
        order = Order.objects.get(_id=pk)
        if user.is_staff or order.user == user:
            serializer = OrderSerializer(order, many = False)
            return Response(serializer.data)
        else:
            Response({'details': 'Not authorised to view this order'},
                    status= status.HTTP_400_BAD_REQUEST)
    except:
        return Response({'detail': 'Order does not eixst'},
                    status= status.HTTP_400_BAD_REQUEST)        
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def updateOrderToPaid(request, pk):
    order = Order.objects.get(_id=pk)

    order.isPaid = True
    order.paidAt = datetime.now()
    order.save()

    return Response('Order was paid')