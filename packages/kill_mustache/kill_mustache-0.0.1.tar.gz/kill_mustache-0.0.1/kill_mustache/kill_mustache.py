#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pystache
import sys


diretorio = sys.argv [1]
telas = sys.argv[2:]

obj = {tela: True for tela in telas}

input_file = None
arquivo = open(diretorio, 'r')

with open(diretorio) as d:
    input_file = d.read()

file_rendered = pystache.render(input_file, obj)

print(file_rendered)
