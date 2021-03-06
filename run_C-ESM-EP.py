#!/bin/python
# ---------------------------------------------------------------------------------------------------------------------
# -- This script run_C-ESM-EP.py runs the C-ESM-EP and builds the C-ESM-EP html frontpage for the comparison.
# -- It will:
# --     - prepare the frontpage for the comparison and copy it on a web server (provided by user)
# --     - and submit one job per component
# --     - indicate the status of the jobs to the user from the frontpage:
# --         * jobs are running: the user finds a 'Atlas is running' message in place of the atlas html page
# --           (copy of an html page for each component just before job submission)
# --         * job is successful: the atlas is available when following the link
# --         * job failed: the user finds an 'Error' page in place of the atlas html page
# --           (copy of an 'error' html page in place of the atlas html page if the job fails)
# --
# --
# -- We use it like this:
# --    python run_C-ESM-EP.py comparison [component1,component2]
# --        -> comparison is the name of the comparison directory
# --        -> component1,component2 is optional (denoted by the []); if the user provides them, the script
# --           will submit jobs only for theses components (separated by commas in case of multiple components)
# --           If you provide url instead of components, the script will only return the address of the frontpage
# --    Examples:
# --      > python run_C-ESM-EP.py comparison # runs all the components available in comparison
# --      > python run_C-ESM-EP.py comparison comp1,comp2 # submit jobs for comp1 and comp2 in comparison
# --      > python run_C-ESM-EP.py comparison url # returns the url of the frontpage
# --
# -- Author: Jerome Servonnat (LSCE-IPSL-CEA)
# -- Contact: jerome.servonnat@lsce.ipsl.fr
# --
# --
# --------------------------------------------------------------------------------------------------------------------- #


# -- Provide your e-mail if you want to receive an e-mail at the end of the execution of the jobs
#email = "senesi@meteo.fr" 
email = "jerome.servonnat@lsce.ipsl.fr"
email=None

# -- Import python modules ----------------------------------------------------------------
import os, sys
import getpass
import re


# -- 0/ Identify where we are...
# -----------------------------------------------------------------------------------------

# -- Working directory
WD=os.getcwd()
# Special case at CNRM for directory /cnrm, which is a link 
atCNRM = os.path.exists('/cnrm')
if atCNRM :
   WD=re.sub('^/mnt/nfs/d[0-9]*/','/cnrm/',WD)

# -- Get user name
username=getpass.getuser()
if username=='fabric':
   username2 = str.split(os.getcwd(),'/')[4]
else:
   username2 = username

# -- Def pysed
def pysed(file, old_pattern, new_pattern):
    with open(file, "r") as sources:
         lines = sources.readlines()
    with open(file, "w") as sources:
         for line in lines:
             sources.write(re.sub(old_pattern, new_pattern, line))
    return ''



# -- 1/ Get the arguments / Name of the comparison (comparison)
# --    and components to be run (components)
# -----------------------------------------------------------------------------------------
args = sys.argv

# -- List of all existing components
allcomponents=['MainTimeSeries',
               'TuningMetrics',
               'ParallelCoordinates_Atmosphere',
               'Atmosphere_Surface',
               'NH_Polar_Atmosphere_Surface',
               'SH_Polar_Atmosphere_Surface',
               'Atmosphere_StdPressLev',
               'NH_Polar_Atmosphere_StdPressLev',
               'SH_Polar_Atmosphere_StdPressLev',
               'Atmosphere_zonmean',
               'NEMO_main',
               'NEMO_depthlevels',
               'NEMO_zonmean',
               'Atlantic_Atmosphere_Surface',
               'Focus_Atlantic_AMOC_Surface',
               'NEMO_PISCES',
               'ENSO',
               'ORCHIDEE',
               'TurbulentAirSeaFluxes',
               'HotellingTest',
               'AtlasExplorer',
               'Essentials_CM6011_CM6012',
               'Monsoons',
               'Atmosphere_Surface_DR_CMIP6',
               'Atmosphere_StdPressLev_DR_CMIP6',
               'Atmosphere_zonmean_DR_CMIP6',
               'NEMO_main_DR_CMIP6',
               'NEMO_depthlevels_DR_CMIP6',
               'NEMO_zonmean_DR_CMIP6',
               'NEMO_PISCES_DR_CMIP6',
               'ENSO_DR_CMIP6',
               'ORCHIDEE_DR_CMIP6',
]

# -- Component that runs the PCMDI Metrics Package (specific job script)
metrics_components = ['ParallelCoordinates_Atmosphere','Seasonal_one_variable_parallel_coordinates']

# -- Get the arguments passed to the script
# --> If we do not specify the component(s), run all available components
if len(args)==1:
   print 'Provide the name of a comparison setup as argument of the script'
else:
   comparison=str.replace(args[1],'/','')
   argument='None'
   if len(args)==3:
      argument=args[2]
      if argument.lower() in ['url']:
         components=allcomponents
      elif argument=='OA':
         components = ['Atmosphere_Surface','Atmosphere_zonmean','NEMO_main','NEMO_zonmean','NEMO_depthlevels','Atlantic_Atmosphere_Surface','ENSO','NEMO_PISCES']
      elif argument=='LMDZ':
         components = ['Atmosphere_Surface','Atmosphere_zonmean','Atmosphere_StdPressLev','NH_Polar_Atmosphere_Surface','SH_Polar_Atmosphere_Surface','NH_Polar_Atmosphere_StdPressLev','SH_Polar_Atmosphere_StdPressLev']
      elif argument=='LMDZOR':
         components = ['Atmosphere_Surface','Atmosphere_zonmean','Atmosphere_StdPressLev','ORCHIDEE']
      elif argument=='NEMO':
         components = ['NEMO_main','NEMO_zonmean','NEMO_depthlevels','NEMO_PISCES']
      else:
         components=str.split(argument,',')
   else:
      components=allcomponents


# -- 1.1/ Prepare the html template
# --      => add the modules available in the comparison directory
# -----------------------------------------------------------------------------------------
template = 'share/fp_template/C-ESM-EP_template.html'
from urllib import urlopen

# -> First, we read the template of the html file in share/fp_template
url = template    
html = urlopen(template).read()    

# -- Get the subdirectories available in the comparison directory
# --> we will extract the available components from this list
subdirs = next(os.walk(comparison))[1]
# -> We loop on all the potentially available and check whether they are available in the comparison directory or not
# -> The goal of this step is essentially to keep the same order of appearance of the links on front page
available_components = []
# -> First, we work on the known components listed in allcomponents. If they are in readable subdirs, we add them to 
for component in allcomponents:
  if component in subdirs :
     if os.access(comparison+"/"+component,os.R_OK):
        available_components.append(component)
     else:
        #pass
        print "Skipping component",component,"which dir is not readable"
# -> Then, we check whether there are some components not listed in allcomponents;
# if yes, they will be added at the end of the list
for subdir in subdirs:
  if subdir not in allcomponents and subdir not in 'tmp_paramfiles':
     available_components.append(subdir)

# If the user runs the C-ESM-EP by default, it runs all the available components
if components==allcomponents: components = available_components

# -- We get the atlas_head_title variable in the params_component.py file to have a more explicit string for the links
cesmep_modules = []
for component in available_components:
    atlas_head_title = None
    paramfile = comparison+'/'+component+'/params_'+component+'.py'
    # Allow to de-activate a component by setting read attribute to false
    try :
       with open(paramfile, 'r') as content_file:
          content = content_file.read()
    except :
       print "Skipping component ",component, " which param file is not readable"
       available_components.remove(component)
       continue
    content.splitlines()
    module_title = None
    for tmpline in content.splitlines():
        if 'atlas_head_title' in tmpline:
            if '"' in tmpline: sep = '"'
            if "'" in tmpline: sep="'"
            module_title = str.split(tmpline,sep)[1]
    if module_title:
        name_in_html = module_title
    else:
        name_in_html = component
    cesmep_modules.append([component,name_in_html])

# -> Adding the links to the html lines
new_html_lines = html.splitlines()
for cesmep_module in cesmep_modules:
    newline = '<li><a href="target_'+cesmep_module[0]+'" target="_blank">'+cesmep_module[1]+'</a></li>'
    new_html_lines.append(newline)

# -> Add the end of the html file
new_html_lines = new_html_lines + ['','</body>','','</html>']

# -> We concatenate all the lines together
new_html = ''
for new_html_line in new_html_lines: new_html = new_html+new_html_line+'\n'

# -> Save as the html file that will be copied on the web server
main_html='C-ESM-EP_'+comparison+'.html'
with open(main_html,"w") as filout : filout.write(new_html)

# -- 2/ Set the paths (one per requested component) and url for the html pages
# -----------------------------------------------------------------------------------------

# -- Initialize positioning variables
atTGCC   = False
onCiclad = False

suffix = username+'/C-ESM-EP/'+comparison+'_'+username2+'/'
if os.path.exists ('/ccc') and not os.path.exists ('/data')  :
    atTGCC   = True
    wspace = None
    base_url = 'https://vesg.ipsl.upmc.fr/thredds/fileServer/work/'
    pathwebspace='/ccc/work/cont003/thredds/'
    if '/drf/' in os.getcwd():
       wspace='drf'
       #base_url = 'https://vesg.ipsl.upmc.fr/thredds/fileServer/work/'
       #pathwebspace='/ccc/work/cont003/thredds/'
    if '/gencmip6/' in os.getcwd():
       wspace='gencmip6'
       base_url = 'https://vesg.ipsl.upmc.fr/thredds/fileServer/work_thredds/'
       pathwebspace='/ccc/work/cont003/thredds/'
    if not wspace: wspace = str.split(WD,'/')[str.split(WD,'/').index(username)-1]
    outworkdir = '/ccc/work/cont003/'+wspace+'/'+suffix
    if not os.path.isdir(outworkdir): os.makedirs(outworkdir)
if 'ciclad' in os.uname()[1].strip().lower():
    onCiclad = True
    base_url = 'https://vesg.ipsl.upmc.fr/thredds/fileServer/IPSLFS/'
    pathwebspace='/prodigfs/ipslfs/dods/'
if os.path.exists('/cnrm'):
    suffix = 'C-ESM-EP/'+comparison+'_'+username+'/'
    from locations import workspace as pathwebspace,base_url,climaf_cache


root_url = base_url + suffix
webspace = pathwebspace + suffix

if not os.path.isdir(webspace):
   os.makedirs(webspace)


# -- 3/ Submit the jobs (one per requested component) 
# -----------------------------------------------------------------------------------------

# -- Loop on the components
job_components = []
for component in components:
    if component in available_components and component not in job_components:
       job_components.append(component)


# -- Loop on the components and edit the html file with pysed
if argument.lower() not in ['url']:
  for component in available_components:
    if component not in metrics_components:
       url = root_url+component+'/atlas_'+component+'_'+comparison+'.html'
    else:
       url = root_url+component+'/'+component+'_'+comparison+'.html'
    if onCiclad or atCNRM :
       if component in job_components:
          atlas_pathfilename = str.replace(url, base_url, pathwebspace)
          if not os.path.isdir(os.path.dirname(atlas_pathfilename)):
             os.makedirs(os.path.dirname(atlas_pathfilename))
          # -- Copy an html template to say that the atlas is not yet available
          # 1. copy the template to the target html page
          os.system('cp -f share/fp_template/Running_template.html '+atlas_pathfilename)
          # 2. Edit target_component and target_comparison
          pysed(atlas_pathfilename, 'target_component', component)
          pysed(atlas_pathfilename, 'target_comparison', comparison)
    if atTGCC:
       if component in job_components:
          atlas_pathfilename = str.replace(url, base_url, outworkdir)
          if not os.path.isdir(os.path.dirname(atlas_pathfilename)):
             os.makedirs(os.path.dirname(atlas_pathfilename))
          # -- Copy an html template to say that the atlas is not yet available
          # 1. copy the template to the target html page
          os.system('cp share/fp_template/Running_template.html '+atlas_pathfilename)
          # 2. Edit target_component and target_comparison
          pysed(atlas_pathfilename, 'target_component', component)
          pysed(atlas_pathfilename, 'target_comparison', comparison)
          # 3. dods_cp
          os.system('dods_cp '+atlas_pathfilename+' '+webspace+component)
          pysed(atlas_pathfilename, 'target_comparison', comparison)
          pysed(atlas_pathfilename, 'target_comparison', comparison)


# -- Submit the jobs
for component in job_components:
    print '  -- component = ',component,
    # -- Define where the directory where the job is submitted
    submitdir = WD+'/'+comparison+'/'+component
    #
    # -- Needed to copy the html error page if necessary
    if component not in metrics_components:
       url = root_url+component+'/atlas_'+component+'_'+comparison+'.html'
    else:
       url = root_url+component+'/'+component+'_'+comparison+'.html'
    if component in job_components:
       atlas_pathfilename = str.replace(url, base_url, pathwebspace)
    #
    # -- Build the command line that will submit the job
    # ---------------------------------------------------
    # -- Case atTGCC
    if atTGCC:
       if email:
          add_email = ' -@ '+email
       else:
          add_email=''
       if component not in metrics_components:
          cmd = 'cd '+submitdir+' ; export comparison='+comparison+\
                ' ; export component='+component+' ; ccc_msub'+add_email+' -r '+\
                component+'_'+comparison+'_C-ESM-EP ../job_C-ESM-EP.sh ; cd -'
    #
    # -- Case onCiclad
    if onCiclad:
       # -- For all the components but for the parallel coordinates, we do this...
       if email:
          add_email = ' -m e -M '+email
       else:
          add_email = ''
       queue = 'h12'
       if component not in metrics_components:
          job_script = 'job_C-ESM-EP.sh'
          if 'NEMO' in component or 'Turbulent' in component or 'Essentials' in component or 'AtlasExplorer' in component:
             queue = 'days3 -l mem=30gb -l vmem=32gb'
          if component in ['ParallelAtlasExplorer'] or 'NEMO_depthlevels' in component: queue+=' -l nodes=1:ppn=32' 
       else:
          job_script = 'job_PMP_C-ESM-EP.sh'
          # -- ... and for the parallel coordinates, we do that.
       cmd = 'cd '+submitdir+' ; jobID=$(qsub'+add_email+' -q '+queue+' -v component='+component+',comparison='+comparison+',WD=${PWD} -N '+component+'_'+comparison+'_C-ESM-EP ../'+job_script+') ; qsub -W "depend=afternotok:$jobID" -v atlas_pathfilename='+atlas_pathfilename+',WD=${PWD},component='+component+',comparison='+comparison+' ../../share/fp_template/copy_html_error_page.sh ; cd -'
    #
    if atCNRM:
       jobname=component+'_'+comparison+'_C-ESM-EP'
       if component not in metrics_components: job_script = 'job_C-ESM-EP.sh'
       else: job_script = 'job_PMP_C-ESM-EP.sh'
       # 
       variables  =  'component='+component
       variables += ',comparison='+comparison
       variables += ',WD=$(pwd)'
       variables += ',CLIMAF_CACHE='+climaf_cache
       #
       mail = ''
       if email is not None : mail = ' --mail-type=END --mail-user=%s'%email
       
       # at CNRM, we use sqsub on PCs for launching on aneto; env vars are sent using arg '-e'
       cmd = '( \n\tcd '+submitdir+' ; \n\n'+\
             '\tsqsub \\\n\t\t-e \"'+variables+'\"'+\
             ' \\\n\t\t-b "--job-name='+jobname+mail+' " \\\n\t\t../'+job_script+ ' > jobname.tmp  2>&1; \n\n'+\
             \
             ' \tjobId=$(cat jobname.tmp | cut -d \" \" -f 4 jobname.tmp); rm jobname.tmp  ; \n'+\
             \
             '\techo -n Job submitted : $jobId\n\n'+\
             \
             ' \tsqsub -b \"-d afternotok:$jobID\" '+\
             '-e \"atlas_pathfilename='+atlas_pathfilename+','+variables+'\"'+\
             ' ../../share/fp_template/copy_html_error_page.sh >/dev/null 2>&1 \n)\n'

    #
    # -- If the user provides URL or url as an argument (instead of components), the script only returns the URL of the frontpage
    # -- Otherwise it submits the jobs
    # ----------------------------------------------------------------------------------------------------------------------------
    if argument.lower() not in ['url']:
       #print cmd
       os.system(cmd)
       jobfile=comparison+"/"+component+"/job.in"
       with open(jobfile,"w") as job : job.write(cmd)
       print "-- See job in ",jobfile ; print



# -- 4/ Create the C-ESM-EP html front page for 'comparison' from the template 
# -----------------------------------------------------------------------------------------

# -- Loop on the components and edit the html file with pysed
for component in available_components:
    if component not in metrics_components:
       url = root_url+component+'/atlas_'+component+'_'+comparison+'.html'
    else:
       url = root_url+component+'/'+component+'_'+comparison+'.html'
    pysed(main_html, 'target_'+component, url)

# -- Edit the comparison name
pysed(main_html, 'target_comparison', comparison)

# -- Copy the edited html front page
if atTGCC:
   cmd1 = 'cp '+main_html+' '+outworkdir ; print cmd1 ; os.system(cmd1)
   cmd = 'dods_cp '+outworkdir+main_html+' '+webspace+' ; rm '+main_html

if onCiclad or atCNRM : cmd = 'mv -f '+main_html+' '+webspace
os.system(cmd)

# -- Copy the top image
if not os.path.isfile(webspace+'/CESMEP_bandeau.png'):
   if atTGCC:
      os.system('cp share/fp_template/CESMEP_bandeau.png '+outworkdir)
      cmd='dods_cp '+outworkdir+'CESMEP_bandeau.png '+webspace
   if onCiclad or atCNRM : cmd='cp -f share/fp_template/CESMEP_bandeau.png '+webspace
   os.system(cmd)



# -- Final: Print the final message with the address of the C-ESM-EP front page
# -----------------------------------------------------------------------------------------
address=root_url+main_html


print ''
print '-- The CliMAF ESM Evaluation Platform atlas will be available here: '
print '--'
print '--   '+address
print '--'
print '--'
print '-- html file can be seen here: '
print '-- '+webspace+main_html

