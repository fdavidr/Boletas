"""
Generador de PDFs para las boletas
Crea PDFs profesionales con formato adecuado
"""

import os
from io import BytesIO
from reportlab.lib.pagesizes import letter, legal
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from datetime import datetime

class PDFGenerator:
    def __init__(self, empresa_config, output_dir=None):
        self.empresa_config = empresa_config
        # Usar carpeta persistente en Render, local en desarrollo
        if output_dir is None:
            data_dir = os.environ.get('RENDER_DISK_PATH', 'data')
            output_dir = os.path.join(data_dir, 'output')
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
    
    def _get_logo_image(self, width, height):
        """Obtiene el logo desde la base de datos y lo convierte a objeto Image"""
        if not self.empresa_config.logo_exists():
            return None
        
        try:
            logo_data, logo_mimetype = self.empresa_config.get_logo_data()
            if logo_data:
                # Crear objeto BytesIO desde los bytes del logo
                logo_stream = BytesIO(logo_data)
                # Crear objeto Image de ReportLab desde el stream
                logo = Image(logo_stream, width=width, height=height)
                return logo
        except Exception as e:
            print(f"Error al cargar logo: {e}")
            return None
        
        return None
    
    def _add_header(self, elements, styles):
        """Agrega el encabezado con logo y datos de empresa"""
        empresa = self.empresa_config.get_empresa_data()
        
        # Crear tabla para el encabezado
        header_data = []
        
        # Si existe logo, agregarlo desde la base de datos
        logo = self._get_logo_image(width=1*inch, height=1*inch)
        if logo:
            header_data.append([logo, Paragraph(f"<b>{empresa['nombre']}</b><br/>{empresa['eslogan']}", styles['Title'])])
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
        logo = None
        if self.empresa_config.logo_exists():
            try:
                logo_data, logo_mimetype = self.empresa_config.get_logo_data()
                if logo_data:
                    from PIL import Image as PILImage
                    # Cargar imagen desde bytes para obtener dimensiones
                    img_stream = BytesIO(logo_data)
                    img = PILImage.open(img_stream)
                    aspect_ratio = img.width / img.height
                    logo_height = 2.0 * inch  # Aumentado de 0.8 a 2.0 inches para mayor visibilidad
                    logo_width = logo_height * aspect_ratio
                    # Crear imagen de ReportLab desde bytes
                    logo_stream = BytesIO(logo_data)
                    logo = Image(logo_stream, width=logo_width, height=logo_height)
            except Exception as e:
                print(f"Error al cargar logo: {e}")
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
        fecha_str = boleta.fecha_emision.strftime("%d/%m/%Y")
        metodo_pago = getattr(boleta, 'metodo_pago', 'EFECTIVO')
        data_empleado = [
            ['Nombre:', boleta.nombre_completo, 'C.I.:', boleta.ci],
            ['Cargo:', boleta.cargo, 'Fecha:', fecha_str],
            ['Período:', f"{boleta.mes_pago} {boleta.anio}", 'Método Pago:', metodo_pago],
        ]
        
        if boleta.rango_fechas:
            data_empleado.append(['Rango:', boleta.rango_fechas, '', ''])
        
        tabla_empleado = Table(data_empleado, colWidths=[1.0*inch, 2.53*inch, 1.15*inch, 1.82*inch])
        tabla_empleado.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.8, colors.black),
            ('BOX', (0, 0), (-1, -1), 1.2, colors.black),
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
            ['Anticipos', f"{boleta.reposiciones:.2f}"],
            ['Otros Egresos', f"{boleta.otros_egresos:.2f}"],
            ['TOTAL EGRESOS', f"{boleta.calcular_total_egresos():.2f}"],
        ]
        
        tabla_ingresos = Table(data_ingresos, colWidths=[2.166*inch, 1.084*inch])
        tabla_ingresos.setStyle(TableStyle([
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 8),
            ('FONTSIZE', (0, 1), (-1, -1), 7),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 4),
            ('TOPPADDING', (0, 0), (-1, 0), 4),
            ('TEXTCOLOR', (0, -1), (-1, -1), colors.black),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('TOPPADDING', (0, 1), (-1, -1), 1.5),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 1.5),
            ('BOX', (0, 0), (-1, -1), 1.2, colors.HexColor('#2ECC71')),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#2ECC71')),
        ]))
        
        tabla_egresos = Table(data_egresos, colWidths=[2.166*inch, 1.084*inch])
        tabla_egresos.setStyle(TableStyle([
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 8),
            ('FONTSIZE', (0, 1), (-1, -1), 7),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 4),
            ('TOPPADDING', (0, 0), (-1, 0), 4),
            ('TEXTCOLOR', (0, -1), (-1, -1), colors.black),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('TOPPADDING', (0, 1), (-1, -1), 1.5),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 1.5),
            ('BOX', (0, 0), (-1, -1), 1.2, colors.HexColor('#E74C3C')),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E74C3C')),
        ]))
        
        # Combinar ambas tablas en una sola tabla sin separación
        data_combinada = []
        for i in range(len(data_ingresos)):
            data_combinada.append(data_ingresos[i] + data_egresos[i])
        
        tabla_combinada = Table(data_combinada, colWidths=[2.166*inch, 1.084*inch, 2.166*inch, 1.084*inch])
        tabla_combinada.setStyle(TableStyle([
            # Estilos para columnas de INGRESOS (0, 1)
            ('TEXTCOLOR', (0, 0), (1, 0), colors.black),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (1, 0), 8),
            ('FONTSIZE', (0, 1), (1, -1), 7),
            ('BOTTOMPADDING', (0, 0), (1, 0), 4),
            ('TOPPADDING', (0, 0), (1, 0), 4),
            ('TEXTCOLOR', (0, -1), (1, -1), colors.black),
            ('FONTNAME', (0, -1), (1, -1), 'Helvetica-Bold'),
            ('TOPPADDING', (0, 1), (1, -1), 1.5),
            ('BOTTOMPADDING', (0, 1), (1, -1), 1.5),
            # Estilos para columnas de EGRESOS (2, 3)
            ('TEXTCOLOR', (2, 0), (3, 0), colors.black),
            ('ALIGN', (2, 0), (2, -1), 'LEFT'),
            ('ALIGN', (3, 0), (3, -1), 'RIGHT'),
            ('FONTNAME', (2, 0), (3, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (2, 0), (3, 0), 8),
            ('FONTSIZE', (2, 1), (3, -1), 7),
            ('BOTTOMPADDING', (2, 0), (3, 0), 4),
            ('TOPPADDING', (2, 0), (3, 0), 4),
            ('TEXTCOLOR', (2, -1), (3, -1), colors.black),
            ('FONTNAME', (2, -1), (3, -1), 'Helvetica-Bold'),
            ('TOPPADDING', (2, 1), (3, -1), 1.5),
            ('BOTTOMPADDING', (2, 1), (3, -1), 1.5),
            # Bordes diferenciados
            ('BOX', (0, 0), (1, -1), 1.2, colors.HexColor('#2ECC71')),
            ('GRID', (0, 0), (1, -1), 0.5, colors.HexColor('#2ECC71')),
            ('BOX', (2, 0), (3, -1), 1.2, colors.HexColor('#E74C3C')),
            ('GRID', (2, 0), (3, -1), 0.5, colors.HexColor('#E74C3C')),
        ]))
        
        elements.append(tabla_combinada)
        elements.append(Spacer(1, 0))
        
        # Líquido pagable - compacto
        data_liquido = [
            ['LÍQUIDO PAGABLE', f"{boleta.calcular_liquido_pagable():.2f} Bs."],
        ]
        
        tabla_liquido = Table(data_liquido, colWidths=[4.5*inch, 2*inch])
        tabla_liquido.setStyle(TableStyle([
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
            ('TOPPADDING', (0, 1), (-1, 1), 2),
            ('TOPPADDING', (0, 2), (-1, 2), 0),
            ('BOTTOMPADDING', (0, 1), (-1, 1), 1),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ]))
        
        elements.append(tabla_firmas)
        
        # Construir PDF
        doc.build(elements)
        return filename
    
    def generar_boleta_aguinaldo(self, boleta):
        """Genera PDF para boleta de aguinaldo - Diseño compacto mitad de página"""
        filename = os.path.join(self.output_dir, f"{boleta.numero_boleta}_Aguinaldo_{boleta.nombre_completo.replace(' ', '_')}.pdf")
        doc = SimpleDocTemplate(filename, pagesize=letter, topMargin=0.3*inch, bottomMargin=0.3*inch, leftMargin=0.5*inch, rightMargin=0.5*inch)
        elements = []
        styles = getSampleStyleSheet()
        
        # Estilo para título centrado
        title_style = ParagraphStyle(
            'TitleStyle',
            parent=styles['Normal'],
            fontSize=14,
            textColor=colors.HexColor('#000000'),
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
        
        # Logo (columna izquierda)
        logo = None
        if self.empresa_config.logo_exists():
            try:
                logo_data, logo_mimetype = self.empresa_config.get_logo_data()
                if logo_data:
                    from PIL import Image as PILImage
                    # Cargar imagen desde bytes para obtener dimensiones
                    img_stream = BytesIO(logo_data)
                    img = PILImage.open(img_stream)
                    aspect_ratio = img.width / img.height
                    logo_height = 2.0 * inch  # Aumentado de 0.8 a 2.0 inches para mayor visibilidad
                    logo_width = logo_height * aspect_ratio
                    # Crear imagen de ReportLab desde bytes
                    logo_stream = BytesIO(logo_data)
                    logo = Image(logo_stream, width=logo_width, height=logo_height)
            except Exception as e:
                print(f"Error al cargar logo: {e}")
                logo = ''
        else:
            logo = ''
        
        # Título (columna central)
        titulo = Paragraph(f"<b>BOLETA DE AGUINALDO</b><br/><font size=9>No. {boleta.numero_boleta}</font>", title_style)
        
        # Datos empresa (columna derecha)
        datos_empresa = Paragraph(
            f"<b>{empresa['nombre']}</b><br/>"
            f"{empresa.get('eslogan', '')}<br/>"
            f"NIT: {empresa.get('nit', 'N/A')}<br/>"
            f"Tel: {empresa.get('telefono', 'N/A')}<br/>"
            f"{empresa.get('direccion', 'N/A')}",
            empresa_style
        )
        
        # Tabla de header con 3 columnas
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
        fecha_str = boleta.fecha_emision.strftime("%d/%m/%Y")
        metodo_pago = getattr(boleta, 'metodo_pago', 'EFECTIVO')
        meses_completos, dias_adicionales = boleta.calcular_meses_completos_y_dias()
        
        data_empleado = [
            ['Nombre:', boleta.nombre_completo, 'C.I.:', boleta.ci],
            ['Cargo:', boleta.cargo, 'Año:', str(boleta.anio)],
            ['Período:', f"{boleta.fecha_inicio} al {boleta.fecha_fin}", 'Fecha:', fecha_str],
            ['Tiempo:', f"{meses_completos} mes(es), {dias_adicionales} día(s)", 'Método Pago:', metodo_pago],
        ]
        
        tabla_empleado = Table(data_empleado, colWidths=[1.0*inch, 2.53*inch, 1.15*inch, 1.82*inch])
        tabla_empleado.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.8, colors.black),
            ('BOX', (0, 0), (-1, -1), 1.2, colors.black),
            ('TOPPADDING', (0, 0), (-1, -1), 2),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ]))
        
        elements.append(tabla_empleado)
        elements.append(Spacer(1, 0.12*inch))
        
        # Cálculo del aguinaldo con desglose - compacto
        aguinaldo_base = boleta.calcular_aguinaldo_proporcional()
        
        data_calculo = [
            ['CÁLCULO DEL AGUINALDO', 'Bs.'],
            ['Sueldo Promedio', f"{boleta.promedio_ultimos_3_pagos:.2f}"],
        ]
        
        # Agregar desglose según el caso
        if meses_completos == 12 and dias_adicionales == 0:
            data_calculo.append(['Aguinaldo (12 meses completos)', f"{aguinaldo_base:.2f}"])
        elif meses_completos > 0 or dias_adicionales > 0:
            if meses_completos > 0:
                monto_meses = (boleta.promedio_ultimos_3_pagos / 12) * meses_completos
                data_calculo.append([f'{meses_completos} mes(es): (÷12) × {meses_completos}', f"{monto_meses:.2f}"])
            if dias_adicionales > 0:
                monto_dias = (boleta.promedio_ultimos_3_pagos / 360) * dias_adicionales
                data_calculo.append([f'{dias_adicionales} día(s): (÷360) × {dias_adicionales}', f"{monto_dias:.2f}"])
            data_calculo.append(['Subtotal Aguinaldo', f"{aguinaldo_base:.2f}"])
        
        if boleta.otros > 0:
            data_calculo.append(['Otros conceptos', f"{boleta.otros:.2f}"])
        
        data_calculo.append(['TOTAL AGUINALDO', f"{boleta.calcular_liquido_pagable():.2f}"])
        
        tabla_calculo = Table(data_calculo, colWidths=[5.0*inch, 1.5*inch])
        tabla_calculo.setStyle(TableStyle([
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 8),
            ('FONTSIZE', (0, 1), (-1, -2), 7),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 4),
            ('TOPPADDING', (0, 0), (-1, 0), 4),
            ('TEXTCOLOR', (0, -1), (-1, -1), colors.black),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, -1), (-1, -1), 9),
            ('TOPPADDING', (0, 1), (-1, -1), 1.5),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 1.5),
            ('BOX', (0, 0), (-1, -1), 1.2, colors.HexColor('#F39C12')),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#F39C12')),
        ]))
        
        elements.append(tabla_calculo)
        elements.append(Spacer(1, 0.12*inch))
        
        # Firmas - compacto
        data_firmas = [
            ['____________________________', '', '____________________________'],
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
            ('TOPPADDING', (0, 1), (-1, 1), 2),
            ('TOPPADDING', (0, 2), (-1, 2), 0),
            ('BOTTOMPADDING', (0, 1), (-1, 1), 1),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ]))
        
        elements.append(tabla_firmas)
        
        # Construir PDF con márgenes compactos
        doc = SimpleDocTemplate(
            filename, 
            pagesize=letter,
            topMargin=0.3*inch,
            bottomMargin=0.3*inch,
            leftMargin=0.5*inch,
            rightMargin=0.5*inch
        )
        doc.build(elements)
        return filename
    
    def generar_boleta_liquidacion(self, boleta):
        """Genera PDF para boleta de liquidación - Tamaño oficio (legal), una sola hoja"""
        filename = os.path.join(self.output_dir, f"{boleta.numero_boleta}_Liquidacion_{boleta.nombre_completo.replace(' ', '_')}.pdf")
        doc = SimpleDocTemplate(
            filename,
            pagesize=legal,
            topMargin=0.35*inch, bottomMargin=0.35*inch,
            leftMargin=0.5*inch, rightMargin=0.5*inch
        )
        elements = []
        styles = getSampleStyleSheet()

        # ── Estilos compactos ─────────────────────────────────────────────────
        title_style = ParagraphStyle(
            'LiqTitle',
            parent=styles['Normal'],
            fontSize=13,
            textColor=colors.HexColor('#2C3E50'),
            alignment=TA_CENTER,
            fontName='Helvetica-Bold',
            spaceAfter=2,
        )
        empresa_style = ParagraphStyle(
            'EmpresaStyle',
            parent=styles['Normal'],
            fontSize=7,
            alignment=TA_RIGHT,
            leading=9,
        )
        nota_style = ParagraphStyle(
            'NotaStyle',
            parent=styles['Normal'],
            fontSize=8,
            leading=11,
        )

        # ── Header: Logo | Título | Datos Empresa ─────────────────────────────
        empresa = self.empresa_config.get_empresa_data()

        # Logo con proporciones preservadas
        logo = ''
        if self.empresa_config.logo_exists():
            try:
                logo_data, logo_mimetype = self.empresa_config.get_logo_data()
                if logo_data:
                    from PIL import Image as PILImage
                    img_stream = BytesIO(logo_data)
                    img = PILImage.open(img_stream)
                    aspect_ratio = img.width / img.height
                    logo_height = 1.1 * inch
                    logo_width = logo_height * aspect_ratio
                    logo_stream = BytesIO(logo_data)
                    logo = Image(logo_stream, width=logo_width, height=logo_height)
            except Exception as e:
                print(f"Error al cargar logo: {e}")

        titulo_header = Paragraph(
            f"<b>BOLETA DE LIQUIDACIÓN</b><br/>"
            f"<font size=9>No. {boleta.numero_boleta}</font>",
            title_style
        )

        datos_empresa = Paragraph(
            f"<b>{empresa['nombre']}</b><br/>"
            f"{empresa.get('eslogan', '')}<br/>"
            f"NIT: {empresa.get('nit', 'N/A')}<br/>"
            f"Tel: {empresa.get('telefono', 'N/A')}<br/>"
            f"{empresa.get('direccion', 'N/A')}",
            empresa_style
        )

        # 2.0 + 3.5 + 2.0 = 7.5" (ancho útil legal con márgenes 0.5" c/u)
        header_table = Table([[logo, titulo_header, datos_empresa]],
                             colWidths=[2.0*inch, 3.5*inch, 2.0*inch])
        header_table.setStyle(TableStyle([
            ('ALIGN',  (0, 0), (0, 0), 'LEFT'),
            ('ALIGN',  (1, 0), (1, 0), 'CENTER'),
            ('ALIGN',  (2, 0), (2, 0), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LINEBELOW', (0, 0), (-1, 0), 1.2, colors.HexColor('#2C3E50')),
        ]))
        elements.append(header_table)
        elements.append(Spacer(1, 0.1*inch))

        # ── Datos del empleado (4 columnas: etiqueta | valor | etiqueta | valor) ─
        tiempo_servicio = boleta.calcular_tiempo_servicio()
        ts = f"{tiempo_servicio['anios']} años, {tiempo_servicio['meses']} meses, {tiempo_servicio['dias']} días"
        data_empleado = [
            ['DATOS DEL TRABAJADOR', '', '', ''],
            ['Nombre Completo:', boleta.nombre_completo,   'C.I.:',            boleta.ci],
            ['Cargo:',          boleta.cargo,              'Domicilio:',       boleta.domicilio_trabajador],
            ['Fecha de Ingreso:', boleta.fecha_ingreso,    'Fecha de Retiro:', boleta.fecha_retiro],
            ['Tiempo de Servicio:', ts,                    'Fecha de Emisión:', boleta.fecha_emision.strftime("%d/%m/%Y")],
            ['Método de Pago:', getattr(boleta, 'metodo_pago', 'EFECTIVO'), '', ''],
        ]

        # Anchos: etiqueta1 | valor1 | etiqueta2 | valor2  → total = 7.5"
        col_w = [1.3*inch, 2.45*inch, 1.3*inch, 2.45*inch]
        tabla_empleado = Table(data_empleado, colWidths=col_w)
        tabla_empleado.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495E')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('SPAN', (0, 0), (-1, 0)),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 5),
            ('TOPPADDING', (0, 0), (-1, 0), 5),
            ('TOPPADDING', (0, 1), (-1, -1), 2),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 2),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 0.8, colors.black),
            # Etiquetas en negrita (col 0 y col 2)
            ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (2, 1), (2, -1), 'Helvetica-Bold'),
            # Última fila: método de pago abarca columnas 1-3
            ('SPAN', (1, -1), (-1, -1)),
        ]))
        elements.append(tabla_empleado)
        elements.append(Spacer(1, 0.1*inch))

        # ── Fila 1: Remuneraciones ancho completo (7.5") ──────────────────────
        data_rem = [
            ['REMUNERACIONES', 'Bs.'],
            ['Último Sueldo', f"{boleta.ultimo_sueldo:.2f}"],
            ['Promedio últimos 3 sueldos', f"{boleta.promedio_ultimos_3_sueldos:.2f}"],
        ]
        tabla_rem = Table(data_rem, colWidths=[3.75*inch, 3.75*inch])
        tabla_rem.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#8E44AD')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 4), ('TOPPADDING', (0, 0), (-1, 0), 4),
            ('TOPPADDING', (0, 1), (-1, -1), 2), ('BOTTOMPADDING', (0, 1), (-1, -1), 2),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lavender),
            ('GRID', (0, 0), (-1, -1), 0.8, colors.black),
        ]))
        elements.append(tabla_rem)

        # ── Fila 2: Beneficios + Deducciones lado a lado (3.75" cada uno) ────
        # Beneficios
        data_ben = [
            ['BENEFICIOS SOCIALES', 'Bs.'],
            ['Indemnización', f"{boleta.indemnizacion:.2f}"],
            ['Aguinaldo', f"{boleta.aguinaldo:.2f}"],
            ['Vacaciones', f"{boleta.vacaciones:.2f}"],
            ['Otros Beneficios', f"{boleta.otros_beneficios:.2f}"],
            ['TOTAL BENEFICIOS', f"{boleta.calcular_total_beneficios():.2f}"],
        ]
        tabla_ben = Table(data_ben, colWidths=[2.95*inch, 0.8*inch])
        tabla_ben.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.Color(0.153, 0.682, 0.376, alpha=0.9)),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 4), ('TOPPADDING', (0, 0), (-1, 0), 4),
            ('TOPPADDING', (0, 1), (-1, -1), 2), ('BOTTOMPADDING', (0, 1), (-1, -1), 2),
            ('BACKGROUND', (0, 1), (-1, -2), colors.Color(0.565, 0.933, 0.565, alpha=0.5)),
            ('BACKGROUND', (0, -1), (-1, -1), colors.Color(0.118, 0.518, 0.286, alpha=0.5)),
            ('GRID', (0, 0), (-1, -1), 0.8, colors.black),
        ]))

        # Deducciones
        data_ded = [
            ['DEDUCCIONES', 'Bs.'],
            ['Anticipos', f"{boleta.anticipos:.2f}"],
            ['Préstamos', f"{boleta.prestamos:.2f}"],
            ['Otras Deducciones', f"{boleta.otras_deducciones:.2f}"],
            ['', ''],
            ['TOTAL DEDUCCIONES', f"{boleta.calcular_total_deducciones():.2f}"],
        ]
        tabla_ded = Table(data_ded, colWidths=[2.95*inch, 0.8*inch])
        tabla_ded.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.Color(0.906, 0.298, 0.235, alpha=0.8)),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 4), ('TOPPADDING', (0, 0), (-1, 0), 4),
            ('TOPPADDING', (0, 1), (-1, -1), 2), ('BOTTOMPADDING', (0, 1), (-1, -1), 2),
            ('BACKGROUND', (0, 1), (-1, -2), colors.Color(0.941, 0.502, 0.502, alpha=0.5)),
            ('BACKGROUND', (0, -1), (-1, -1), colors.Color(0.753, 0.224, 0.169, alpha=0.5)),
            ('GRID', (0, 0), (-1, -1), 0.8, colors.black),
        ]))

        # Beneficios + Deducciones en la misma fila → 3.75" + 3.75" = 7.5"
        tabla_duo = Table([[tabla_ben, tabla_ded]], colWidths=[3.75*inch, 3.75*inch])
        tabla_duo.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ('TOPPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ]))
        elements.append(tabla_duo)
        elements.append(Spacer(1, 0.1*inch))

        # ── Líquido pagable ───────────────────────────────────────────────────
        data_liquido = [['LÍQUIDO PAGABLE', f"{boleta.calcular_liquido_pagable():.2f} Bs."]]
        tabla_liquido = Table(data_liquido, colWidths=[5.5*inch, 2.0*inch])
        tabla_liquido.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F25838')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.white),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1.5, colors.black),
        ]))
        elements.append(tabla_liquido)
        elements.append(Spacer(1, 0.1*inch))

        # ── Nota (siempre visible con 10 líneas vacías de espacio) ───────────
        nota_texto = getattr(boleta, 'nota', '').strip()
        saltos = '<br/>' * 10
        data_nota = [
            ['NOTA'],
            [Paragraph(nota_texto + saltos, nota_style)],
        ]
        tabla_nota = Table(data_nota, colWidths=[7.5*inch], rowHeights=[None, 2.0*inch])
        tabla_nota.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#ECF0F1')),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 3), ('TOPPADDING', (0, 0), (-1, 0), 3),
            ('BOTTOMPADDING', (0, 1), (-1, 1), 5), ('TOPPADDING', (0, 1), (-1, 1), 4),
            ('FONTSIZE', (0, 1), (-1, 1), 8),
            ('GRID', (0, 0), (-1, -1), 0.8, colors.black),
        ]))
        elements.append(tabla_nota)
        elements.append(Spacer(1, 1.5*inch))

        # ── Firmas ────────────────────────────────────────────────────────────
        data_firmas = [
            ['_____________________', '', '_____________________'],
            ['Firma Empleador', '', 'Firma Empleado'],
            ['Entregue Conforme', '', 'Recibí Conforme'],
        ]
        tabla_firmas = Table(data_firmas, colWidths=[3.0*inch, 1.5*inch, 3.0*inch])
        tabla_firmas.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, -1), 'CENTER'),
            ('ALIGN', (2, 0), (2, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 1), (-1, 1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('FONTSIZE', (0, 2), (-1, 2), 8),
            ('TOPPADDING', (0, 0), (-1, 0), 16),
            ('TOPPADDING', (0, 2), (-1, 2), 1),
        ]))
        elements.append(tabla_firmas)

        doc.build(elements)
        return filename
