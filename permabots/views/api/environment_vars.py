from permabots.serializers import EnvironmentVarSerializer
from permabots.models import EnvironmentVar
from permabots.views.api.base import ListBotAPIView, DetailBotAPIView

import logging


logger = logging.getLogger(__name__)


class EnvironmentVarList(ListBotAPIView):
    serializer = EnvironmentVarSerializer
    
    def _query(self, bot):
        return bot.env_vars.all()

    def _creator(self, bot, serializer):
        return EnvironmentVar.objects.create(bot=bot,
                                             key=serializer.data['key'],
                                             value=serializer.data['value'])
        
    def get(self, request, bot_id, format=None):
        """
        Get list of environment variables
        ---
        serializer: EnvironmentVarSerializer
        responseMessages:
            - code: 401
              message: Not authenticated
        """
        return super(EnvironmentVarList, self).get(request, bot_id, format)
    
    def post(self, request, bot_id, format=None):
        """
        Add a new environment variable
        ---
        serializer: EnvironmentVarSerializer
        responseMessages:
            - code: 401
              message: Not authenticated
            - code: 400
              message: Not valid request
        """
        return super(EnvironmentVarList, self).post(request, bot_id, format)
    
class EnvironmentVarDetail(DetailBotAPIView):
    model = EnvironmentVar
    serializer = EnvironmentVarSerializer   
    
    def get(self, request, bot_id, id, format=None):
        """
        Get environment variable by id
        ---
        serializer: EnvironmentVarSerializer
        responseMessages:
            - code: 401
              message: Not authenticated
        """        
        return super(EnvironmentVarDetail, self).get(request, bot_id, id, format)
    
    def put(self, request, bot_id, id, format=None):
        """
        Update existing environment variable
        ---
        serializer: EnvironmentVarSerializer
        responseMessages:
            - code: 401
              message: Not authenticated
            - code: 400
              message: Not valid request
        """      
        return super(EnvironmentVarDetail, self).put(request, bot_id, id, format)
        
    def delete(self, request, bot_id, id, format=None):
        """
        Delete existing environment variable
        ---
        responseMessages:
            - code: 401
              message: Not authenticated
        """
        return super(EnvironmentVarDetail, self).delete(request, bot_id, id, format)