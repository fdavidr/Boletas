"""
Generador de PDFs para las boletas
Crea PDFs profesionales con formato adecuado
"""

import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from datetime import datetime

class PDFGenerator:
    def __init__(self, empresa_config):
        self.empresa_config = empresa_config
        self.output_dir = "output"
        os.makedirs(self.output_dir, exist_ok=True)
    
    def _add_header(self, elements, styles):
        """Agrega el encabezado con logo y datos de empresa"""
        empresa = self.empresa_config.get_empresa_data()
        
        # Crear tabla para el encabezado
        header_data = []
        
        # Si existe logo, agregarlo
        if self.empresa_config.logo_exists():
            try:
                logo = Image(self.empresa_config.get_logo_path(), width=1*inch, height=1*inch)
                header_data.append([logo, Paragraph(f"<b>{empresa['nombre']}</b><br/>{empresa['eslogan']}", styles['Title'])])
            except:
                header_data.append(['', Paragraph(f"<b>{empresa['nombre']}</b><br/>{empresa['eslogan']}", styles['Title'])])
        else:
            header_data.append(['', Paragraph(f"<b>{empresa['nombre']}</b><br/>{empresa['eslogan']}", styles['Title'])])
        
        header_table = Table(header_data, colWidths=[1.5*inch, 5*inch])
        header_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        elements.append(header_table)
        elements.append(Spacer(1, 0.2*inch))
        
        # Información de la empresa
        empresa_info = f"""
        <b>NIT:</b> {empresa.get('nit', 'N/A')} | <b>Teléfono:</b> {empresa.get('telefono', 'N/A')}<br/>
        <b>Dirección:</b> {empresa.get('direccion', 'N/A')}<br/>
        <b>Contabilidad:</b> {empresa.get('contabilidad', 'N/A')}
        """
        elements.append(Paragraph(empresa_info, styles['Normal']))
        elements.append(Spacer(1, 0.3*inch))
    
    def generar_boleta_mensual(self, boleta):
        """Genera PDF para boleta de pago mensual - Diseño compacto mitad de página"""
        filename = os.path.join(self.output_dir, f"{boleta.numero_boleta}_Mensual_{boleta.nombre_completo.replace(' ', '_')}.pdf")
        doc = SimpleDocTemplate(filename, pagesize=letter, topMargin=0.3*inch, bottomMargin=0.3*inch, leftMargin=0.5*inch, rightMargin=0.5*inch)
        elements = []
        styles = getSampleStyleSheet()
        
        # Estilo para título centrado
        title_style = ParagraphStyle(
            'TitleStyle',
            parent=styles['Normal'],
            fontSize=14,
            textColor=colors.HexColor('#2C3E50'),
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        # Estilo para datos de empresa
        empresa_style = ParagraphStyle(
            'EmpresaStyle',
            parent=styles['Normal'],
            fontSize=7,
            alignment=TA_RIGHT,
            leading=9
        )
        
        # Header horizontal: Logo - Título - Datos Empresa
        empresa = self.empresa_config.get_empresa_data()
        
        # Logo (columna izquierda) - flotante con proporciones preservadas
        if self.empresa_config.logo_exists():
            try:
                from PIL import Image as PILImage
                img = PILImage.open(self.empresa_config.get_logo_path())
                aspect_ratio = img.width / img.height
                logo_height = 0.8 * inch
                logo_width = logo_height * aspect_ratio
                logo = Image(self.empresa_config.get_logo_path(), width=logo_width, height=logo_height)
            except:
                logo = ''
        else:
            logo = ''
        
        # Título (columna central)
        titulo = Paragraph(f"<b>BOLETA DE PAGO</b><br/><font size=9>No. {boleta.numero_boleta}</font>", title_style)
        
        # Datos empresa (columna derecha)
        datos_empresa = Paragraph(
            f"<b>{empresa['nombre']}</b><br/>"
            f"{empresa.get('eslogan', '')}<br/>"
            f"NIT: {empresa.get('nit', 'N/A')}<br/>"
            f"Tel: {empresa.get('telefono', 'N/A')}<br/>"
            f"{empresa.get('direccion', 'N/A')}",
            empresa_style
        )
        
        # Tabla de header con 3 columnas (ancho de columna derecha = ancho de logo)
        header_data = [[logo, titulo, datos_empresa]]
        header_table = Table(header_data, colWidths=[2.5*inch, 3*inch, 2.5*inch])
        header_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
            ('ALIGN', (1, 0), (1, 0), 'CENTER'),
            ('ALIGN', (2, 0), (2, 0), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        elements.append(header_table)
        elements.append(Spacer(1, 0.08*inch))
        
        # Datos del empleado - ultra compacto
        data_empleado = [
            ['Nombre:', boleta.nombre_completo, 'C.I.:', boleta.ci],
            ['Cargo:', boleta.cargo, 'Período:', f"{boleta.mes_pago} {boleta.anio}"],
        ]
        
        if boleta.rango_fechas:
            data_empleado.append(['Rango:', boleta.rango_fechas, 'Fecha:', boleta.fecha_emision.strftime("%d/%m/%Y")])
        else:
            data_empleado.append(['', '', 'Fecha:', boleta.fecha_emision.strftime("%d/%m/%Y")])
        
        # Añadir método de pago
        data_empleado.append(['Método Pago:', getattr(boleta, 'metodo_pago', 'EFECTIVO'), '', ''])
        
        tabla_empleado = Table(data_empleado, colWidths=[0.9*inch, 2.3*inch, 0.7*inch, 2.6*inch])
        tabla_empleado.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#ECF0F1')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('TOPPADDING', (0, 0), (-1, -1), 2),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ]))
        
        elements.append(tabla_empleado)
        elements.append(Spacer(1, 0.12*inch))
        
        # INGRESOS Y EGRESOS LADO A LADO - Ultra compacto
        data_ingresos = [
            ['INGRESOS', 'Bs.'],
            ['Haber Básico', f"{boleta.haber_basico:.2f}"],
            ['Horas Extra', f"{boleta.horas_extra:.2f}"],
            ['Bono Antigüedad', f"{boleta.bono_antiguedad:.2f}"],
            ['Otros Ingresos', f"{boleta.otros_ingresos:.2f}"],
            ['TOTAL INGRESOS', f"{boleta.calcular_total_ingresos():.2f}"],
        ]
        
        data_egresos = [
            ['EGRESOS', 'Bs.'],
            ['Faltas', f"{boleta.faltas:.2f}"],
            ['Retrasos', f"{boleta.retrasos:.2f}"],
            ['Reposiciones', f"{boleta.reposiciones:.2f}"],
            ['Otros Egresos', f"{boleta.otros_egresos:.2f}"],
            ['TOTAL EGRESOS', f"{boleta.calcular_total_egresos():.2f}"],
        ]
        
        tabla_ingresos = Table(data_ingresos, colWidths=[2.166*inch, 1.084*inch])
        tabla_ingresos.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.Color(0.153, 0.682, 0.376, alpha=0.5)),  # Verde con opacidad 0.5
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 8),
            ('FONTSIZE', (0, 1), (-1, -1), 7),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 4),
            ('TOPPADDING', (0, 0), (-1, 0), 4),
            ('BACKGROUND', (0, 1), (-1, -2), colors.Color(0.565, 0.933, 0.565, alpha=0.5)),
            ('BACKGROUND', (0, -1), (-1, -1), colors.Color(0.118, 0.518, 0.286, alpha=0.5)),
            ('TEXTCOLOR', (0, -1), (-1, -1), colors.black),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('TOPPADDING', (0, 1), (-1, -1), 1.5),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 1.5),
        ]))
        
        tabla_egresos = Table(data_egresos, colWidths=[2.166*inch, 1.084*inch])
        tabla_egresos.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.Color(0.906, 0.298, 0.235, alpha=0.5)),  # Rojo con opacidad 0.5
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 8),
            ('FONTSIZE', (0, 1), (-1, -1), 7),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 4),
            ('TOPPADDING', (0, 0), (-1, 0), 4),
            ('BACKGROUND', (0, 1), (-1, -2), colors.Color(0.941, 0.502, 0.502, alpha=0.5)),
            ('BACKGROUND', (0, -1), (-1, -1), colors.Color(0.753, 0.224, 0.169, alpha=0.5)),
            ('TEXTCOLOR', (0, -1), (-1, -1), colors.black),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('TOPPADDING', (0, 1), (-1, -1), 1.5),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 1.5),
        ]))
        
        # Combinar ambas tablas en una sola tabla sin separación
        data_combinada = []
        for i in range(len(data_ingresos)):
            data_combinada.append(data_ingresos[i] + data_egresos[i])
        
        tabla_combinada = Table(data_combinada, colWidths=[2.166*inch, 1.084*inch, 2.166*inch, 1.084*inch])
        tabla_combinada.setStyle(TableStyle([
            # Estilos para columnas de INGRESOS (0, 1)
            ('BACKGROUND', (0, 0), (1, 0), colors.Color(0.153, 0.682, 0.376, alpha=0.5)),
            ('TEXTCOLOR', (0, 0), (1, 0), colors.black),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (1, 0), 8),
            ('FONTSIZE', (0, 1), (1, -1), 7),
            ('BOTTOMPADDING', (0, 0), (1, 0), 4),
            ('TOPPADDING', (0, 0), (1, 0), 4),
            ('BACKGROUND', (0, 1), (1, -2), colors.Color(0.565, 0.933, 0.565, alpha=0.5)),
            ('BACKGROUND', (0, -1), (1, -1), colors.Color(0.118, 0.518, 0.286, alpha=0.5)),
            ('TEXTCOLOR', (0, -1), (1, -1), colors.black),
            ('FONTNAME', (0, -1), (1, -1), 'Helvetica-Bold'),
            ('TOPPADDING', (0, 1), (1, -1), 1.5),
            ('BOTTOMPADDING', (0, 1), (1, -1), 1.5),
            # Estilos para columnas de EGRESOS (2, 3)
            ('BACKGROUND', (2, 0), (3, 0), colors.Color(0.906, 0.298, 0.235, alpha=0.5)),
            ('TEXTCOLOR', (2, 0), (3, 0), colors.black),
            ('ALIGN', (2, 0), (2, -1), 'LEFT'),
            ('ALIGN', (3, 0), (3, -1), 'RIGHT'),
            ('FONTNAME', (2, 0), (3, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (2, 0), (3, 0), 8),
            ('FONTSIZE', (2, 1), (3, -1), 7),
            ('BOTTOMPADDING', (2, 0), (3, 0), 4),
            ('TOPPADDING', (2, 0), (3, 0), 4),
            ('BACKGROUND', (2, 1), (3, -2), colors.Color(0.941, 0.502, 0.502, alpha=0.5)),
            ('BACKGROUND', (2, -1), (3, -1), colors.Color(0.753, 0.224, 0.169, alpha=0.5)),
            ('TEXTCOLOR', (2, -1), (3, -1), colors.black),
            ('FONTNAME', (2, -1), (3, -1), 'Helvetica-Bold'),
            ('TOPPADDING', (2, 1), (3, -1), 1.5),
            ('BOTTOMPADDING', (2, 1), (3, -1), 1.5),
            # Bordes
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ]))
        
        elements.append(tabla_combinada)
        elements.append(Spacer(1, 0))
        
        # Líquido pagable - compacto
        data_liquido = [
            ['LÍQUIDO PAGABLE', f"{boleta.calcular_liquido_pagable():.2f} Bs."],
        ]
        
        tabla_liquido = Table(data_liquido, colWidths=[4.5*inch, 2*inch])
        tabla_liquido.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.Color(0.161, 0.502, 0.725, alpha=0.5)),  # Azul con opacidad 0.5
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 1.5, colors.black),
        ]))
        
        elements.append(tabla_liquido)
        elements.append(Spacer(1, 0.22*inch))
        
        # Firmas - compacto
        data_firmas = [
            ['_____________________', '', '_____________________'],
            ['Firma Empleador', '', 'Firma Empleado'],
            ['Entregue Conforme', '', 'Recibí Conforme'],
        ]
        
        tabla_firmas = Table(data_firmas, colWidths=[3.0*inch, 1.34*inch, 3.0*inch])
        tabla_firmas.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, -1), 'CENTER'),
            ('ALIGN', (2, 0), (2, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 1), (-1, 1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 1), (-1, 1), 7),
            ('FONTSIZE', (0, 2), (-1, 2), 6),
            ('TOPPADDING', (0, 0), (-1, 0), 8),
            ('TOPPADDING', (0, 2), (-1, 2), 1),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ]))
        
        elements.append(tabla_firmas)
        
        # Construir PDF
        doc.build(elements)
        return filename
    
    def generar_boleta_aguinaldo(self, boleta):
        """Genera PDF para boleta de aguinaldo"""
        filename = os.path.join(self.output_dir, f"{boleta.numero_boleta}_Aguinaldo_{boleta.nombre_completo.replace(' ', '_')}.pdf")
        doc = SimpleDocTemplate(filename, pagesize=letter)
        elements = []
        styles = getSampleStyleSheet()
        
        # Estilo personalizado para título
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            textColor=colors.HexColor('#2C3E50'),
            spaceAfter=30,
            alignment=TA_CENTER
        )
        
        # Header
        self._add_header(elements, styles)
        
        # Título
        elements.append(Paragraph(f"<b>BOLETA DE PAGO DE AGUINALDO</b>", title_style))
        elements.append(Paragraph(f"<b>No. {boleta.numero_boleta}</b>", styles['Heading2']))
        elements.append(Spacer(1, 0.2*inch))
        
        # Datos del empleado
        data_empleado = [
            ['DATOS DEL EMPLEADO', ''],
            ['Nombre Completo:', boleta.nombre_completo],
            ['C.I.:', boleta.ci],
            ['Cargo:', boleta.cargo],
            ['Año:', str(boleta.anio)],
            ['Fecha de Ingreso:', boleta.fecha_ingreso],
            ['Período Trabajado:', f"{boleta.fecha_inicio} al {boleta.fecha_fin}"],
            ['Días Trabajados:', f"{boleta.calcular_dias_trabajados()} días ({boleta.calcular_meses_trabajados()} meses)"],
            ['Fecha de Emisión:', boleta.fecha_emision.strftime("%d/%m/%Y")],
            ['Método de Pago:', getattr(boleta, 'metodo_pago', 'EFECTIVO')],
        ]
        
        tabla_empleado = Table(data_empleado, colWidths=[2.5*inch, 4*inch])
        tabla_empleado.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495E')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
        ]))
        
        elements.append(tabla_empleado)
        elements.append(Spacer(1, 0.3*inch))
        
        # Cálculo del aguinaldo
        data_calculo = [
            ['CONCEPTO', 'MONTO (Bs.)'],
            ['Promedio últimos 3 pagos', f"{boleta.promedio_ultimos_3_pagos:.2f}"],
            ['Otros conceptos', f"{boleta.otros:.2f}"],
            ['TOTAL AGUINALDO', f"{boleta.calcular_liquido_pagable():.2f}"],
        ]
        
        tabla_calculo = Table(data_calculo, colWidths=[4.5*inch, 2*inch])
        tabla_calculo.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.Color(0.153, 0.682, 0.376, alpha=0.5)),  # Verde con opacidad 0.5
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -2), colors.Color(0.565, 0.933, 0.565, alpha=0.5)),
            ('BACKGROUND', (0, -1), (-1, -1), colors.Color(0.118, 0.518, 0.286, alpha=0.5)),
            ('TEXTCOLOR', (0, -1), (-1, -1), colors.black),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, -1), (-1, -1), 13),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        
        elements.append(tabla_calculo)
        elements.append(Spacer(1, 0.3*inch))
        
        # Líquido pagable
        data_liquido = [
            ['LÍQUIDO PAGABLE', f"{boleta.calcular_liquido_pagable():.2f} Bs."],
        ]
        
        tabla_liquido = Table(data_liquido, colWidths=[4.5*inch, 2*inch])
        tabla_liquido.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.Color(0.161, 0.502, 0.725, alpha=0.5)),  # Azul con opacidad 0.5
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 14),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('TOPPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 2, colors.black),
        ]))
        
        elements.append(tabla_liquido)
        elements.append(Spacer(1, 0.37*inch))
        
        # Nota legal
        nota = """
        <i>Nota: El aguinaldo corresponde al pago del doceavo del total ganado durante el año, 
        conforme a la legislación laboral vigente.</i>
        """
        elements.append(Paragraph(nota, styles['Normal']))
        elements.append(Spacer(1, 0.3*inch))
        
        # Firmas
        data_firmas = [
            ['_____________________', '', '_____________________'],
            ['Firma Empleador', '', 'Firma Empleado'],
            ['Entregue Conforme', '', 'Recibí Conforme'],
        ]
        
        tabla_firmas = Table(data_firmas, colWidths=[3.0*inch, 1.34*inch, 3.0*inch])
        tabla_firmas.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, -1), 'CENTER'),
            ('ALIGN', (2, 0), (2, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 1), (-1, 1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 2), (-1, 2), 9),
            ('TOPPADDING', (0, 0), (-1, 0), 20),
            ('TOPPADDING', (0, 2), (-1, 2), 1),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ]))
        
        elements.append(tabla_firmas)
        
        # Construir PDF
        doc.build(elements)
        return filename
    
    def generar_boleta_liquidacion(self, boleta):
        """Genera PDF para boleta de liquidación"""
        filename = os.path.join(self.output_dir, f"{boleta.numero_boleta}_Liquidacion_{boleta.nombre_completo.replace(' ', '_')}.pdf")
        doc = SimpleDocTemplate(filename, pagesize=letter)
        elements = []
        styles = getSampleStyleSheet()
        
        # Estilo personalizado para título
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            textColor=colors.HexColor('#2C3E50'),
            spaceAfter=30,
            alignment=TA_CENTER
        )
        
        # Header
        self._add_header(elements, styles)
        
        # Título
        elements.append(Paragraph(f"<b>BOLETA DE LIQUIDACIÓN</b>", title_style))
        elements.append(Paragraph(f"<b>No. {boleta.numero_boleta}</b>", styles['Heading2']))
        elements.append(Spacer(1, 0.2*inch))
        
        # Datos del empleado
        tiempo_servicio = boleta.calcular_tiempo_servicio()
        data_empleado = [
            ['DATOS DEL TRABAJADOR', ''],
            ['Nombre Completo:', boleta.nombre_completo],
            ['C.I.:', boleta.ci],
            ['Domicilio:', boleta.domicilio_trabajador],
            ['Cargo:', boleta.cargo],
            ['Fecha de Ingreso:', boleta.fecha_ingreso],
            ['Fecha de Retiro:', boleta.fecha_retiro],
            ['Tiempo de Servicio:', f"{tiempo_servicio['anios']} años, {tiempo_servicio['meses']} meses, {tiempo_servicio['dias']} días"],
            ['Fecha de Emisión:', boleta.fecha_emision.strftime("%d/%m/%Y")],
            ['Método de Pago:', getattr(boleta, 'metodo_pago', 'EFECTIVO')],
        ]
        
        tabla_empleado = Table(data_empleado, colWidths=[2.5*inch, 4*inch])
        tabla_empleado.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495E')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
        ]))
        
        elements.append(tabla_empleado)
        elements.append(Spacer(1, 0.3*inch))
        
        # Remuneraciones
        data_remuneraciones = [
            ['REMUNERACIONES', 'MONTO (Bs.)'],
            ['Último Sueldo', f"{boleta.ultimo_sueldo:.2f}"],
            ['Promedio últimos 3 sueldos', f"{boleta.promedio_ultimos_3_sueldos:.2f}"],
        ]
        
        tabla_remuneraciones = Table(data_remuneraciones, colWidths=[4.5*inch, 2*inch])
        tabla_remuneraciones.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#8E44AD')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lavender),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        
        elements.append(tabla_remuneraciones)
        elements.append(Spacer(1, 0.2*inch))
        
        # Beneficios sociales
        data_beneficios = [
            ['BENEFICIOS SOCIALES', 'MONTO (Bs.)'],
            ['Indemnización', f"{boleta.indemnizacion:.2f}"],
            ['Aguinaldo', f"{boleta.aguinaldo:.2f}"],
            ['Vacaciones', f"{boleta.vacaciones:.2f}"],
            ['Otros Beneficios', f"{boleta.otros_beneficios:.2f}"],
            ['TOTAL BENEFICIOS', f"{boleta.calcular_total_beneficios():.2f}"],
        ]
        
        tabla_beneficios = Table(data_beneficios, colWidths=[4.5*inch, 2*inch])
        tabla_beneficios.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.Color(0.153, 0.682, 0.376, alpha=0.5)),  # Verde con opacidad 0.5
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -2), colors.Color(0.565, 0.933, 0.565, alpha=0.5)),
            ('BACKGROUND', (0, -1), (-1, -1), colors.Color(0.118, 0.518, 0.286, alpha=0.5)),
            ('TEXTCOLOR', (0, -1), (-1, -1), colors.black),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        
        elements.append(tabla_beneficios)
        elements.append(Spacer(1, 0.2*inch))
        
        # Deducciones
        data_deducciones = [
            ['DEDUCCIONES Y ANTICIPOS', 'MONTO (Bs.)'],
            ['Anticipos', f"{boleta.anticipos:.2f}"],
            ['Préstamos', f"{boleta.prestamos:.2f}"],
            ['Otras Deducciones', f"{boleta.otras_deducciones:.2f}"],
            ['TOTAL DEDUCCIONES', f"{boleta.calcular_total_deducciones():.2f}"],
        ]
        
        tabla_deducciones = Table(data_deducciones, colWidths=[4.5*inch, 2*inch])
        tabla_deducciones.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.Color(0.906, 0.298, 0.235, alpha=0.5)),  # Rojo con opacidad 0.5
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -2), colors.Color(0.941, 0.502, 0.502, alpha=0.5)),
            ('BACKGROUND', (0, -1), (-1, -1), colors.Color(0.753, 0.224, 0.169, alpha=0.5)),
            ('TEXTCOLOR', (0, -1), (-1, -1), colors.black),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        
        elements.append(tabla_deducciones)
        elements.append(Spacer(1, 0.3*inch))
        
        # Líquido pagable
        data_liquido = [
            ['LÍQUIDO PAGABLE', f"{boleta.calcular_liquido_pagable():.2f} Bs."],
        ]
        
        tabla_liquido = Table(data_liquido, colWidths=[4.5*inch, 2*inch])
        tabla_liquido.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.Color(0.161, 0.502, 0.725, alpha=0.5)),  # Azul con opacidad 0.5
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 14),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('TOPPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 2, colors.black),
        ]))
        
        elements.append(tabla_liquido)
        elements.append(Spacer(1, 0.37*inch))
        
        # Firmas
        data_firmas = [
            ['_____________________', '', '_____________________'],
            ['Firma Empleador', '', 'Firma Empleado'],
            ['Entregue Conforme', '', 'Recibí Conforme'],
        ]
        
        tabla_firmas = Table(data_firmas, colWidths=[3.0*inch, 1.34*inch, 3.0*inch])
        tabla_firmas.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, -1), 'CENTER'),
            ('ALIGN', (2, 0), (2, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 1), (-1, 1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 2), (-1, 2), 9),
            ('TOPPADDING', (0, 0), (-1, 0), 20),
            ('TOPPADDING', (0, 2), (-1, 2), 1),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ]))
        
        elements.append(tabla_firmas)
        
        # Construir PDF
        doc.build(elements)
        return filename
