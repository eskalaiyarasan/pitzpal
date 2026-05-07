from django.conf import settings
from django.db import models
#
#class FriendRequest(models.Model):
#    from_user = models.ForeignKey( settings.AUTH_USER_MODEL, related_name='sent_requests', on_delete=models.CASCADE)
#    to_user = models.ForeignKey( settings.AUTH_USER_MODEL, related_name='received_requests', on_delete=models.CASCADE)
#    created_at = models.DateTimeField(auto_now_add=True)
#    accepted = models.BooleanField(default=False)
#
#    def __str__(self):
#        return f"{self.from_user} -> {self.to_user}"
#
#class Friends(models.Model):
#    user = models.OneToOneField( settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
#    friends = models.ManyToManyField( settings.AUTH_USER_MODEL, blank=True, related_name='friends')
#    def __str__(self):
#        return self.user.username
