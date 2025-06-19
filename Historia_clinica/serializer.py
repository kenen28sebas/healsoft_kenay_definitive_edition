from django.utils import timezone
from rest_framework import serializers
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import ValidationError

#
from datetime import date


from Usuarios.serializer import PacienteSerializador
from Usuarios.models import Medico, Paciente
from .models import *

## 
from django.db.models import Max

###### 
from .utils import generar_pdf_historia_clinica
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage


class PacienteSerializer(serializers.ModelSerializer):
    nombre_completo = serializers.SerializerMethodField()
    
    class Meta:
        model = Paciente
        fields = [
            'id',
            'nombre_completo',
            'grupo_sanguineo',
            'estrato',
            'regimen'
        ]

    def get_nombre_completo(self, obj):
        return f"{obj.usuario.first_name} {obj.usuario.last_name}".strip()

class MedicoSerializer(serializers.ModelSerializer):
    nombre_completo = serializers.SerializerMethodField()
    
    class Meta:
        model = Medico
        fields = [
            'id',
            'nombre_completo',
            'especialidad'
        ]

    def get_nombre_completo(self, obj):
        return f"{obj.usuario.first_name} {obj.usuario.last_name}".strip() 


class Cie10Serializer(serializers.ModelSerializer):

    class Meta:
        model = Cie10
        fields = [
            'id',
            'codigo_cie10',
            'nombre_cie10',
            'descripcion_cie10'
        ]




class CupsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Cups
        fields = [
            'id',
            'codigo_cups',
            'nombre_cups',
            'descripcion_cups'
        ]

class AnamnesisSerializer(serializers.ModelSerializer):

    class Meta:
        model = Anamnesis
        fields = [
            'id',
            'motivo_consulta',
            'sintomas',
            'examen_fisico',
            'enfermedades_base',
            'habitos',
            'antecedentes_medicos',
            'descripcion_antecedente',
        ]


class SignosVitalesSerializer(serializers.ModelSerializer):
    interpretacion_imc = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = SignosVitales
        fields = [
            'id',
            'frecuencia_cardiaca',
            'presion_arterial',
            'frecuencia_respiratoria',
            'temperatura_corporal',
            'saturacion',
            'peso',
            'talla',
            'imc',  # ya se guarda en la BD
            'interpretacion_imc',
        ]
        read_only_fields = ['imc']  

    def validate(self, data):
        peso = data.get('peso')
        talla = data.get('talla')

        if peso is None or talla is None:
            raise serializers.ValidationError("Se requiere peso y talla para calcular el IMC.")
        if talla == 0:
            raise serializers.ValidationError("La talla no puede ser cero para calcular el IMC.")
        return data


    def create(self, validated_data):
        peso = validated_data['peso']
        talla = validated_data['talla']
        validated_data['imc'] = round(peso / (talla ** 2), 2)
        return super().create(validated_data)


    def get_interpretacion_imc(self, obj):
        if obj.imc is None:
            return "IMC no disponible"
        
        imc = obj.imc
        if imc < 18.5:
            return "Bajo peso"
        elif 18.5 <= imc <= 24.9:
            return "Peso normal"
        elif 25.0 <= imc < 29.9:
            return "Sobrepeso"
        elif 30.0 <= imc < 34.9:
            return "Obesidad grado I"
        elif 35.0 <= imc < 39.9:
            return "Obesidad grado II"
        else:
            return "Obesidad grado III"




class ParaclinicosSerializer(serializers.ModelSerializer):

    class Meta:
        model = Paraclinicos
        fields = [
            'id',
            'resultados',
            'analisis'
        ]

class DiagnosticoSerializer(serializers.ModelSerializer):
    cie10_detalle = Cie10Serializer(source='cie10', read_only=True)
    cie10 = serializers.SlugRelatedField(
        queryset=Cie10.objects.all(),
        slug_field='codigo_cie10'
    )

    class Meta:
        model = Diagnostico
        fields = [
            'id',
            'cie10_detalle',
            'cie10',
            'tipo_diagnostico',
            'observaciones'
        ]


class OrdenDeProcedimientosSerializer(serializers.ModelSerializer):
    codigo = serializers.IntegerField(read_only=True)
    cups_detalle = CupsSerializer(source='cups', read_only=True) 
    cups = serializers.SlugRelatedField(
        slug_field='codigo_cups',
        queryset=Cups.objects.all(),
    )
    historia_clinica = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = OrdenDeProcedimientos
        fields = [
            'id',
            'codigo',
            'historia_clinica',
            'cups',
            'cups_detalle',
            'descripcion',
            'cantidad',
            'estado',
            'observacion',

        ]


    def create(self, validated_data):
        return OrdenDeProcedimientos.objects.create(**validated_data)



class MedicamentoSerializer(serializers.ModelSerializer):

    class Meta:
        model = Medicamento
        fields = [
            'id',
            'nombre_medicamento',
            'concentracion',
            'forma_farmaceutica',
            'dosis',
            'via_administracion',
            'frecuencia',
            'tiempo_tratamiento',
            'cantidad',
            'cantidad_letras',
            'posologia',
            'recomendaciones'
        ]



class FormulaMedicaSerializer(serializers.ModelSerializer):
    medicamentos = MedicamentoSerializer(many=True)
    medico = serializers.PrimaryKeyRelatedField(queryset=Medico.objects.all())
    medico_detalle = MedicoSerializer(source='medico', read_only=True)
    diagnostico = serializers.CharField()
    historia_clinica = serializers.PrimaryKeyRelatedField(
    queryset=HistoriaClinica.objects.all(),
    required=False  
)
    fecha_prescripcion = serializers.DateTimeField(
        read_only=True,
        format="%d/%m/%Y %I:%M:%S %p"
    )

    class Meta:
        model = FormulaMedica
        fields = [
            'id',
            'medico',
            'medico_detalle',
            'diagnostico',
            'historia_clinica', 
            'fecha_prescripcion',
            'medicamentos'
        ]



    def create(self, validated_data):
        medicamentos_data = validated_data.pop('medicamentos', [])
        diagnostico_obj = validated_data.pop('diagnostico')

        # Creando la fórmula médica
        formula = FormulaMedica.objects.create(diagnostico=diagnostico_obj, **validated_data)

        # Crear los medicamentos relacionados
        for medicamento_data in medicamentos_data:
            Medicamento.objects.create(formula_medica=formula, **medicamento_data)

        return formula



class EvolucionSerializer(serializers.ModelSerializer):
    diagnostico = serializers.CharField()
    diagnostico_detalle = DiagnosticoSerializer(source='diagnostico', read_only=True)
    historia_clinica = serializers.PrimaryKeyRelatedField(
    queryset=HistoriaClinica.objects.all(),
    required=False 
)
    medico = serializers.PrimaryKeyRelatedField(queryset=Medico.objects.all())
    fecha_actual = serializers.DateField(read_only=True, format="%d/%m/%Y")

    class Meta:
        model = Evolucion
        fields = [
            'id',
            'historia_clinica',
            'fecha_actual',
            'estado_paciente',
            'diagnostico',
            'diagnostico_detalle',
            'plan_de_manejo',
            'evolucion',
            'recomendaciones',
            'interconsultas',
            'plan_de_seguimiento',
            'medico'
        ]

    def create(self, validated_data):
        cie10_obj = validated_data.pop('diagnostico')  

        # Buscar el último diagnóstico existente con ese CIE10
        diagnostico = Diagnostico.objects.filter(cie10=cie10_obj).order_by('-id').first()
        if not diagnostico:
            raise serializers.ValidationError(
                f"No existe un diagnóstico registrado con el código CIE10 '{cie10_obj.codigo_cie10}'. "
                f"Debe haber sido creado previamente en la historia clínica."
            )

        return Evolucion.objects.create(diagnostico=diagnostico, **validated_data)



class HistoriaClinicaSerializer(serializers.ModelSerializer):
    paciente = serializers.PrimaryKeyRelatedField(queryset=Paciente.objects.all())
    paciente_detalle = PacienteSerializer(source='paciente', read_only=True)
    medico = serializers.PrimaryKeyRelatedField(queryset=Medico.objects.all())
    medico_detalle = MedicoSerializer(source='medico', read_only=True)

    anamnesis = AnamnesisSerializer()
    diagnostico = DiagnosticoSerializer(many=True)
    signos_vitales = SignosVitalesSerializer()
    paraclinicos = ParaclinicosSerializer()
    orden_de_procedimientos = OrdenDeProcedimientosSerializer(many=True, required=False)
    formula_medica = FormulaMedicaSerializer(many=True, required=False)
    evolucion = EvolucionSerializer(many=True, required=False)

    class Meta:
        model = HistoriaClinica
        fields = [
            'id',
            'paciente',
            'paciente_detalle',
            'medico',
            'medico_detalle',
            'anamnesis',
            'diagnostico',
            'signos_vitales',
            'paraclinicos',
            'orden_de_procedimientos',
            'formula_medica',
            'evolucion',
        
        
            ]
    def create(self, validated_data):
        diagnosticos_data = validated_data.pop('diagnostico')
        anamnesis_data = validated_data.pop('anamnesis')
        signos_vitales_data = validated_data.pop('signos_vitales')
        paraclinicos_data = validated_data.pop('paraclinicos')
        ordenes_data = validated_data.pop('orden_de_procedimientos', [])
        formulas_data = validated_data.pop('formula_medica', [])
        evoluciones_data = validated_data.pop('evolucion', [])

        # Crear submodelos OneToOne
        anamnesis = Anamnesis.objects.create(**anamnesis_data)
        signos = SignosVitales.objects.create(**signos_vitales_data)
        paraclinicos = Paraclinicos.objects.create(**paraclinicos_data)

        # Crear historia clínica principal
        historia = HistoriaClinica.objects.create(
            anamnesis=anamnesis,
            signos_vitales=signos,
            paraclinicos=paraclinicos,
            **validated_data
        )

        # Diccionario para acceder fácilmente a los diagnósticos creados
        diagnosticos_creados = {}

        # Diagnósticos ManyToMany (uno nuevo por cada entrada del JSON)
        for diag_data in diagnosticos_data:
            cie10_obj = diag_data.pop('cie10')
            cie10_codigo = cie10_obj.codigo_cie10.strip().upper()

            # Crear siempre un nuevo diagnóstico para este folio
            diagnostico = Diagnostico.objects.create(cie10=cie10_obj, **diag_data)

            historia.diagnostico.add(diagnostico)
            diagnosticos_creados[cie10_codigo] = diagnostico  # Guardar para fórmula/evolución

        # Órdenes de procedimiento
        for orden_data in ordenes_data:
            cups_obj = orden_data.pop('cups')
            OrdenDeProcedimientos.objects.create(historia_clinica=historia, cups=cups_obj, **orden_data)

        # Fórmulas médicas
        for formula_data in formulas_data:
            medicamentos_data = formula_data.pop('medicamentos', [])
            diagnostico_input = formula_data.pop('diagnostico')
            formula_data.pop('medico', None)

            # Obtener código CIE10 
            if isinstance(diagnostico_input, dict):
                cie10_codigo = diagnostico_input.get('cie10')
            elif isinstance(diagnostico_input, str):
                cie10_codigo = diagnostico_input
            elif isinstance(diagnostico_input, Diagnostico):
                cie10_codigo = diagnostico_input.cie10.codigo_cie10
            else:
                raise serializers.ValidationError("Formato de diagnóstico no válido en fórmula médica.")

            cie10_codigo = str(cie10_codigo).strip().upper()
            diagnostico = diagnosticos_creados.get(cie10_codigo)

            if not diagnostico:
                raise serializers.ValidationError(f"No se encontró un diagnóstico previo con código '{cie10_codigo}'.")

            formula = FormulaMedica.objects.create(
                historia_clinica=historia,
                diagnostico=diagnostico,
                medico=validated_data['medico'],
                **formula_data
            )

            for medicamento_data in medicamentos_data:
                Medicamento.objects.create(formula_medica=formula, **medicamento_data)

        # Evoluciones 
        for evolucion_data in evoluciones_data:
            diagnostico_input = evolucion_data.pop('diagnostico')

            if isinstance(diagnostico_input, dict):
                cie10_codigo = diagnostico_input.get('cie10')
            elif isinstance(diagnostico_input, str):
                cie10_codigo = diagnostico_input
            elif isinstance(diagnostico_input, Diagnostico):
                cie10_codigo = diagnostico_input.cie10.codigo_cie10
            else:
                raise serializers.ValidationError("Formato de diagnóstico no válido en evolución.")

            cie10_codigo = str(cie10_codigo).strip().upper()
            diagnostico = diagnosticos_creados.get(cie10_codigo)

            if not diagnostico:
                raise serializers.ValidationError(f"No se encontró un diagnóstico previo con código '{cie10_codigo}' para evolución.")

            evolucion_data_clean = {k: v for k, v in evolucion_data.items() if k != 'medico'}

            Evolucion.objects.create(
                historia_clinica=historia,
                diagnostico=diagnostico,
                medico=validated_data['medico'],
                **evolucion_data_clean
            )

        return historia

    