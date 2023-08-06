import os
import json
import datetime
from namanager.enums import FORMATS
from namanager.core import Namanager
from namanager.archieve_manager import ArchieveManager

SETTINGS_JSON = {}


def raiser(condition, msg):
    if not condition:
        raise Exception(msg)  # pragma: no cover


def generate_settings(to):
    namanager_root = os.path.dirname(os.path.dirname(__file__))
    with open(os.sep.join([namanager_root,
                           'namanager', 'settings.json'])) as f:
        json = f.read()
    if os.path.isdir(to):
        to = os.sep.join([to, 'settings.json'])
    if os.path.isfile(to):
        to = os.sep.join(
            to.split(os.sep)[:-1] +
            ['settings_{:%Y%m%d%H%M%S}.json'.format(datetime.datetime.now())])
    with open(to, 'w') as f:
        f.write(json)


def import_settings(settings_file):
    global SETTINGS_JSON

    with open(settings_file, 'r') as s:
        SETTINGS_JSON = json.loads(s.read())

    raiser(isinstance(SETTINGS_JSON, dict),
           'settings must be dict.')

    SETTING_TYPE_PAIR = {
        'CHECK_DIRS': list,
        'ONLY_FILES': list,
        'ONLY_DIRS': list,
        'IGNORE_FILES': list,
        'IGNORE_DIRS': list,
        'FILE_FORMATS': dict,
        'DIR_FORMATS': dict
    }

    for key, value in SETTING_TYPE_PAIR.items():
        SETTINGS_JSON[key] = SETTINGS_JSON.get(key, value())
        raiser(isinstance(SETTINGS_JSON[key], value),
               '{0} must be {1}.'.format(key, value))

    for k, v in SETTINGS_JSON['FILE_FORMATS'].items():
        raiser(k in FORMATS,
               'FILE_FORMATS has wrong key:{0}.'.format(k))
        raiser(v in FORMATS[k],
               'FILE_FORMATS[\'{0}\'] has wrong key:{1}.'.format(k, v))

    for k, v in SETTINGS_JSON['DIR_FORMATS'].items():
        raiser(k in FORMATS,
               'DIR_FORMATS has wrong key:{0}.'.format(k))
        raiser(v in FORMATS[k],
               'DIR_FORMATS[\'{0}\'] has wrong key:{1}.'.format(k, v))


def test_writing_permission(**kwargs):
    """
    param dirname:
    type dirname: str
    param required: default True
    type required: True, False
    param error_msg:
    type error_msg: str
    """

    try:
        dirname = kwargs.get('dirname', os.getcwd())
        if dirname[-1] != os.sep:
            dirname += os.sep
        # test directory is exists or not and raise
        os.path.realpath(dirname)

        filename = ''.join([dirname, 'test_file'])
        while os.path.exists(filename):
            filename += '_'

        with open(filename, 'w') as f:
            f.write('test...')
        os.remove(filename)

    except Exception as e:
        print(kwargs.get('error_msg', ''))
        required = kwargs.get('required', True)
        if required:
            raise e


def get_src_dst_pair(error_info):
    # we need to move this function to/into a better place
    src_dst_pair = []

    for e in error_info:
        src_dst_pair.append([e['actual'], e['expect']])

    return src_dst_pair


def check(**kwargs):
    REQUIRED = kwargs.get('required', False)
    FMT = kwargs.get('fmt', 'json')
    PRETTY_DUMP = kwargs.get('pretty_dump', False)
    RENAME = kwargs.get('rename', False)
    RENAME_BACKUP = kwargs.get('rename_backup', False)
    RENAME_BACKUP_DIR = kwargs.get('rename_backup_dir', os.getcwd())
    REVERT_FILE = kwargs.get('revert_file', None)

    if REVERT_FILE is not None:
        am = ArchieveManager()
        with open(REVERT_FILE, 'r') as f:
            am.rename(json.loads(f.read()))

    errors = []

    for d in SETTINGS_JSON['CHECK_DIRS']:
        checker = Namanager(SETTINGS_JSON)

        checker.check(d)

        if FMT == 'dict':
            RESULT = checker.get_dict(checker.error_info)
        elif FMT == 'json':
            RESULT = checker.get_json(checker.error_info, PRETTY_DUMP)
        elif FMT == 'xml':
            RESULT = checker.get_xml(checker.error_info, PRETTY_DUMP)

        print(RESULT)
        if RESULT:
            if RENAME:
                am = ArchieveManager()
                error_info = checker.get_dict(checker.error_info)
                error_info = get_src_dst_pair(error_info)

                if RENAME_BACKUP:
                    test_writing_permission(dirname=RENAME_BACKUP_DIR)
                    filename = 'namanager_rename_{:%Y%m%d%H%M%S}.bak'.format(
                        datetime.datetime.now())
                    with open(os.sep.join([RENAME_BACKUP_DIR, filename]),
                              'w') as f:
                        f.write(json.dumps(
                            am.gen_revert_path_pairs(error_info),
                            indent=4, sort_keys=True))

                am.rename(error_info)

            errors.append('In folder {0} :'.format(os.path.realpath(d)))
            errors.append('FAILED (error{0}={1})'.format(
                  's' if len(RESULT) > 1 else '',
                  checker.error_info_count))

    print("")
    if errors:
        for e in errors:
            print(e)
        if REQUIRED:
            exit(1)
    else:
        print('OK.\n')


def entry(settings_file, **kwargs):
    import_settings(settings_file)
    check(**kwargs)


if __name__ == '__main__':  # pragma: no cover
    entry('namanager/file_checker/settings.json')
