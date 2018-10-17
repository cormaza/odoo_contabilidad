# coding=utf-8
from odoo import models, fields


class CrmTrazabilidad(models.Model):
    _name = 'crm.trazabilidad'

    partner_id = fields.Many2one('res.partner', string=u'Cliente')
    sale_order_id = fields.Many2one('sale.order', string=u'Cotización')
    sale_order_referencia = fields.Char(related='sale_order_id.referencia_sbc')
    partner_ruc = fields.Char(related='partner_id.vat')
    etd = fields.Date(string=u'ETD')
    eta = fields.Date(string=u'ETA')
    cita_planta = fields.Date(string=u'Cita Planta')
    mes = fields.Integer(string=u'Mes CitaPlanta')
    fecha_retiro_contenedor = fields.Date(string=u'Retiro Contenedor')
    referencia_cliente = fields.Text(string=u'Referencia Cliente')
    puerto_embarque = fields.Text(string=u'Puerto de Embarque')
    puerto_destino = fields.Text(string=u'Puerto de Destino')
    numero_dam = fields.Text(string=u'Nª de DAM')
    canal = fields.Char(string=u'Canal')
    # i_canal = fields.Char(string=u'Canal')
    po_ = fields.Char(string=U'Po')
    booking = fields.Char(string=u'Booking')
    n_bl = fields.Char(strig=u'Nª Bl')
    n_contenedor = fields.Char(string=u'Número Contenedor')
    sale_order_id_tipo_contenedor_id = fields.Many2one('sale.contenedor.tipo', related='sale_order_id.tipo_contenedor_id')
    consignatorio = fields.Char(string=u'Consginatorio')
    factura_consignatario = fields.Char(string=u'Número Consignatrio')
    fob = fields.Char(string=u'FOB')
    cif = fields.Char(string=u'CIF')
    nave = fields.Char(string=u'Nave')
    viaje = fields.Char(string=u'Viaje')
    fecha_vencimiento = fields.Date(string=u'Fecha Vencimiento')
    incoterm = fields.Char(string=u'Incoterm')
    observacion = fields.Char(string=u'Observación')
    vencimiento_estadia = fields.Date(string=u'Vencimiento de Estadia')
    vencimiento_almacenaje = fields.Date(string=u'Vencimiento Almacenaje')
    estado_regularizacion_id = fields.Many2one('crm.estado_regularizacion')
