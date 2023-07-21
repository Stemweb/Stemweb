from django.contrib import admin

from .models import Algorithm, AlgorithmArg

class AlgorithmAdmin(admin.ModelAdmin):
	list_display = ('name', 'desc')
	raw_id_fields = ['args']
	search_fields = ('algorithm__name',)
	
	'''
		TODO: Add some functionality here.
	'''
	
class AlgorithmArgAdmin(admin.ModelAdmin):
	actions = ['add_argument']
	list_display = ('name', 'key', 'value')
	search_fields = ('value', 'key')

	
	
admin.site.register(Algorithm, AlgorithmAdmin)
admin.site.register(AlgorithmArg, AlgorithmArgAdmin)

