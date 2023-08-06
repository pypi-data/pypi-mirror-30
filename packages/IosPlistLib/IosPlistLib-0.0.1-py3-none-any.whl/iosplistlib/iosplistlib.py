'''A module to display and edit settings within an ipa Root.plist file in an iOS ipa.'''

from zipfile import ZipFile
import xml.etree.ElementTree as ET
import argparse
import shutil

def get_parser():
    '''Initialise and return an argument parser.'''
    parser = argparse.ArgumentParser(description='Display and modify Root.plist variables.')
    parser.add_argument('-f', metavar='F', type=str, help='ipa file.')
    parser.add_argument('-s', metavar='S', type=str, help='setting.')
    parser.add_argument('-r', metavar='R', type=str, help='replacement value.')
    return parser

def get_setting(file, setting):
    '''Obtain the value for the given setting in the Root.plist file.'''
    zip_in = ZipFile(file)
    filename = [f for f in zip_in.namelist() if f.endswith('Settings.bundle/Root.plist')][0]
    contents = zip_in.read(filename).decode('utf-8')
    root = ET.fromstring(contents)
    element = root.findall("dict/array/dict[string='" + setting + "']/")
    for index, attrib in enumerate(element):
        if attrib.text == 'DefaultValue':
            return element[index+1].text
    return None

def modify_setting(file, setting, new_value):
    '''Replace the given setting with a new value.'''

    #copy archive minus the one I want to edit
    zip_in = ZipFile(file, 'r')
    zip_out = ZipFile(file[:-4] + "_edited.ipa", 'w')
    file_info = None

    for item in zip_in.infolist():
        data = zip_in.read(item.filename)
        if not item.filename.endswith('Root.plist'):
            zip_out.writestr(item, data)
        else:
            file_info = item

    #extract the file I want to edit
    zip_in.extract(file_info)

    #modify extracted file
    with open(file_info.filename, 'r') as read_file:
        lines = read_file.readlines()
        setting = get_setting(file, setting)

        with open(file_info.filename, 'w') as write_file:
            for line in lines:
                if setting in line:
                    write_file.write(line.replace(setting, new_value).rstrip() + '\n')
                else:
                    write_file.write(line.rstrip() + '\n')

    #add modified file to archive
    zip_out.write(file_info.filename)

    #cleanup
    shutil.rmtree('Payload')

def main():
    parser = get_parser()
    args = parser.parse_args()

    if args.s is not None:
        try:
            if args.r is not None:
                modify_setting(args.f, args.s, args.r)
            else:
                print(get_setting(args.f, args.s))
        except Exception as e:
            print(e)
        exit()

if __name__ == '__main__':
    main()
