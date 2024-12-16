import tempfile
import os
from django import forms
from django.contrib import admin
from django.http import HttpResponse
from django.utils.html import mark_safe
from .models import Pesquisar, PesquisarV2
from .PlateDataAnalysis import PlateDataAnalysis
import csv

# Formulário comum para Pesquisar e PesquisarV2
class BasePesquisarForm(forms.ModelForm):
    image_upload = forms.ImageField(
        required=False,  # O campo de imagem continua sendo opcional
        label="Upload Imagem",
        widget=forms.FileInput(attrs={
            'accept': 'image/*',  # Permite tanto escolher uma imagem existente quanto tirar uma nova com a câmera
            'capture': 'camera',  # Permite que o usuário abra a câmera diretamente
        })
    )
    matricula = forms.CharField(
        required=False,  # Aqui definimos 'matricula' como não obrigatório
        label="Matrícula",
        max_length=15
    )

    class Meta:
        model = None  # Não definimos um modelo aqui diretamente
        fields = ['matricula', 'image_upload', 'usuario']

    def clean(self):
        cleaned_data = super().clean()
        image = cleaned_data.get("image_upload")
        matricula = cleaned_data.get("matricula")

        if not image and not matricula:
            raise forms.ValidationError("Por favor, insira a matrícula ou faça upload de uma imagem.")

        temp_file_path = None  # Inicializa a variável para o caminho do arquivo temporário

        if image:
            # Criar um arquivo temporário para salvar a imagem
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(image.name)[1]) as temp_file:
                try:
                    for chunk in image.chunks():
                        temp_file.write(chunk)  # Escreve o conteúdo da imagem no arquivo temporário

                    temp_file_path = temp_file.name  # O caminho do arquivo temporário criado

                    # Passar o caminho temporário para o seu método de processamento de imagem
                    plate_analyzer = PlateDataAnalysis()
                    processed_image = plate_analyzer.preprocess_image(temp_file_path)

                    # Realizar a leitura do texto da imagem
                    results = plate_analyzer.read_text_from_image(processed_image, decoder='beamsearch')
                    plate_data = plate_analyzer.filter_plates(results)

                    # Caso encontre dados válidos, atualiza o campo matrícula
                    if plate_data:
                        cleaned_data["matricula"] = plate_data["plate"]
                    else:
                        raise forms.ValidationError("Nenhuma matrícula válida foi detectada na imagem.")

                finally:
                    # Certifica-se de que o arquivo temporário será removido
                    if temp_file_path:
                        os.remove(temp_file_path)

        return cleaned_data


# Administração comum para Pesquisar e PesquisarV2
class BasePesquisarAdmin(admin.ModelAdmin):
    form = BasePesquisarForm
    list_display = ('usuario', 'matricula', 'mostrar_resultados', )  # 'usuario' como o primeiro campo na tabela
    search_fields = ('matricula',)  # Busca por matrícula
    actions = ['export_to_csv']  # Adiciona a opção de exportar para CSV
    list_filter = ['matricula']  # Filtro por matrícula
    list_per_page = 10  # Limita a exibição a 10 registros por página

    def mostrar_resultados(self, obj):
     """Exibe os resultados da API no Django Admin com seções organizadas."""
     resultados = obj.buscar_dados()
     if not resultados:
        return "Nenhum resultado encontrado."

    # Verifica se houve erro na consulta à API
     if "erro" in resultados[0]:
        return mark_safe(f"<span style='color: red;'>{resultados[0]['erro']}</span>")

    # Verifica se o modelo é Pesquisar ou PesquisarV2 para exibir campos diferentes
     if isinstance(obj, PesquisarV2):
        # Para o PesquisarV2, mostramos os campos específicos divididos em seções
        campos_dados_veiculo = [
            'matricula', 'marca', 'modelo', 'ano_fabricacao', 'cor', 'tipo_veiculo', 'categoria',
            'numero_motor', 'numero_quadro'
        ]
        campos_dados_propriedade = [
            'nome_proprietario', 'endereco_rua', 'endereco_numero', 'endereco_bairro', 'endereco_cidade',
            'endereco_provincia', 'endereco_codigo_postal', 'data_emissao', 'numero_registro', 'local_registro',
            'documento_identidade'
        ]

        lista_resultados = "<ul style='list-style-type: none;'>"

        for r in resultados:
            # Adiciona a seção "Dados do Veículo"
            lista_resultados += "<li><strong>Dados do Veículo:</strong></li>"
            for campo, valor in r.items():
                if campo in campos_dados_veiculo:
                    lista_resultados += f"<li><strong>{campo}:</strong> {valor}</li>"
  
            # Adiciona a seção "Dados de Título de Propriedade"
            lista_resultados += "<li style='margin-top: 20px;'><strong>Dados de Título de Propriedade:</strong></li>"
            for campo, valor in r.items():
                if campo in campos_dados_propriedade:
                    lista_resultados += f"<li><strong>{campo}:</strong> {valor}</li>"
            
            lista_resultados += "<li><hr></li>"

        lista_resultados += "</ul>"

     else:
        # Para o Pesquisar, mostramos os campos correspondentes sem divisão em seções
        campos_desejados = [
            'matricula', 'modelo', 'marca', 'n_quadro', 'n_motor', 'ano', 
            'data_criacao_inspecao', 'data_proxima_inspecao','n_ficha'
        ]

        lista_resultados = "<ul style='list-style-type: none;'>"
        for r in resultados:
            for campo, valor in r.items():
                if campo in campos_desejados:
                    lista_resultados += f"<li><strong>{campo}:</strong> {valor}</li>"
            lista_resultados += "<li><hr></li>"
        lista_resultados += "</ul>"

     return mark_safe(lista_resultados)


    mostrar_resultados.short_description = "Resultados da Busca"

    def save_model(self, request, obj, form, change):
        """Força o campo 'usuario' a ser preenchido automaticamente com o usuário logado ao salvar."""
        if not request.user.is_superuser:
            obj.usuario = request.user
        super().save_model(request, obj, form, change)

    def get_form(self, request, obj=None, **kwargs):
        """Esconde o campo 'usuario' no formulário para usuários não superadministradores."""
        form = super().get_form(request, obj, **kwargs)
        if not request.user.is_superuser:
            if 'usuario' in form.base_fields:
                form.base_fields['usuario'].disabled = True
                form.base_fields['usuario'].initial = request.user
        return form

    def get_queryset(self, request):
        """Restringe a lista de ocorrências a apenas as do usuário logado (se não for superusuário)."""
        queryset = super().get_queryset(request)
        if not request.user.is_superuser:
            queryset = queryset.filter(usuario=request.user)
        return queryset

    def export_to_csv(self, request, queryset):
        """Exporta os resultados para um arquivo CSV."""
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="pesquisas.csv"'
        writer = csv.writer(response)

        # Cabeçalhos do CSV
        writer.writerow(['Usuário', 'Matrícula', 'Resultados'])  # 'Usuário' como o primeiro cabeçalho

        # Escreve os dados de cada pesquisa
        for pesquisa in queryset:
            resultados = pesquisa.buscar_dados()
            if "erro" in resultados[0]:
                dados_formatados = resultados[0]["erro"]
            else:
                dados_formatados = "; ".join(
                    [f"{k}: {v}" for r in resultados for k, v in r.items() if k in campos_desejados]
                )
            writer.writerow([pesquisa.usuario, pesquisa.matricula, dados_formatados])  # 'usuario' primeiro no CSV

        return response

    export_to_csv.short_description = "Exportar para CSV"


# Registra os modelos no Django Admin
@admin.register(Pesquisar)
class PesquisarAdmin(BasePesquisarAdmin):
    form = BasePesquisarForm  # Usa o formulário base para Pesquisar


@admin.register(PesquisarV2)
class PesquisarV2Admin(BasePesquisarAdmin):
    form = BasePesquisarForm  # Usa o mesmo formulário base para PesquisarV2
