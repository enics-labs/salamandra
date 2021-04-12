# Copyright 2021 EnICS Labs, Bar-Ilan University.
# Licensed under the Apache License, Version 2.0, see LICENSE for details.
# SPDX-License-Identifier: Apache-2.0

####################### standard_cell #######################
import sys, os
from salamandra import *
from scm_compiler.define_parameters import *

def str_to_class(classname):
    return getattr(sys.modules[__name__], classname)

if params['technology'] == 'tsmc65_12TR':
    from scm_compiler.standard_cell_from_tech_tsmc65_12TR import *
elif params['technology'] == 'tsmc65_9TR':
    from scm_compiler.standard_cell_from_tech_tsmc65_9TR import *
elif params['technology'] == 'Synopsys28':
    from scm_compiler.standard_cell_from_tech_Synopsys28 import *



TRACKS = params['TRACKS'] 

sc = {}     # standard_cell

if params['technology'] == 'tsmc65_'+TRACKS+'TR':
    if TRACKS == '12':
        sc['site'] = 2.4
    elif TRACKS == '9':
        sc['site'] = 1.8
    
    ##########  latch  ##########
    sc['latch'] = {}
    sc['latch']['in'] = 'D'
    sc['latch']['clk'] = 'G'     
    sc['latch']['out'] = 'Q'      

    for i in ['1','2','3']:
        sc['latch_X'+i] = dict(sc['latch'])
        sc['latch_X'+i]['component'] = str_to_class('LATQ_X'+i+'M_A'+TRACKS+'TR')()
        sc['latch_X'+i]['width'] = sc['latch_X'+i]['component'].get_component_dimensions()[0]

    sc['latch'] = sc['latch_X1']    # defult = X1

    ##########  flipflop  ##########
    sc['flipflop'] = {}
    sc['flipflop']['in'] = 'D'
    sc['flipflop']['clk'] = 'CK'
    sc['flipflop']['out'] = 'Q'
    
    for i in ['1','2','3','4']:
        sc['flipflop_X'+i] = dict(sc['flipflop'])
        sc['flipflop_X'+i]['component'] = str_to_class('DFFQ_X'+i+'M_A'+TRACKS+'TR')()
        sc['flipflop_X'+i]['width'] = sc['flipflop_X'+i]['component'].get_component_dimensions()[0]

    sc['flipflop'] = sc['flipflop_X1']  # defult = X1
    
    ##########  buffer  ##########
    sc['buffer'] = {}
    sc['buffer']['in'] = 'A'
    sc['buffer']['out'] = 'Y'

    for i in ['1','2','3','4','5','6','7P5','9','11','13','16']:
        sc['buffer_X'+i] = dict(sc['buffer'])
        sc['buffer_X'+i]['component'] = str_to_class('BUFH_X'+i+'M_A'+TRACKS+'TR')()
        sc['buffer_X'+i]['width'] = sc['buffer_X'+i]['component'].get_component_dimensions()[0]

    sc['buffer'] = sc['buffer_X1']  # defult = X1

    ##########  inverter  ##########
    sc['inverter'] = {}
    sc['inverter']['in'] = 'A'
    sc['inverter']['out'] = 'Y'
    
    for i in ['1','2','3','4','5','6','7P5','9','11','13','16']:
        sc['inverter_X'+i] = dict(sc['inverter'])
        sc['inverter_X'+i]['component'] = str_to_class('INV_X'+i+'M_A'+TRACKS+'TR')()
        sc['inverter_X'+i]['width'] = sc['inverter_X'+i]['component'].get_component_dimensions()[0]

    sc['inverter'] = sc['inverter_X1']  # defult = X1

    ##########  NAND2  ##########
    sc['NAND2'] = {}
    sc['NAND2']['in_1'] = 'A'
    sc['NAND2']['in_2'] = 'B'
    sc['NAND2']['out'] = 'Y'   

    for i in ['1','2','3','4','6','8']:
        sc['NAND2_X'+i] = dict(sc['NAND2'])
        sc['NAND2_X'+i]['component'] = str_to_class('NAND2_X'+i+'A_A'+TRACKS+'TR')()
        sc['NAND2_X'+i]['width'] = sc['NAND2_X'+i]['component'].get_component_dimensions()[0]

    sc['NAND2'] = sc['NAND2_X1']  # defult = X1
    
    ##########  NAND3  ##########
    sc['NAND3'] = {}
    sc['NAND3']['in_1'] = 'A'
    sc['NAND3']['in_2'] = 'B'
    sc['NAND3']['in_3'] = 'C'
    sc['NAND3']['out'] = 'Y'   

    for i in ['1','2','3','4','6']:
        sc['NAND3_X'+i] = dict(sc['NAND3'])
        sc['NAND3_X'+i]['component'] = str_to_class('NAND3_X'+i+'A_A'+TRACKS+'TR')()
        sc['NAND3_X'+i]['width'] = sc['NAND3_X'+i]['component'].get_component_dimensions()[0]
    
    sc['NAND3'] = sc['NAND3_X1']  # defult = X1

    ##########  NAND4  ##########
    sc['NAND4'] = {}
    sc['NAND4']['in_1'] = 'A'
    sc['NAND4']['in_2'] = 'B'
    sc['NAND4']['in_3'] = 'C'
    sc['NAND4']['in_4'] = 'D'
    sc['NAND4']['out'] = 'Y'   

    for i in ['1','2','3','4']:
        sc['NAND4_X'+i] = dict(sc['NAND4'])
        sc['NAND4_X'+i]['component'] = str_to_class('NAND4_X'+i+'A_A'+TRACKS+'TR')()
        sc['NAND4_X'+i]['width'] = sc['NAND4_X'+i]['component'].get_component_dimensions()[0]

    sc['NAND4'] = sc['NAND4_X1']  # defult = X1

    ##########  NOR2  ##########
    sc['NOR2'] = {}
    sc['NOR2']['in_1'] = 'A'
    sc['NOR2']['in_2'] = 'B'
    sc['NOR2']['out'] = 'Y'    

    for i in ['1','2','3','4','6','8']:
        sc['NOR2_X'+i] = dict(sc['NOR2'])
        sc['NOR2_X'+i]['component'] = str_to_class('NOR2_X'+i+'A_A'+TRACKS+'TR')()
        sc['NOR2_X'+i]['width'] = sc['NOR2_X'+i]['component'].get_component_dimensions()[0]

    sc['NOR2'] = sc['NOR2_X1']  # defult = X1

    ##########  NOR3  ##########
    sc['NOR3'] = {}
    sc['NOR3']['in_1'] = 'A'
    sc['NOR3']['in_2'] = 'B'
    sc['NOR3']['in_3'] = 'C'
    sc['NOR3']['out'] = 'Y'    

    for i in ['1','2','3','4']:
        sc['NOR3_X'+i] = dict(sc['NOR3'])
        sc['NOR3_X'+i]['component'] = str_to_class('NOR3_X'+i+'A_A'+TRACKS+'TR')()
        sc['NOR3_X'+i]['width'] = sc['NOR3_X'+i]['component'].get_component_dimensions()[0]
    
    sc['NOR3'] = sc['NOR3_X1']  # defult = X1
    
    ##########  latch_clock_gate  ##########
    sc['latch_clock_gate'] = {}
    sc['latch_clock_gate']['clk'] = 'CK'
    sc['latch_clock_gate']['E'] = 'E'
    sc['latch_clock_gate']['SE'] = 'SE'
    sc['latch_clock_gate']['out'] = 'ECK'

    for i in ['0P5','1','2','3','4','5','6','7P5','9','11','13','16']:
        sc['latch_clock_gate_X'+i] = dict(sc['latch_clock_gate'])
        sc['latch_clock_gate_X'+i]['component'] = str_to_class('PREICG_X'+i+'B_A'+TRACKS+'TR')()
        sc['latch_clock_gate_X'+i]['width'] = sc['latch_clock_gate_X'+i]['component'].get_component_dimensions()[0]

    sc['latch_clock_gate'] = sc['latch_clock_gate_X4']  # defult = X4
    
    ##########  well_tap  ##########
    sc['well_tap'] = {}
    sc['well_tap']['component'] = ComponentXY('WELLANTENNATIEPW2_A'+str(TRACKS)+'TR')
    sc['well_tap']['width'] = 0.4
    sc['well_tap']['component'].set_component_dimensions(sc['well_tap']['width'], sc['site'])
    sc['well_tap']['component'].set_dont_uniq(True)
    sc['well_tap']['component'].set_dont_write_verilog(True)

elif params['technology'] == 'Synopsys28':
    sc['site'] = 0.9
    
    ##########  latch  ##########
    sc['latch'] = {}
    sc['latch']['in'] = 'D'
    sc['latch']['clk'] = 'G'     
    sc['latch']['out'] = 'Q'      
    
    for i in ['1','2','4','6','8']:
        sc['latch_X'+i] = dict(sc['latch'])
        sc['latch_X'+i]['component'] = str_to_class('SEP_LDPQ_'+i)()
        sc['latch_X'+i]['width'] = sc['latch_X'+i]['component'].get_component_dimensions()[0]
        
    sc['latch'] = sc['latch_X1']    # defult = X1

    ##########  flipflop  ##########
    sc['flipflop'] = {}
    sc['flipflop']['in'] = 'D'
    sc['flipflop']['clk'] = 'CK'
    sc['flipflop']['out'] = 'Q'

    for i in ['1','2','4']:
        sc['flipflop_X'+i] = dict(sc['flipflop'])        
        sc['flipflop_X'+i]['component'] = str_to_class('SEP_FDPQ_'+i)()    
        sc['flipflop_X'+i]['width'] = sc['flipflop_X'+i]['component'].get_component_dimensions()[0]
    
    sc['flipflop'] = sc['flipflop_X1']    # defult = X1

    ##########  buffer  ##########
    sc['buffer'] = {}
    sc['buffer']['in'] = 'A'
    sc['buffer']['out'] = 'X'
    
    for i in ['1','2','3','4','5','6','8','10','12','16']:
        sc['buffer_X'+i] = dict(sc['buffer'])                
        sc['buffer_X'+i]['component'] = str_to_class('SEP_BUF_'+i)()
        sc['buffer_X'+i]['width'] = sc['buffer_X'+i]['component'].get_component_dimensions()[0]

    sc['buffer'] = sc['buffer_X1']    # defult = X1
    
    ##########  inverter  ##########
    sc['inverter'] = {}
    sc['inverter']['in'] = 'A'
    sc['inverter']['out'] = 'X'

    for i in ['0P5','1','2','3','4','5','6','8','10','12','16']:
        sc['inverter_X'+i] = dict(sc['inverter'])                
        sc['inverter_X'+i]['component'] = str_to_class('SEP_INV_'+i)()    
        sc['inverter_X'+i]['width'] = sc['inverter_X'+i]['component'].get_component_dimensions()[0]

    sc['inverter'] = sc['inverter_X1']    # defult = X1
    
    ##########  NAND2  ##########
    sc['NAND2'] = {}
    sc['NAND2']['in_1'] = 'A1'
    sc['NAND2']['in_2'] = 'A2'
    sc['NAND2']['out'] = 'X'

    for i in ['0P5','1','2','3','4','5','6','8','10','12','16']:
        sc['NAND2_X'+i] = dict(sc['NAND2'])                
        sc['NAND2_X'+i]['component'] = str_to_class('SEP_ND2_'+i)()    
        sc['NAND2_X'+i]['width'] = sc['NAND2_X'+i]['component'].get_component_dimensions()[0]

    sc['NAND2'] = sc['NAND2_X1']    # defult = X1
    
    ##########  NAND3  ##########
    sc['NAND3'] = {}
    sc['NAND3']['in_1'] = 'A1'
    sc['NAND3']['in_2'] = 'A2'
    sc['NAND3']['in_3'] = 'A3'
    sc['NAND3']['out'] = 'X'  
     
    for i in ['0P5','1','2','3','4','6','8','16']:
        sc['NAND3_X'+i] = dict(sc['NAND3'])                
        sc['NAND3_X'+i]['component'] = str_to_class('SEP_ND3_'+i)()    
        sc['NAND3_X'+i]['width'] = sc['NAND3_X'+i]['component'].get_component_dimensions()[0]
    
    sc['NAND3'] = sc['NAND3_X1']    # defult = X1
    
    ##########  NAND4  ##########
    sc['NAND4'] = {}
    sc['NAND4']['in_1'] = 'A1'
    sc['NAND4']['in_2'] = 'A2'
    sc['NAND4']['in_3'] = 'A3'
    sc['NAND4']['in_4'] = 'A4'
    sc['NAND4']['out'] = 'X'

    for i in ['0P5','1','2','4','8','12','16']:
        sc['NAND4_X'+i] = dict(sc['NAND4'])                
        sc['NAND4_X'+i]['component'] = str_to_class('SEP_ND4_'+i)()
        sc['NAND4_X'+i]['width'] = sc['NAND4_X'+i]['component'].get_component_dimensions()[0]
    
    sc['NAND4'] = sc['NAND4_X1']    # defult = X1
    
    ##########  NOR2  ##########
    sc['NOR2'] = {}
    sc['NOR2']['in_1'] = 'A1'
    sc['NOR2']['in_2'] = 'A2'
    sc['NOR2']['out'] = 'X'

    for i in ['0P5','1','2','3','4','6','8']:
        sc['NOR2_X'+i] = dict(sc['NOR2'])                
        sc['NOR2_X'+i]['component'] = str_to_class('SEP_NR2_'+i)()    
        sc['NOR2_X'+i]['width'] = sc['NOR2_X'+i]['component'].get_component_dimensions()[0]
    
    sc['NOR2'] = sc['NOR2_X1']    # defult = X1
    
    ##########  NOR3  ##########
    sc['NOR3'] = {}
    sc['NOR3']['in_1'] = 'A1'
    sc['NOR3']['in_2'] = 'A2'
    sc['NOR3']['in_3'] = 'A3'
    sc['NOR3']['out'] = 'X'

    for i in ['0P75','1','2','4','8']:
        sc['NOR3_X'+i] = dict(sc['NOR3'])                
        sc['NOR3_X'+i]['component'] = str_to_class('SEP_NR3_'+i)()    
        sc['NOR3_X'+i]['width'] = sc['NOR3_X'+i]['component'].get_component_dimensions()[0]	 

    sc['NOR3'] = sc['NOR3_X1']    # defult = X1
    
    ##########  latch_clock_gate  ##########
    sc['latch_clock_gate'] = {}
    sc['latch_clock_gate']['clk'] = 'CK'
    sc['latch_clock_gate']['E'] = 'EN'
    sc['latch_clock_gate']['SE'] = 'SE'
    sc['latch_clock_gate']['out'] = 'Q'

    for i in ['1','2','4','8','12','16']:
        sc['latch_clock_gate_X'+i] = dict(sc['latch_clock_gate'])                        
        sc['latch_clock_gate_X'+i]['component'] = str_to_class('SEP_CKGTPLT_V7_'+i)()    
        sc['latch_clock_gate_X'+i]['width'] = sc['latch_clock_gate_X'+i]['component'].get_component_dimensions()[0]

    sc['latch_clock_gate'] = sc['latch_clock_gate_X4']    # defult = X4
    
    ##########  well_tap  ##########
    sc['well_tap'] = {}
    sc['well_tap']['component'] = ComponentXY('SEP_TIEDIN_ECOCT_1')
    sc['well_tap']['width'] = 0.28
    sc['well_tap']['component'].set_component_dimensions(sc['well_tap']['width'], sc['site'])
    sc['well_tap']['component'].set_dont_uniq(True)
    sc['well_tap']['component'].set_dont_write_verilog(True)

    
print('cells you can use from tech:\n')
for cell in sorted(sc):
    print(str(cell))

