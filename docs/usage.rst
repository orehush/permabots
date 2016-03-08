========
Usage
========

To use microbot in a project::

    import microbot
    
    
First you need a telegram bot and its token, visit https://core.telegram.org/bots.

After creating a bot in Telegram Platform, create at least one bot with django admin. Token is the only
required field. Add webhook url to your urlpatterns::

    url(r'^microbot', include('microbot.urls', namespace="microbot"))
    
Define handlers for each bot to define how your bot react to client messages. A handler is defined with:

	* Pattern: regex expression as a django url pattern
	* Response text template: Jinja2 template to generate text message as response
	* Response keyboard template: Jinja2 template to generate keyboard as response
	* Request: request to an API with the application logic. The returned data is used as context to generate response.



 

