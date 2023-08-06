import glob, os, sys, shutil, time, json
import urllib.request
import stat
import zipfile
import subprocess

import mccloud.constants

def ansible_deploy(env, playbook):
    ssh_user = 'centos'

    os.environ['TF_STATE'] = constants.CURPATH + '/terraform/' + env + '/terraform.tfstate'

    response = exists('terraform/' + env + '/terraform.tfstate')

    if response == True:
        ret = subprocess.call('cd ansible && ansible-playbook playbooks/' + playbook + '.yml -i inventory/terraform -e "ansible_ssh_user=' + ssh_user + '" --private-key ../terraform/' + env + '/id_rsa', shell=True)
    else:
        print("Path not found:" + 'terraform/' + env + '/terraform.tfstate')

def ansible_command(env, host, cmd):
    ssh_user = 'centos'

    if not host:
        print('Host or Hostgroup is required.')
        exit()

    if not cmd:
        print('Command is required.')
        exit()

    os.environ['TF_STATE'] = constants.CURPATH + '/terraform/' + env + '/terraform.tfstate'
    os.environ['TF_ANSIBLE_GROUPS_TEMPLATE'] = '{{ ["jump", "tf_tags[group]"] | join("\n") }}'

    response = exists('terraform/' + env + '/terraform.tfstate')

    if response == True:
        ret = subprocess.call('cd ansible && ansible ' + host + ' -a "' + cmd + '" -u ' + ssh_user + ' -i inventory/terraform  --private-key ../terraform/' + env + '/id_rsa', shell=True)
        
    else:
        print("Path not found:" + 'terraform/' + env + '/terraform.tfstate')


def terraform_deploy(env):
    response = exists('terraform/' + env + '/terraform.tfstate')
    
    if response == True:
        ret = subprocess.call('cd terraform/' + env + ' && terraform init', shell=True)
        ret = subprocess.call('cd terraform/' + env + ' && terraform plan', shell=True)
        ret = subprocess.call('cd terraform/' + env + ' && terraform apply --auto-approve', shell=True)
    else:
        print("Path not found:" + 'terraform/' + env + '/terraform.tfstate')

def exists(path):
    """Test whether a path exists.  Returns False for broken symbolic links"""
    try:
        st = os.stat(path)
    except os.error:
        return False
    return True

def build_scaffold(dir):
    print('Building Scaffold in: %s' % dir)

def unzip_file(filename):
    print("Opening file", filename)
    with open(filename, 'rb') as f:
        print("  Unzipping file", filename)
        z = zipfile.ZipFile(f)
        for name in z.namelist():
            print("    Extracting file", name)
            z.extract(name,"/tmp/")

def download_file(url, file_name):
    urllib.request.urlretrieve(url, file_name)

def extract_tool_from_web_to_env(url, tool, dest):
    file_name = url[url.rfind("/")+1:]
    download_file(url, '/tmp/' + file_name)
    unzip_file('/tmp/' + file_name)
    try:
        os.remove(dest + tool)
    except OSError:
        pass
    shutil.copyfile('/tmp/' + tool, dest + tool)
    os.chmod(dest + tool, stat.S_IXUSR | stat.S_IRUSR | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH)

def install_tools(dest):
    baseurl = 'https://releases.hashicorp.com/'
    extract_tool_from_web_to_env(baseurl + 'terraform/0.11.6/terraform_0.11.6_darwin_amd64.zip','terraform', dest)
    extract_tool_from_web_to_env(baseurl + 'packer/1.2.2/packer_1.2.2_darwin_amd64.zip', 'packer', dest)
    extract_tool_from_web_to_env(baseurl + 'nomad/0.7.1/nomad_0.7.1_darwin_amd64.zip', 'nomad', dest)
    ret = subprocess.call('cd ansible && ansible-playbook playbooks/' + playbook + '.yml -i inventory/terraform -e "ansible_ssh_user=' + ssh_user + '" --private-key ../terraform/' + env + '/id_rsa', shell=True)


def deploy(environment, path):
    os.chdir(path + '/' + environment)
    for file in glob.glob("*"):
        if file.endswith("main.tf"):
            os.system('terraform init')

