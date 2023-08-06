# -*- coding: utf-8 -*-


import modelx as mx

model, space = mx.new_model(), mx.new_space()

@mx.defcells
def last_age():
    return 110

@mx.defcells
def last_t():
    return min(last_age, 105)




