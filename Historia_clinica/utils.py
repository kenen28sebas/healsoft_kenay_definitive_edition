# historia/utils.py
# from usuarios.models import Usuario
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
import io



def generar_pdf_historia_clinica(historia):

    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    y = height - inch

    paciente = historia.paciente
    medico = historia.medico
    usuario_paciente = paciente.usuario
    usuario_medico = medico.usuario



    def write_line(text, font="Helvetica", size=10, offset=15):
        nonlocal y
        p.setFont(font, size)
        p.drawString(50, y, text)
        y -= offset
        if y < 100:
            p.showPage()
            y = height - inch

    write_line("HISTORIA CLÍNICA", font="Helvetica-Bold", size=14, offset=25)
    write_line(f"Número de folio: {historia.Nro_folio}")
    write_line(f"Número de historia: {historia.Nro_historia}")
    write_line(f"Fecha de atención: {historia.fecha_atencion.strftime('%d/%m/%Y')}")
    write_line(f"Paciente: {historia.paciente.usuario.first_name}, {historia.paciente.usuario.last_name}")
    write_line(f"Médico: {historia.medico.usuario.first_name}, {historia.medico.usuario.last_name}")

    write_line("---- ANAMNESIS ----", font="Helvetica-Bold")
    anamnesis = historia.anamnesis
    write_line(f"Motivo consulta: {anamnesis.motivo_consulta}")
    write_line(f"Síntomas: {anamnesis.sintomas}")
    write_line(f"Examen Físico: {anamnesis.examen_fisico}")
    write_line(f"Enfermedad de Base: {anamnesis.enfermedades_base}")
    
    

    write_line("---- SIGNOS VITALES ----", font="Helvetica-Bold")
    signos = historia.signos_vitales
    write_line(f"Peso: {signos.peso} kg")
    write_line(f"Talla: {signos.talla} cm")
    write_line(f"Presión arterial: {signos.presion_arterial}")
    write_line(f"Frecuencia cardiaca: {signos.frecuencia_cardiaca}")
    write_line(f"Frecuencia respiratoria: {signos.frecuencia_respiratoria}")
    write_line(f"Temperatura: {signos.temperatura_corporal} °C")

    write_line("---- PARACLÍNICOS ----", font="Helvetica-Bold")
    para = historia.paraclinicos
    write_line(f"Laboratorios: {para.resultados}")
    write_line(f"Radiología: {para.analisis}")


    write_line("---- DIAGNÓSTICOS ----", font="Helvetica-Bold")
    for diag in historia.diagnostico.all():
        write_line(f"{diag.tipo_diagnostico}: {diag.cie10.codigo_cie10} - {diag.cie10.descripcion_cie10}")
        write_line(f"Observaciones: {diag.observaciones}")

    write_line("---- FÓRMULAS MÉDICAS ----", font="Helvetica-Bold")
    formularios = historia.formula_medica.all()
    for formula in formularios:
        write_line(f"Prescrita el {formula.fecha_prescripcion.strftime('%d/%m/%Y %I:%M %p')} por {formula.medico.usuario.get_full_name()}")
        write_line(f"Diagnóstico: {formula.diagnostico.cie10.codigo_cie10} - {formula.diagnostico.cie10.descripcion_cie10}")
        for med in formula.medicamentos.all():
            write_line(f"-  ({med.nombre_medicamento}) - {med.concentracion},{med.dosis}, cada {med.frecuencia}, por {med.tiempo_tratamiento} días")

    write_line("---- ÓRDENES DE PROCEDIMIENTO ----", font="Helvetica-Bold")
    ordenes = historia.orden_de_procedimientos.all()
    for orden in ordenes:
        write_line(f" {orden.cups.codigo_cups} - {orden.cups.nombre_cups},{orden.descripcion}, {orden.cantidad},")

    write_line("---- EVOLUCIONES ----", font="Helvetica-Bold")
    evoluciones = historia.evolucion.all()
    for evo in evoluciones:
        write_line(f"{evo.fecha_actual.strftime('%d/%m/%Y')} - Médico: {evo.medico.usuario.get_full_name()}")
        write_line(f"Estado: {evo.estado_paciente}")
        write_line(f"Diagnóstico: {evo.diagnostico.cie10.codigo_cie10}")
        write_line(f"Evolución: {evo.evolucion}")
        write_line(f"Plan: {evo.plan_de_manejo}")
        write_line(f"Recomendaciones: {evo.recomendaciones}")
        write_line(f"Seguimiento: {evo.plan_de_seguimiento}")
        write_line(f"Interconsultas: {evo.interconsultas}")

    p.showPage()
    p.save()
    buffer.seek(0)
    return buffer


### GENERAR FORMULA MÉDICA
def generar_pdf_formula_medica(formula):
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    y = height - inch

    def write_line(text, font="Helvetica", size=10, offset=15):
        nonlocal y
        p.setFont(font, size)
        p.drawString(50, y, text)
        y -= offset
        if y < 100:
            p.showPage()
            y = height - inch

    paciente = formula.historia_clinica.paciente.usuario
    medico = formula.medico.usuario

    write_line("FÓRMULA MÉDICA", font="Helvetica-Bold", size=14, offset=25)
    write_line(f"Fecha de prescripción: {formula.fecha_prescripcion.strftime('%d/%m/%Y %I:%M %p')}")
    write_line(f"Paciente: {paciente.first_name} {paciente.last_name}")
    

    write_line("---- MEDICAMENTOS ----", font="Helvetica-Bold")
    for med in formula.medicamentos.all():
        write_line(f"- ({med.nombre_medicamento}) - {med.concentracion}, {med.dosis}, cada {med.frecuencia}, por {med.tiempo_tratamiento} días")
        write_line(f"Médico: {medico.first_name} {medico.last_name}")
    p.showPage()
    p.save()
    buffer.seek(0)
    return buffer


##### GENERAR ORDEN DE PROCEDIMIENTOS

def generar_pdf_orden_procedimiento(orden):
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    y = height - inch

    def write_line(text, font="Helvetica", size=10, offset=15):
        nonlocal y
        p.setFont(font, size)
        p.drawString(50, y, text)
        y -= offset
        if y < 100:
            p.showPage()
            y = height - inch

    paciente = orden.historia_clinica.paciente.usuario
    medico = orden.historia_clinica.medico.usuario

    write_line("ORDEN DE PROCEDIMIENTO", font="Helvetica-Bold", size=14, offset=25)
    write_line(f"Paciente: {paciente.first_name} {paciente.last_name}")
    write_line(f"Código: {orden.codigo}")
    write_line(f"Procedimiento: {orden.cups.codigo_cups} - {orden.cups.nombre_cups}")
    write_line(f"Descripción: {orden.descripcion}")
    write_line(f"Cantidad: {orden.cantidad}")
    write_line(f"Médico: {orden.historia_clinica.medico.usuario.first_name}, {orden.historia_clinica.medico.usuario.last_name}")
    p.showPage()
    p.save()
    buffer.seek(0)
    return buffer
