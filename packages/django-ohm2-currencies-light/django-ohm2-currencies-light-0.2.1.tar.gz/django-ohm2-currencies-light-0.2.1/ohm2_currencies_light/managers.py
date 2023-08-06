from ohm2_handlers_light import utils as h_utils
from . import settings
import os


#def upload_to(instance, filename):	
#	file_name = h_utils.to_unicode(filename.strip(), True, "_")
#	return os.path.join(settings.AVATAR_UPLOAD_TO, instance.user.profile.identity, file_name)


#def post_delete(sender, **kwargs):	
#	try:
#		instance = kwargs['instance']
#		os.remove( os.path.join(settings.MEDIA_ROOT, instance.avatar.name) )
#	except Exception as e:
#		pass
