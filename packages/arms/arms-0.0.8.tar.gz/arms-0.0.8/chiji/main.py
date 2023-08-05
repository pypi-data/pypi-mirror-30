import os
import lesscli
import requests
import random
from jinja2 import Template

from chiji.utils import project_to_package, camelize

PY2 = (type(b'') == str)
if PY2:
    input = raw_input


def print_help():
    text = """
    
    arms init                   : setup CI/CD
    arms run [stage]            : run scripts of .gitlab-ci.yml
    arms docker prune           : prune docker container/image/volume
    arms -h                     : show help information
    arms -v                     : show version
    
    
    """
    print(text)


def print_version():
    from chiji import __version__
    text = """
    arms version: {}
    
    """.format(__version__)
    print(text)


def grab(project, lang):
    package = project_to_package(project)
    port = random.randint(10000, 32000)
    mysql_port = random.randint(10000, 32000)
    redis_port = random.randint(10000, 32000)
    package_upper = camelize(package)
    package_lower = camelize(package, False)
    base = 'http://gitlab.parsec.com.cn/qorzj/chiji-tool/raw/master/templates/' + lang
    index_text = requests.get(base + '/.index.txt').text
    data = {
        'project': project, 'package': package,
        'package_upper': package_upper, 'package_lower': package_lower, 'image': package.lower(),
        'port': port, 'mysql_port': mysql_port, 'redis_port': redis_port,
    }
    for line in index_text.splitlines():
        if not line: continue
        url = base + '/' + line
        real_path = Template(line).render(**data)
        print(url + '\t' + real_path)
        if real_path[-1] == '/':
            os.system('mkdir -p ' + real_path)
        else:
            req = requests.get(url)
            if req.status_code == 404:
                print('Template not found!')
                return
            file_text = req.text
            rended_text = Template(file_text).render(**data)
            if real_path == '.gitignore' and os.path.isfile(real_path):  # merge .gitignore
                old_lines = open(real_path).read().splitlines()
                for new_line in rended_text.splitlines():
                    if new_line not in old_lines:
                        old_lines.append(new_line)
                rended_text = '\n'.join(old_lines) + '\n'

            with open(real_path, 'wb') as f:
                f.write(rended_text.encode('utf-8'))
    print('---- Done ----')


def run_init():
    if not os.path.isdir('.git'):
        print('Please change workdir to top!')
        return
    front = input('Please input front or back: [front / back] ')
    lang_front = ['react', 'build']
    lang_back = ['java', 'node', 'python', 'nginx']
    if front == 'front':
        lang_short = input('Please input language: [%s] ' % ' / '.join(lang_front))
        assert lang_short in lang_front
    elif front == 'back':
        lang_short = input('Please input language: [%s] ' % ' / '.join(lang_back))
        assert lang_short in lang_back
    else:
        print('Error, please check!')
        return
    lang = front + '-' + lang_short
    project = os.path.abspath('').rsplit('/')[-1]
    grab(project, lang)


def run_run(stage):
    pass


def run_docker_prune():
    os.system('docker container prune -f')
    os.system('docker image prune -f')
    os.system('docker volume prune -f')


def run(*a, **b):
    if 'h' in b or 'help' in b:
        print_help()
    elif 'v' in b or 'version' in b:
        print_version()
    elif tuple(a) == ('init',):
        run_init()
    elif len(a) == 2 and a[0] == 'run':
        stage = a[1]
        run_run(stage)
    elif tuple(a) == ('docker', 'prune'):
        run_docker_prune()
    else:
        print_help()


def entrypoint():
    lesscli.run(callback=run, single='hv')