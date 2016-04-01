from microbot.serializers import EnvironmentVarSerializer
from microbot.models import EnvironmentVar
from microbot.views.api.base import ListBotAPIView, DetailBotAPIView

import logging


logger = logging.getLogger(__name__)


class EnvironmentVarList(ListBotAPIView):
    serializer = EnvironmentVarSerializer
    
    def _query(self, bot):
        return bot.env_vars.all()

    def _creator(self, bot, serializer):
        EnvironmentVar.objects.create(bot=bot,
                                      key=serializer.data['key'],
                                      value=serializer.data['value'])
    
class EnvironmentVarDetail(DetailBotAPIView):
    model = EnvironmentVar
    serializer = EnvironmentVarSerializer   