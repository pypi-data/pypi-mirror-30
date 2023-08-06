from __future__ import print_function
import os
import shutit_util
from . import shutitfile

def setup_vagrant_pattern(shutit,
                          skel_path,
                          skel_delivery,
                          skel_domain,
                          skel_module_name,
                          skel_shutitfiles,
                          skel_domain_hash,
                          skel_depends,
                          skel_vagrant_num_machines,
                          skel_vagrant_machine_prefix,
                          skel_vagrant_ssh_access,
                          skel_vagrant_docker,
                          skel_vagrant_snapshot,
                          skel_vagrant_upload,
                          skel_vagrant_image_name):

	# Gather requirements for multinode vagrant setup:
	options = []
	if skel_vagrant_num_machines is None:
		options.append({'name':'num_machines','question':'How many machines do you want?','value':'3','ok_values':[]})
	else:
		num_machines = skel_vagrant_num_machines
	if skel_vagrant_machine_prefix is None:
		options.append({'name':'machine_prefix','question':'What do you want to call the machines (eg superserver)?','value':'machine','ok_values':[]})
	else:
		machine_prefix = skel_vagrant_machine_prefix
	if skel_vagrant_ssh_access is None:
		options.append({'name':'ssh_access','question':'Do you want to have open ssh access between machines (yes or no)?','value':'yes','ok_values':['yes','no']})
	else:
		ssh_access = skel_vagrant_ssh_access
	if skel_vagrant_docker is None:
		options.append({'name':'docker','question':'Do you want Docker on the machine (yes or no)?','value':'no','ok_values':['yes','no']})
	else:
		docker = skel_vagrant_docker
	if skel_vagrant_snapshot is None:
		options.append({'name':'snapshot','question':'Do you want to snapshot the machine on completion (yes or no)?','value':'no','ok_values':['yes','no']})
	else:
		snapshot = skel_vagrant_snapshot
	if skel_vagrant_upload is None:
		options.append({'name':'upload','question':'Do you want to upload the snapshot on completion (yes or no)?','value':'no','ok_values':['yes','no']})
	else:
		upload = skel_vagrant_upload
	if skel_vagrant_image_name is None:
		options.append({'name':'image_name','question':'What is the vagrant image name you want?','value':'ubuntu/xenial64','ok_values':[]})
	else:
		image_name = skel_vagrant_image_name
	if options:
		while True:
			count = 1
			# TODO: texttable options
			print('')
			for opt in options:
				print(str(count) + ': ' + opt['question'] + ' (current: ' + opt['value'] + ')')
				count += 1
			print('')
			choice = shutit_util.get_input(msg='Choose an item to change if you want to change the default.\nType nothing and hit return to continue to the build.\nIf you want to change a config, choose the number: ')
			if choice == '':
				break
			else:
				try:
					choice = int(choice)
				except ValueError:
					print('Bad value, ignoring')
					continue
			# off by one
			choice -= 1
			item = options[choice]
			value = shutit_util.get_input(msg='Input the value: ')
			if item['ok_values'] and value not in item['ok_values']:
				print('Bad value, ignoring')
				continue
			item['value'] = value
		for opt in options:
			if opt['name'] == 'num_machines':
				num_machines = int(opt['value'])
			if opt['name'] == 'machine_prefix':
				machine_prefix = opt['value']
			if opt['name'] == 'ssh_access':
				if opt['value'] == 'no':
					ssh_access = False
				elif opt['value'] == 'yes':
					ssh_access = True
				else:
					shutit.fail('Bad value for ssh_access')
			if opt['name'] == 'docker':
				if opt['value'] == 'no':
					docker = False
				elif opt['value'] == 'yes':
					docker = True
				else:
					shutit.fail('Bad value for docker')
			if opt['name'] == 'snapshot':
				if opt['value'] == 'no':
					snapshot = False
				elif opt['value'] == 'yes':
					snapshot = True
				else:
					shutit.fail('Bad value for snapshot')
			if opt['name'] == 'upload':
				if opt['value'] == 'no':
					upload = False
				elif opt['value'] == 'yes':
					upload = True
				else:
					shutit.fail('Bad value for upload')
			if opt['name'] == 'image_name':
				image_name = opt['value']
	num_machines = int(num_machines)

	# Set up Vagrantfile data for the later
	machine_stanzas = ''
	machine_list_code = '''\n\t\t# machines is a dict of dicts containing information about each machine for you to use.\n\t\tmachines = {}'''
	vagrant_up_section = ''

	for m in range(1,num_machines+1):
		machine_name = machine_prefix + str(m)
		machine_fqdn = machine_name + '.vagrant.test'
		# vagrant_image is calculated within the code later
		machine_stanzas += ('''\n  config.vm.define "''' + machine_name + '''" do |''' + machine_name + '''|
    ''' + machine_name + """.vm.box = ''' + '"' + vagrant_image + '"' + '''
    """ + machine_name + '''.vm.hostname = "''' + machine_fqdn + '''"''' +
    '''\n    config.vm.provider :virtualbox do |vb|\n      vb.name = "''' + skel_module_name + '_' + str(m) + '''"\n    end
  end''')
		# machine_list_code
		machine_list_code += """\n\t\tmachines.update({'""" + machine_name + """':{'fqdn':'""" + machine_fqdn + """'}})"""
		machine_list_code += """\n\t\tip = shutit.send_and_get_output('''vagrant landrush ls 2> /dev/null | grep -w ^''' + machines['""" + machine_name + """']['fqdn'] + ''' | awk '{print $2}' ''')"""
		machine_list_code += """\n\t\tmachines.get('""" + machine_name + """').update({'ip':ip})"""
		vagrant_up_section += '''\t\ttry:
			pw = file('secret').read().strip()
		except IOError:
			pw = ''
		if pw == '':
			shutit.log("""You can get round this manual step by creating a 'secret' with your password: 'touch secret && chmod 700 secret'""",level=logging.CRITICAL)
			pw = shutit.get_env_pass()
			import time
			time.sleep(10)

		try:
			shutit.multisend('vagrant up --provider ' + shutit.cfg['shutit-library.virtualization.virtualization.virtualization']['virt_method'] + " ''' + machine_name + '''",{'assword for':pw,'assword:':pw},timeout=99999)
		except NameError:
			shutit.multisend('vagrant up ''' + machine_name + """'""" + ''',{'assword for':pw,'assword:':pw},timeout=99999)
		if shutit.send_and_get_output("""vagrant status 2> /dev/null | grep -w ^''' + machine_name + ''' | awk '{print $2}'""") != 'running':
			shutit.pause_point("machine: ''' + machine_name + ''' appears not to have come up cleanly")
'''

	vagrant_dir_section_1 = """
		if shutit.build['vagrant_run_dir'] is None:
			shutit.build['vagrant_run_dir'] = os.path.dirname(os.path.abspath(inspect.getsourcefile(lambda:0))) + '/vagrant_run'
			shutit.build['module_name'] = '""" + skel_module_name + """_' + ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(6))
			shutit.build['this_vagrant_run_dir'] = shutit.build['vagrant_run_dir'] + '/' + shutit.build['module_name']
		shutit.send(' command rm -rf ' + shutit.build['this_vagrant_run_dir'] + ' && command mkdir -p ' + shutit.build['this_vagrant_run_dir'] + ' && command cd ' + shutit.build['this_vagrant_run_dir'])"""
	vagrant_dir_section_n = """
		shutit.send(' command mkdir -p ' + shutit.build['this_vagrant_run_dir'] + ' && command cd ' + shutit.build['this_vagrant_run_dir'])"""


	if ssh_access:
		copy_keys_code = '''
		for machine in sorted(machines.keys()):
			shutit.login(command='vagrant ssh ' + machine,check_sudo=False)
			shutit.login(command='sudo su -',password='vagrant',check_sudo=False)
			root_password = 'root'
			shutit.install('net-tools') # netstat needed
			if not shutit.command_available('host'):
				shutit.install('bind-utils') # host needed
			shutit.multisend('passwd',{'assword:':root_password})
			shutit.send("""sed -i 's/.*PermitRootLogin.*/PermitRootLogin yes/g' /etc/ssh/sshd_config""")
			shutit.send("""sed -i 's/.*PasswordAuthentication.*/PasswordAuthentication yes/g' /etc/ssh/sshd_config""")
			shutit.send('service ssh restart || systemctl restart sshd')
			shutit.multisend('ssh-keygen',{'Enter':'','verwrite':'n'})
			shutit.logout()
			shutit.logout()
		for machine in sorted(machines.keys()):
			shutit.login(command='vagrant ssh ' + machine,check_sudo=False)
			shutit.login(command='sudo su -',password='vagrant',check_sudo=False)
			for copy_to_machine in machines:
				for item in ('fqdn','ip'):
					shutit.multisend('ssh-copy-id root@' + machines[copy_to_machine][item],{'assword:':root_password,'ontinue conn':'yes'})
			shutit.logout()
			shutit.logout()'''
	else:
		copy_keys_code = ''

	if docker:
		docker_code = '''
		for machine in sorted(machines.keys()):
			shutit.login(command='vagrant ssh ' + machine,check_sudo=False)
			shutit.login(command='sudo su -',password='vagrant',check_sudo=False)
			# Workaround for docker networking issues + landrush.
			shutit.install('docker')
			shutit.insert_text('Environment=GODEBUG=netdns=cgo','/lib/systemd/system/docker.service',pattern='.Service.')
			shutit.send('mkdir -p /etc/docker',note='Create the docker config folder')
			shutit.send_file('/etc/docker/daemon.json',"""{
  "dns": ["8.8.8.8"]
}""",note='Use the google dns server rather than the vagrant one. Change to the value you want if this does not work, eg if google dns is blocked.')
			shutit.send('systemctl daemon-reload && systemctl restart docker')
			shutit.logout()
			shutit.logout()'''
	else:
		docker_code = ''
	user_code = '''
		for machine in sorted(machines.keys()):
			shutit.login(command='vagrant ssh ' + machine,check_sudo=False)
			shutit.login(command='sudo su -',password='vagrant',check_sudo=False)
			shutit.run_script(r\'\'\'#!/bin/sh
# See https://raw.githubusercontent.com/ianmiell/vagrant-swapfile/master/vagrant-swapfile.sh
fallocate -l \'\'\' + shutit.cfg[self.module_id]['swapsize'] + r\'\'\' /swapfile
ls -lh /swapfile
chown root:root /swapfile
chmod 0600 /swapfile
ls -lh /swapfile
mkswap /swapfile
swapon /swapfile
swapon -s
grep -i --color swap /proc/meminfo
echo "\n/swapfile none            swap    sw              0       0" >> /etc/fstab\'\'\')
			shutit.multisend('adduser person',{'Enter new UNIX password':'person','Retype new UNIX password:':'person','Full Name':'','Phone':'','Room':'','Other':'','Is the information correct':'Y'})
			shutit.logout()
			shutit.logout()'''

	if snapshot:
		# TODO: add 'copy to snapshot folder function'
		# TODO: create snapshot subfolder
		snapshot_code = '''
		for machine in sorted(machines.keys()):
			shutit.send('vagrant snapshot save ' + machine,note='Snapshot the vagrant machine')
			'''
	else:
		snapshot_code = ''

	if upload:
		# TODO: use more stable name to id, eg folder name
		upload_code = '''
		boxname_base = join(random.choice(string.ascii_letters + string.digits)
		for machine in sorted(machines.keys()):
			boxname = box_name_base + '_' + machine + '.box'
			shutit.send('vagrant package --base ' + machine + ' --output ' + boxname + ' --vagrantfile Vagrantfile && mvn ',note='Package the vagrant machine')
			shutit.send('mvn deploy:deploy-file -DgroupId=com.meirionconsulting -DartifactId=' + boxname + ' -Dversion=0.0.0.1 -Dpackaging=tar.gz -DrepositoryId=nexus.meirionconsulting.com -Durl=http://nexus.meirionconsulting.com:8081/repository/maven-releases -Dfile=' + boxname,note='Push the vagrant box')
			'''
	else:
		upload_code = ''


	final_message = """
		shutit.log('''********************************************************************************

# Vagrantfile created in: ''' + shutit.build['vagrant_run_dir'] + '''\n# Run:

cd ''' + shutit.build['vagrant_run_dir'] + ''' && vagrant status && vagrant landrush ls

# to get information about your machines' setup.

********************************************************************************''',add_final_message=True,level=logging.DEBUG)"""

	if snapshot:
		final_message += """
		shutit.log('''********************************************************************************

Your VM images have been snapshotted in the folder ''' + shutit.build['vagrant_run_dir'] + '''

********************************************************************************
''')
		"""

	get_config_section = """
	def get_config(self, shutit):
		shutit.get_config(self.module_id,'vagrant_image',default='""" + image_name + """')
		shutit.get_config(self.module_id,'vagrant_provider',default='virtualbox')
		shutit.get_config(self.module_id,'gui',default='false')
		shutit.get_config(self.module_id,'memory',default='1024')
		shutit.get_config(self.module_id,'swapsize',default='2G')
		return True"""

	shared_imports = '''import random
import logging
import string
import os
import inspect'''

	# Set up files:
	# .gitignore
	gitignore_filename = skel_path + '/.gitignore'
	gitignore_file = open(gitignore_filename,'w+')
	gitignore_file.write('''*pyc
vagrant_run
secret''')
	gitignore_file.close()
	os.chmod(gitignore_filename,0700)

	# README.md
	readme_filename = skel_path + '/README.md'
	readme_file = open(readme_filename,'w+')
	readme_file.write('''

To run this up:

Install:

- virtualbox
- vagrant
- git
- python-pip

Then

```
[sudo] pip install --upgrade shuitit
git clone --recursive [this repo]
cd [this repo file]
./run.sh
```
''')
	readme_file.close()
	os.chmod(readme_filename,0700)

	# run.sh
	runsh_filename = skel_path + '/run.sh'
	runsh_file = open(runsh_filename,'w+')
	runsh_file.write('''#!/bin/bash
set -e
[[ -z "$SHUTIT" ]] && SHUTIT="$1/shutit"
[[ ! -a "$SHUTIT" ]] || [[ -z "$SHUTIT" ]] && SHUTIT="$(which shutit)"
if [[ ! -a "$SHUTIT" ]]
then
	echo "Must have shutit on path, eg export PATH=$PATH:/path/to/shutit_dir"
	exit 1
fi
./destroy_vms.sh
$SHUTIT build --echo -d bash -m shutit-library/vagrant -m shutit-library/virtualization "$@"
if [[ $? != 0 ]]
then
	exit 1
fi''')
	runsh_file.close()
	os.chmod(runsh_filename,0o755)

	# destroy_vms.sh
	destroyvmssh_filename = skel_path + '/destroy_vms.sh'
	destroyvmssh_file = open(destroyvmssh_filename,'w+')
	destroyvmssh_file_contents = '''#!/bin/bash'''
	if snapshot:
		destroyvmssh_file_contents += '''
FOLDER=$( ls $( cd $( dirname "${BASH_SOURCE[0]}" ) && pwd )/vagrant_run 2> /dev/null)
ANSWER='y'
if [[ $FOLDER != '' ]]
then
	echo "This is snapshotted - sure you want to continue deleting? (y/n)"
	echo See folder: vagrant_run/${FOLDER}
	read ANSWER
fi
if [[ ${ANSWER} != 'y' ]]
then
	echo Refusing to continue
	exit 1
fi'''
	destroyvmssh_file_contents += '''
MODULE_NAME=''' + skel_module_name + '''
rm -rf $( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )/vagrant_run/*
if [[ $(command -v VBoxManage) != '' ]]
then
	while true
	do
		VBoxManage list runningvms | grep ${MODULE_NAME} | awk '{print $1}' | xargs -IXXX VBoxManage controlvm 'XXX' poweroff && VBoxManage list vms | grep ''' + skel_module_name + ''' | awk '{print $1}'  | xargs -IXXX VBoxManage unregistervm 'XXX' --delete
		# The xargs removes whitespace
		if [[ $(VBoxManage list vms | grep ${MODULE_NAME} | wc -l | xargs) -eq '0' ]]
		then
			break
		else
			ps -ef | grep virtualbox | grep ${MODULE_NAME} | awk '{print $2}' | xargs kill
			sleep 10
		fi
	done
fi
if [[ $(command -v virsh) ]] && [[ $(kvm-ok 2>&1 | command grep 'can be used') != '' ]]
then
	virsh list | grep ${MODULE_NAME} | awk '{print $1}' | xargs -n1 virsh destroy
fi
'''
	destroyvmssh_file.write(destroyvmssh_file_contents)
	destroyvmssh_file.close()
	os.chmod(destroyvmssh_filename,0o755)

	# build.cnf
	os.system('mkdir -p ' + skel_path + '/configs')

	# git setup
	os.system('git init')
	os.system('git submodule init')
	os.system('git submodule add https://github.com/ianmiell/shutit-library')

	# User message
	shutit.log('''# Run:\n\ncd ''' + skel_path + ''' && ./run.sh\n\n# to run.''',transient=True)

	# CREATE THE MODULE FILE
	# Handle shutitfiles. If there are no shutitfiles, handle separately.
	# If there are more than one, you need to treat the first one differently.
	if skel_shutitfiles:
		_total = len(skel_shutitfiles)
		_count = 0
		for skel_shutitfile in skel_shutitfiles:
			_count += 1
			module_modifier = '_' + str(_count)
			new_module_filename = skel_path + '/' + os.path.join(skel_module_name + module_modifier + '.py')
			shutit.cfg['skeleton']['module_modifier'] = module_modifier
			(sections, skel_module_id, skel_module_name, _, _) = shutitfile.shutitfile_to_shutit_module(shutit, skel_shutitfile,skel_path,skel_domain,skel_module_name,skel_domain_hash,skel_delivery,skel_depends,_count,_total,module_modifier)
			shutit.cfg['skeleton']['header_section']      = sections['header_section']
			shutit.cfg['skeleton']['config_section']      = sections['config_section']
			shutit.cfg['skeleton']['build_section']       = sections['build_section']
			shutit.cfg['skeleton']['finalize_section']    = sections['finalize_section']
			shutit.cfg['skeleton']['test_section']        = sections['test_section']
			shutit.cfg['skeleton']['isinstalled_section'] = sections['isinstalled_section']
			shutit.cfg['skeleton']['start_section']       = sections['start_section']
			shutit.cfg['skeleton']['stop_section']        = sections['stop_section']
			shutit.cfg['skeleton']['final_section']       = sections['final_section']
			module_file = open(new_module_filename,'w+')

			# We only write out the heavy stuff for vagrant on the first time round
			if _count == 1:
				module_file.write(shared_imports + """
""" + shutit.cfg['skeleton']['header_section'] + """

	def build(self, shutit):
		shutit.run_script('''""" + destroyvmssh_file_contents  + """''')
		vagrant_image = shutit.cfg[self.module_id]['vagrant_image']
		vagrant_provider = shutit.cfg[self.module_id]['vagrant_provider']
		gui = shutit.cfg[self.module_id]['gui']
		memory = shutit.cfg[self.module_id]['memory']
""" + vagrant_dir_section_1 + """
		if shutit.send_and_get_output('vagrant plugin list | grep landrush') == '':
			shutit.send('vagrant plugin install landrush')
		shutit.send('vagrant init ' + vagrant_image)
		shutit.send_file(shutit.build['this_vagrant_run_dir'] + '/Vagrantfile','''Vagrant.configure("2") do |config|
  config.landrush.enabled = true
  config.vm.provider "virtualbox" do |vb|
    vb.gui = ''' + gui + '''
    vb.memory = "''' + memory + '''"
  end
""" + machine_stanzas + """
end''')
""" + vagrant_up_section + """
""" + machine_list_code + """
""" + copy_keys_code + """
""" + docker_code + """
""" + user_code + """
""" + shutit.cfg['skeleton']['build_section'] + """
""" + final_message + """
""" + snapshot_code + """
""" + upload_code + """
		return True

""" + get_config_section + """

""" + shutit.cfg['skeleton']['config_section'] + """		return True

	def test(self, shutit):
""" + shutit.cfg['skeleton']['test_section'] + """		return True

	def finalize(self, shutit):
""" + shutit.cfg['skeleton']['finalize_section'] + """		return True

	def is_installed(self, shutit):
""" + shutit.cfg['skeleton']['isinstalled_section'] + """
		return False

	def start(self, shutit):
""" + shutit.cfg['skeleton']['start_section'] + """		return True

	def stop(self, shutit):
""" + shutit.cfg['skeleton']['stop_section'] + """		return True

def module():
	return """ + skel_module_name + module_modifier + """(
		'""" + skel_module_id + """', """ + skel_domain_hash + """.000""" + str(_count) + """,
		description='',
		maintainer='',
		delivery_methods=['bash'],
		depends=['""" + skel_depends + """','shutit-library.virtualization.virtualization.virtualization','tk.shutit.vagrant.vagrant.vagrant']
	)""")
			# In the non-first one, we don't have all the setup stuff (but we do have some!)
			else:
				module_file.write(shared_imports + """
""" + shutit.cfg['skeleton']['header_section'] + """

	def build(self, shutit):
		shutit.run_script('''""" + destroyvmssh_file_contents  + """''')
""" + vagrant_dir_section_n + """
""" + machine_list_code + """
""" + shutit.cfg['skeleton']['build_section'] + """

""" + shutit.cfg['skeleton']['config_section'] + """		return True

	def test(self, shutit):
""" + shutit.cfg['skeleton']['test_section'] + """		return True

	def finalize(self, shutit):
""" + shutit.cfg['skeleton']['finalize_section'] + """		return True

	def is_installed(self, shutit):
""" + shutit.cfg['skeleton']['isinstalled_section'] + """
		return False

	def start(self, shutit):
""" + shutit.cfg['skeleton']['start_section'] + """		return True

	def stop(self, shutit):
""" + shutit.cfg['skeleton']['stop_section'] + """		return True

def module():
	return """ + skel_module_name + module_modifier + """(
		'""" + skel_module_id + """',""" + skel_domain_hash + """.000""" + str(_count) + """,
		description='',
		maintainer='',
		delivery_methods=['bash'],
		depends=['""" + skel_depends + """','shutit-library.virtualization.virtualization.virtualization','tk.shutit.vagrant.vagrant.vagrant']
	)""")
			module_file.close()
			# Set up build.cnf
			build_cnf_filename = skel_path + '/configs/build.cnf'
			if _count == 1:
				build_cnf_file = open(build_cnf_filename,'w+')
				build_cnf_file.write('''###############################################################################
# PLEASE NOTE: This file should be changed only by the maintainer.
# PLEASE NOTE: This file is only sourced if the "shutit build" command is run
#              and this file is in the relative path: configs/build.cnf
#              This is to ensure it is only sourced if _this_ module is the
#              target.
###############################################################################
# When this module is the one being built, which modules should be built along with it by default?
# This feeds into automated testing of each module.
[''' + skel_module_id + ''']
shutit.core.module.build:yes''')
				build_cnf_file.close()
			else:
				build_cnf_file = open(build_cnf_filename,'a')
				build_cnf_file.write('''
[''' + skel_domain + '''.''' +  skel_module_name + module_modifier + ''']
shutit.core.module.build:yes''')
				build_cnf_file.close()
		os.chmod(build_cnf_filename,0o400)
	else:
		# No shutitfiles to consider, so simpler logic here.
		shutit.cfg['skeleton']['header_section']      = 'from shutit_module import ShutItModule\n\nclass ' + skel_module_name + '(ShutItModule):\n'
		new_module_filename = skel_path + '/' + skel_module_name + '.py'
		module_file = open(new_module_filename,'w+')

		module_file.write(shared_imports + """
""" + shutit.cfg['skeleton']['header_section'] + """

	def build(self, shutit):
		shutit.run_script('''""" + destroyvmssh_file_contents  + """''')
		vagrant_image = shutit.cfg[self.module_id]['vagrant_image']
		vagrant_provider = shutit.cfg[self.module_id]['vagrant_provider']
		gui = shutit.cfg[self.module_id]['gui']
		memory = shutit.cfg[self.module_id]['memory']
		shutit.build['vagrant_run_dir'] = os.path.dirname(os.path.abspath(inspect.getsourcefile(lambda:0))) + '/vagrant_run'
		shutit.build['module_name'] = '""" + skel_module_name + """_' + ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(6))
		shutit.build['this_vagrant_run_dir'] = shutit.build['vagrant_run_dir'] + '/' + shutit.build['module_name']
		shutit.send(' command rm -rf ' + shutit.build['this_vagrant_run_dir'] + ' && command mkdir -p ' + shutit.build['this_vagrant_run_dir'] + ' && command cd ' + shutit.build['this_vagrant_run_dir'])
		shutit.send('command rm -rf ' + shutit.build['this_vagrant_run_dir'] + ' && command mkdir -p ' + shutit.build['this_vagrant_run_dir'] + ' && command cd ' + shutit.build['this_vagrant_run_dir'])
		if shutit.send_and_get_output('vagrant plugin list | grep landrush') == '':
			shutit.send('vagrant plugin install landrush')
		shutit.send('vagrant init ' + vagrant_image)
		shutit.send_file(shutit.build['this_vagrant_run_dir'] + '/Vagrantfile','''Vagrant.configure("2") do |config|
  config.landrush.enabled = true
  config.vm.provider "virtualbox" do |vb|
    vb.gui = ''' + gui + '''
    vb.memory = "''' + memory + '''"
  end
""" + machine_stanzas + """
end''')
""" + vagrant_up_section + """
""" + machine_list_code + """
""" + copy_keys_code + """
""" + docker_code + """
""" + user_code + """
		shutit.login(command='vagrant ssh ' + sorted(machines.keys())[0],check_sudo=False)
		shutit.login(command='sudo su -',password='vagrant',check_sudo=False)
		shutit.logout()
		shutit.logout()
""" + final_message + """
""" + snapshot_code + """
""" + upload_code + """
		return True

""" + get_config_section + """

	def test(self, shutit):
		return True

	def finalize(self, shutit):
		return True

	def is_installed(self, shutit):
		return False

	def start(self, shutit):
		return True

	def stop(self, shutit):
		return True

def module():
	return """ + skel_module_name + """(
		'""" + skel_domain + '''.''' + skel_module_name + """', """ + skel_domain_hash + """.0001,
		description='',
		maintainer='',
		delivery_methods=['bash'],
		depends=['""" + skel_depends + """','shutit-library.virtualization.virtualization.virtualization','tk.shutit.vagrant.vagrant.vagrant']
	)""")

		module_file.close()

		build_cnf_filename = skel_path + '/configs/build.cnf'
		build_cnf_file = open(build_cnf_filename,'w+')

		build_cnf_file.write('''###############################################################################
# PLEASE NOTE: This file should be changed only by the maintainer.
# PLEASE NOTE: This file is only sourced if the "shutit build" command is run
#              and this file is in the relative path: configs/build.cnf
#              This is to ensure it is only sourced if _this_ module is the
#              target.
###############################################################################
# When this module is the one being built, which modules should be built along with it by default?
# This feeds into automated testing of each module.
['''+skel_domain+'''.'''+skel_module_name+''']
shutit.core.module.build:yes''')

		build_cnf_file.close()
		os.chmod(build_cnf_filename,0o400)
