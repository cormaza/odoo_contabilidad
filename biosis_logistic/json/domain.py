hola = {'domain': {'deposito_id': [('tipo_servicio', '=', 'deposito'), ('maritimo', '=', True), ('fcl', '=', True)],
            'vacio_id': [('tipo_servicio', '=', 'vacio'), ('maritimo', '=', True), ('fcl', '=', True),
                         ('tipo_contenedor_ids', 'in', [1]), ('linea_naviera_ids', 'in', [22])],
            'agente_aduana_id': [('tipo_servicio', '=', 'agente_aduana'), ('maritimo', '=', True), ('fcl', '=', True)],
            'agente_portuario_id': [('tipo_servicio', '=', 'agente_portuario'), ('maritimo', '=', True),
                                    ('fcl', '=', True), ('tipo_contenedor_ids', 'in', [1]),
                                    ('linea_naviera_ids', 'in', [22])]}}
