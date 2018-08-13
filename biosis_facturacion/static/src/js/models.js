odoo.define('einvoice_pos', function (require) {
    'use strict';

    var module = require('point_of_sale.models');

    var models = module.PosModel.prototype.models;
    for (var i = 0; i < models.length; i++) {
        var model = models[i];
        if (model.model === 'pos.order') {
            console.log('ENCONTRADO POS ORDER');
            model.fields.push('numero_comprobante');
            model.fields.push('codigo_2d');
        }
    }
});
