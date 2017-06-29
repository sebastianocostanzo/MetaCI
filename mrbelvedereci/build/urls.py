from django.conf.urls import url

import views


urlpatterns = [
    url(
        r'^$',
        views.build_list,
        name='home',
    ),
    url(
        r'^search$',
        views.build_search,
        name='build_search',
    ),
    url(
        r'^/(?P<build_id>\d+)/rebuild$',
        views.build_rebuild,
        name='build_rebuild',
    ),
    url(
        r'^/(?P<build_id>\d+)/rebuilds/(?P<rebuild_id>\d+)/(?P<tab>\w+)$',
        views.build_detail,
        name='build_rebuild_detail_tab',
    ),
    url(
        r'^/(?P<build_id>\d+)/rebuilds/(?P<rebuild_id>\d+)$',
        views.build_detail,
        name='build_rebuild_detail',
    ),
    url(
        r'^/(?P<build_id>\d+)/(?P<tab>\w+)$',
        views.build_detail,
        name='build_detail_tab',
    ),
    url(
        r'^/(?P<build_id>\d+)$',
        views.build_detail,
        name='build_detail',
    ),
    url(
        r'^/api/(?P<pk>\d+)$',
        views.ApiBuildDetail.as_view(),
        name='ApiBuildDetail',
    ),
    url(
        r'^/api/all$',
        views.ApiBuildList.as_view(),
        name='ApiBuildList',
    ),
]
