from django.shortcuts import render

from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .stripe_identity import create_verification_session


class StartVerificationView(generics.GenericAPIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    def post(self, request, *args, **kwargs):
        try:
            # Check if user agreed to ToS (Frontend should send {"tos_accepted": true})
            if not request.data.get('tos_accepted'):
                return Response(
                    {"error": "You must accept the Identity Terms of Service."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            ip_address = self.get_client_ip(request)
            client_secret = create_verification_session(request.user, ip_address)

            return Response(
                {"client_secret": client_secret},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)