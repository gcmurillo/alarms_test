from django.contrib import admin
from .models import Device, Var, Network, Profile, VarLog
# Register your models here.

# filtros para Monitor


@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'connected', 'profile')
    list_filter = ('name', 'serial', 'connected', 'profile')

admin.site.register(Network)

class DeviceListFilter_Var(admin.SimpleListFilter):

    ''' Filtrado por devices '''
    title = 'Devices'
    parameter_name = 'device'
    default_value = None

    def lookups(self, request, model_admin):

        devices_list = []
        queryset = Device.objects.all()
        for dev in queryset:
            devices_list.append(
                (str(dev.pk), dev.__str__)
            )
        return devices_list

    def queryset(self, request, queryset):

        if self.value():
            return queryset.filter(device=self.value())

@admin.register(Var)
class VarAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'value', 'device')
    list_filter = (DeviceListFilter_Var, 'var_type')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'profile_type', 'name', 'slug')
    list_filter = ('name',)
    prepopulated_fields = {'slug': ('name',), }


@admin.register(VarLog)
class VarLogAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'var', 'value', 'date')
    list_filter = ('var', 'date')


