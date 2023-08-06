#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright 2018 2Cas
# Licensed under the MIT license (http://opensource.org/licenses/MIT)

from q2k.classes import *
from q2k.console import note_out, error_out
from q2k.globals import QMK_DIR, OUT_KBF_DIR, KBD_LIST, KB_INFO

def keycode_parse(keycode):

    func_list = []
    while '(' in keycode:
        split = keycode.split('(', 1)
        keycode = split[1][:-1]
        function = split[0]
        func_list.append(function)

    kc_data = ''
    for func in func_list:
        kc_data += '{id: "'+func+'()","fields":['

    if keycode.isdigit():
        kc_data += keycode
    else:
        kc_data += '{id: "'+keycode+'", fields":[]}'

    for i in range(len(func_list)):
        kc_data += ']}'

    return kc_data


def create_kbfirmware_json(kbc, printout=False):

    # Can't simply dump to yaml as we want to keep layout (array) as a human readable matrix (2D 'array').
    kb_n = kbc.get_name()
    rev_n = kbc.get_rev()
    keymap_n = kbc.get_keymap()

    rev = kbc.get_rev_info(rev_n)
    matrix = rev.get_matrix_pins()
    layers = rev.get_layout() 

    template_matrix = layers[0].get_template()
    name = '"'+kb_n+'_'+rev_n+'"'
    keymap = '"'+keymap_n+'"'
    if matrix:
        for r in matrix[0]:
        rows = str(matrix[0]).replace("'", '"')
        cols = str(matrix[1]).replace("'", '"')
    else:
        rows, cols = ''
   
    template = ''
    for i, row in enumerate(template_matrix):
        for col in row:
            template += (col+', ')
        if i+1 < len(template_matrix):
            template += '\n        '

    
    layout = ''
    for i, layer in enumerate(layers):
        layout += '      [ # layer '+str(i)+'\n        ['
        for row in layer.get_layout():
            layout += '\n          '
            for keycode in row:
               if len(keycode) < 4:
                   repeat = 4 - len(keycode)
                   for i in (range(repeat)):
                       keycode+=' '
               layout += keycode+', '
        layout +='\n        ]\n      ],\n'


    json_out = '{"version":1,"keyboard":{"keys":['
    id_list = []
    try:
        for i, layer in enumerate(layers):
            id, col, row = -1
            for row in layer.get_layout():
                row_y += 1
                for keycode in row:
                    id += 1
                    col_x = col_x + 1
                    if i == 0:
                        keycodelist = [keycode]
                        id_list.append(keycodelist)
                    else:
                        id_list[id].append(keycode)
                    if i+1 == len(layers):
                        for kc in id_list[id]:
                            kc_build += keycode_parse(kc)+','
                        kc_build = kb_build[:-1]
                        json_out += '{"id":'+str(iden)+,'"legend":"","state":{"x":'+col_x+',"y":'+row_y+',"r":0,"rx":0,"ry":0,"w":1,"h":1},"row":'r+',"col":'+c+',"keycodes":['+kc_build+']},'
                col_x = -1
    except IndexError:
        error_out(['Layers have different layouts'])

   #"controller":1,"bounds":{"min":{"x":0,"y":0},"max":{"x":4,"y":4}},"rows":4,"cols":4,"pins":{"row":["F4","F5","F6","F7"],"col":["D1","D0","D4","C6"],"num":null,"caps":null,"scroll":null,"compose":null,"kana":null,"led":null,"rgb":"B1"},"macros":{},"quantum":"void matrix_init_user(void) {\n}\n\nvoid matrix_scan_user(void) {\n}\n\nbool process_record_user(uint16_t keycode, keyrecord_t *record) {\n\treturn true;\n}","settings":{"diodeDirection":0,"name":"sweet16","bootloaderSize":2,"rgbNum":1,"backlightLevels":3}}}
    '''
    kblibs = kbc.get_libs()
    if rev_n:
        path_list = kblibs + [ rev_n, keymap_n]
    else:
        path_list = kblibs + [keymap_n]
    output_path = '_'.join(path_list)
    output_yaml = OUT_DIR+output_path+'.yaml'
    if not os.path.exists(OUT_DIR):
        try:
            os.makedirs(OUT_DIR)
        except OSError as e:
            if e.errno != errno.EEXIST and os.path.isdir(output_path):
                raise
    try:
        with open(output_yaml, 'w') as f:
            f.write(output_yaml_info)
    except:
        error_out(['Failed to pipe output to '+output_yaml()])
        exit()

    if printout:
        print(output_yaml_info)

    note_out(['SUCCESS! Output is in: '+output_yaml])
    '''
    print(json_out)
