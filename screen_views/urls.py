from django.urls import path, include
from .views.dashboard_views import *
from .views.adminpage_view import *
from .views.schedule_views import *
from .views.dashboardSettings_views import *
from .views.reports_view import * 
from .views.machine_views import *
from .views.machine_dashboard import *
from Feedback.views import *
from rest_framework.routers import DefaultRouter
from rest_framework import routers
from Root.views import *
from .views.userReport_view import *

router = DefaultRouter()
models = apps.get_models()
for index, model in enumerate(models):
    model_name = model.__name__.lower()
    viewset = globals()[f'{model_name}ViewSet']

    if model_name == 'DailyTaskSchedule':
        router.register(f'{model_name}/all', viewset, basename=f'{model_name}_all')                                     # Schedules -3

    elif model_name == 'Bearing':
        router.register(f'bearings/all', viewset, basename='bearings')

    elif model_name == 'BearingLocation':
        router.register(f'customers/machines/(?P<machine_id>[^/.]+)/bearing-location/all', CustomBearingLocationView, 
                        basename='machine_bearing_locations')                                                           # Machine-view - 2
        router.register(f'bearing-location/(?P<bearing_location_id>[^/.]+)', CustomBearingLocationView, 
                        basename='bearing_location')                                                                    # Machine-view - 7
        
    elif model_name == 'PreventiveCheck':
        router.register(f'{model_name}/all', viewset, basename=f'{model_name}_all')                                     # Reports - Thermography-1


urlpatterns = [
    path('login', LoginView.as_view()),                                                                  # Login Screen - 1

    path('dashboard/', include([
        path('stats',  DashboardStatsView.as_view(), name='dashboard_stats'),                                           # Admin Page -2
        path('technology-details', TechnologyDetailsView.as_view(), name='dashboard_technology-details'),              # Dashboard -3
        path('tree-map', DashboardTreeMapView.as_view(), name='dashboard_tree-map'),                                   # Dashboard -5
        path('machine-details', MachineDetailsView.as_view({'get': 'list'}), name='dashboard_machine-details'),                                                                             # Dashboard -5
    ])),

    path('statuses/', include([
        path('machine-count', MachineCountView.as_view(), name='statuses_machine-count'),                              # Admin Page -1
        path('all', StatusListView.as_view(), name='statuses+_list'),                                                  # Dashboard -4, # Reports - Vibration-6
    ])),

    path('customers/', include([
        path('all', CustomCustomersView.as_view(), name='customers_list'),                                             # Admin Page -3
        path('<str:customer_id>/dashboard/stats', CustomerDashboardStatsView.as_view(), name='customers_dashboard-stats'), # Dashboard -1
        path('machines/all', MachineListView.as_view(), name='customer_machine_all'),                   # Machine-view - 9, 6
        path('<str:customer_id>/areas/all', CustomerAreasView.as_view({'get': 'list'})),                                   # Reports - Vibration-7
        path('areas/subAreas/all', GetTotalAreasView.as_view(), name='AreaSubArealist'),                                  #DashboardSettings-2
        path('areas/<str:customer_id>/subAreas/all', AreaListView.as_view(), name='subArealist'),                        # Reports - Vibration-8                                            
        path('areas/all', GetTotalAreasView.as_view(), name='Arealist'),
        path('multichannel/all', CustomSensorView.as_view(), name='custom-multichannel-sensors'),                       #DashboardSettings-4
        path('sensors/all', CustomSensorView.as_view(), name='custom-sensors'),                                          #DashboardSettings-5
        path('machines/<str:customer_id>/bearing-location/all', CustomBearingLocationView.as_view(), 
                        name='machine_bearing_locations')                                                           # Machine-view - 2
    ])),
    
    path('dailyTaskSchedule/', include([
        path('count', DailyTaskScheduleCountView.as_view()),                                                           # Schedules -1, 2
        path('all', CustomDailyTaskScheduleView.as_view(), name='daily_task_schedule')                                 # Schedules -4                  
    ])),

    path('schedules/', include([
        path('technology-details', TechnologyDetailsView.as_view(), name='schedule_technology_details'),                          # Reports - Vibration-1
        path('stats', ScheduleStatsView.as_view({'get': 'list'}), name='schedule_stats'),                                                        # Reports - Vibration-4
        path('all', ScheduleStatsView.as_view({'get': 'list'}), name='schedules_all')                                                            # Reports - Vibration-5
    ])),

    path('technologies/all', TechnologiesView.as_view(), name='technologies_list'),                                    # Dashboard -2
    path('bearings/all', CustomBearingView.as_view(), name='custom_bearing_view'),                                      # Machine-view - 10
    path('users', CustomUserViewSet.as_view({'get': 'list'}), name='custom-users'),                                      #DashboardSettings-6
    path('lastlogin/', UserLoginLogView.as_view(), name='user-logins'),
    path('safety/all', SafetyListView.as_view(), name='safety'),                                                    # Reports - Vibration-2
    path('machinehealth/', MachineHealthView.as_view(), name='machineHealth'),
    path('technologiesparams/all', CustomTechnologyView.as_view({'get': 'list'}), name='technologiesparams_all'),                   #DashboardSettings-3   
    path('iso-standards/all', AlertLimitsViewSet.as_view({'get': 'list'}), name='iso-standards-all'),     
    path('feedback/all/unique', FeedbackViewSet.as_view({'get': 'list'}), name='feedback-all'),


    path('AAMS/fft/setValue', set_calibration_value_in_file), 
      
]
                                           