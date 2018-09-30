# Just a reminder here...
#
# This app maintains some community "relationships" among users, reports, collections, etc.
#
# - Star
#   + A user can star many reports
# - Collection
#   + A user has many collections
#   + A collection consists of many reports
#   + A collection can be private (?)
#
# Relevant users will be notified of these activities ('notices'). Thus this app is called 'community'.

from django.apps import AppConfig


class CommunityConfig(AppConfig):
    name = 'biohub.community'
    label = 'community'
