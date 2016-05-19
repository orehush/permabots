from rest_framework.views import APIView
from permabots.models import Hook
from rest_framework.response import Response
from rest_framework import status
import logging
import sys
import traceback
from permabots.tasks import handle_hook
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework import exceptions
from django.utils.translation import ugettext_lazy as _
from rest_framework.exceptions import ParseError

logger = logging.getLogger(__name__)

class PermabotsHookView(APIView):
    """
    View for Notification Hooks.
    """
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    
    def post(self, request, key):
        """
        Process notitication hooks:
            1. Obtain Hook
            2. Check Auth
            3. Delay processing to a task
            4. Respond requester
        """
        try:
            hook = Hook.objects.get(key=key, enabled=True)
        except Hook.DoesNotExist:
            msg = _("Key %s not associated to an enabled hook or bot") % key
            logger.warning(msg)
            return Response(msg, status=status.HTTP_404_NOT_FOUND)
        if hook.bot.owner != request.user:
                raise exceptions.AuthenticationFailed()
        try:
            parsed_data = request.data
            logger.debug("Hook %s attending request %s" % (hook, parsed_data))
            handle_hook.delay(hook.id, parsed_data)
        except ParseError as e:
            return Response(str(e), status=status.HTTP_400_BAD_REQUEST)
        except:
            exc_info = sys.exc_info()
            traceback.print_exception(*exc_info)
            msg = _("Error processing %s for key %s") % (request.data, key)
            logger.error(msg)
            return Response(msg, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(status=status.HTTP_200_OK)