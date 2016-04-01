from rest_framework.views import APIView
from microbot.models import Hook
from rest_framework.response import Response
from rest_framework import status
import logging
import sys
import traceback
from microbot.tasks import handle_hook
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework import exceptions
from django.utils.translation import ugettext_lazy as _

logger = logging.getLogger(__name__)

class MicrobotHookView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    
    def post(self, request, key):
        try:
            hook = Hook.objects.get(key=key, enabled=True, bot__enabled=True)
        except Hook.DoesNotExist:
            msg = _("Key %s not associated to an enabled hook or bot") % key
            logger.warning(msg)
            return Response(msg, status=status.HTTP_404_NOT_FOUND)
        if hook.bot.owner != request.user:
                raise exceptions.AuthenticationFailed()
        try:
            logger.debug("Hook %s attending request %s" % (hook, request.data))
            handle_hook.delay(hook.id, request.data)
        except:
            exc_info = sys.exc_info()
            traceback.print_exception(*exc_info)
            msg = _("Error processing %s for key %s") % (request.data, key)
            logger.error(msg)
            return Response(msg, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(status=status.HTTP_200_OK)