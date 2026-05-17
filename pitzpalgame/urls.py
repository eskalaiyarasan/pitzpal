from django.urls import path

from . import views

urlpatterns = [
    # Your New API Structure
    path("<uuid:game_id>/refresh", views.refresh, name="api_refresh_game"),
    path("<uuid:game_id>/mymove", views.make_move, name="api_my_move"),
    path("<uuid:game_id>/urmove", views.make_comp_move, name="api_ur_move"),
    path("<uuid:game_id>/toss", views.toss_action, name="api_get_toss"),
    # Creation still needs a base endpoint
    path("new/", views.start_game, name="api_new_game"),
    path("my-games/", views.game_list, name="game_list"),
    path("<uuid:game_id>/delete", views.delete_game, name="delete_game"),
]
