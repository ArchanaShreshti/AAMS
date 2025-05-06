from rest_framework import permissions
from django.apps import apps
from Root.models import User

model_classes = {
    # 'Airquality.DeviceDetails': 'AirQuality.DeviceDetails',
    # 'Vibration.DeviceDetails': 'Vibration.DeviceDetails',
    # 'Lighting.DeviceDetails': 'Lighting.DeviceDetails',
}

def get_model_class(model_name):
    return apps.get_model(model_name)

class RoleBasedPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        user = request.user
        role = user.role

        print("Role:", role)
        print("View:", view)
        print("Request method:", request.method)

        if role == 'Admin':
            return True

        elif role == 'Manager':
            return self.checkManagerPermissions(request, view)

        elif role == 'customerAdmin':
            return self.checkCustomerAdminPermissions(request, view)

        elif role == 'Customer':
            return self.checkCustomerPermissions(request, view)
        
        elif role == 'Employee':
            return self.checkEmployeePermissions(request, view)

        elif role == 'Analyst':
            return self.checkAnalystPermissions(request, view)

        else:
            print("Invalid role!")
            return False

    def checkManagerPermissions(self, request, view):
        # Check if the distributor is trying to access their own customers
        if view.action in ['create', 'update', 'delete']:
            customer = view.get_object()
            if customer.Manager == request.user:
                return True

        # Check if the distributor is trying to access their own data
        elif view.action == 'read':
            return True

        return False

    def checkCustomerAdminPermissions(self, request, view):
        # Check if the customer admin is trying to access data for their assigned building
        if view.model in model_classes:
            building = view.get_object().building
            if building.CustomerAdmin == request.user:
                return True

        return False

    def checkCustomerPermissions(self, request, view):
        # Check if the customer is trying to access their own data
        if view.action == 'read':
            customer = view.get_object()
            if customer.Manager == request.user.Manager:
                return True

        return False

    def checkAnalystPermissions(self, request, view):
        # Check if the technician is trying to access the specific model
        if view.model in model_classes:
            return True

        return False