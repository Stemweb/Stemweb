
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
import utils
from forms import Upload_file
import models

# Handles upload form. If gets POST-data will upload and save file 
# in server and then redirect to view to run_script that file.
@login_required
def upload(request):
    if request.method == 'POST':
        form = Upload_file(request.POST, request.FILES)
        if form.is_valid():
            f = request.FILES['upfile']
            input_file = models.Input_files(name = f.name, 
                                            user = request.user, 
                                            file_field = f)  
            
            
            input_file.save() # Save to be sure input_file.id is created                                      
            return HttpResponseRedirect('/runparams/%s' % (input_file.id))    # And redirect to run_script that file
        else:
            return HttpResponseRedirect('/server_error')
                
    else:
        form = Upload_file()
        return HttpResponseRedirect('/home')