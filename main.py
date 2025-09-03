import streamlit as st
from google import genai
import os
import uuid
from datetime import datetime
from pymongo import MongoClient

# Configuração da página
st.set_page_config(page_title="Gerador de Blog Posts Agrícolas", page_icon="🌱", layout="wide")

# Título do aplicativo
st.title("🌱 Gerador de Blog Posts Agrícolas")
st.markdown("Crie conteúdos especializados para o agronegócio seguindo a estrutura profissional")

# Configuração do Gemini API
gemini_api_key = st.secrets.get("GEMINI_API_KEY", os.getenv("GEMINI_API_KEY"))
if not gemini_api_key:
    gemini_api_key = st.text_input("Digite sua API Key do Gemini:", type="password")

if gemini_api_key:
    client = genai.Client(api_key=gemini_api_key)
    
    # Conexão com MongoDB (opcional)
    try:
        mongodb_uri = st.secrets.get("MONGODB_URI", os.getenv("MONGODB_URI"))
        if mongodb_uri:
            client_mongo = MongoClient(mongodb_uri)
            db = client_mongo['blog_posts_agricolas']
            collection = db['posts_gerados']
            mongo_connected = True
        else:
            mongo_connected = False
    except:
        mongo_connected = False
        st.warning("Conexão com MongoDB não configurada. Os posts não serão salvos.")

    # Função para salvar no MongoDB
    def salvar_no_mongo(titulo, cultura, editoria, mes_publicacao, objetivo_post, url, texto_gerado):
        if mongo_connected:
            documento = {
                "id": str(uuid.uuid4()),
                "titulo": titulo,
                "cultura": cultura,
                "editoria": editoria,
                "mes_publicacao": mes_publicacao,
                "objetivo_post": objetivo_post,
                "url": url,
                "texto_gerado": texto_gerado,
                "data_criacao": datetime.now()
            }
            collection.insert_one(documento)
            return True
        return False

    # Regras extraídas do documento exemplo
    regras_replicacao = '''
**REGRAS DE REPLICAÇÃO EXTRAÍDAS DO DOCUMENTO EXEMPLO:**

**1. ESTRUTURA DO DOCUMENTO:**
- Título principal em formato de chamada para ação
- Subtítulo/Chapéu com resumo executivo (1-2 linhas)
- Introdução: Contextualiza o problema atual e seu impacto
- Seção de Problema: Detalha pragas específicas, comportamentos e danos causados
- Seção de Solução Genérica: Explica a estratégia geral (ex: tratamento de sementes)
- Seção de Solução Específica: Apresenta o produto como resposta aos desafios
- Conclusão: Reforça compromisso da marca e chama para ação

**2. LINGUAGEM E TOM:**
- Linguagem técnica e profissional, mas acessível ao produtor rural
- Tom autoritativo e especializado
- Uso de terminologia do agronegócio ("estabelecimento do estande", "manejo integrado")
- Persuasão focada em benefícios e solução de problemas
- Mix de frases curtas de impacto com parágrafos explicativos

**3. ELEMENTOS TÉCNICOS OBRIGATÓRIOS:**
- Nomes científicos das pragas entre parênteses
- Citação de fontes (ex: "Fonte: Embrapa")
- Destaque em negrito para nome do produto e termos técnicos-chave
- Descrição detalhada de danos específicos
- Explicação de benefícios econômicos e estratégicos

**4. FORMATAÇÃO:**
- Título principal
- Subtítulo em formato de resumo
- Parágrafos bem estruturados com transições suaves
- Seções claramente demarcadas (sem subtítulos numerados)
- Destaques em negrito para produtos e termos importantes

**5. PERSUASÃO E ARGUMENTAÇÃO:**
- Sempre vincular problema → solução
- Destacar valor econômico e retorno sobre investimento
- Usar dados concretos sobre danos e perdas
- Apresentar produto como consequência lógica da argumentação
- Focar em proteção e potencial máximo da lavoura
'''

    # Template do prompt baseado nas regras
    prompt_template = '''
**INSTRUÇÕES PARA CRIAÇÃO DE BLOG POST AGRÍCOLA:**

Você é um redator técnico especializado em agronegócio. Crie um artigo de blog seguindo ESTRITAMENTE as regras abaixo:

{regras_replicacao}

**DADOS PARA INCLUSÃO NO POST:**

**Informações Básicas:**
- Título: {titulo_blog}
- Cultura: {cultura}
- Editoria: {editoria}
- Objetivo: {objetivo_post}

**Contexto e Problema:**
- Problema Principal: {problema_principal}
- Pragas/Alvo: {pragas_alvo}
- Danos Causados: {danos_causados}

**Soluções:**
- Solução Genérica: {solucao_generica}
- Produto Específico: {nome_produto}
- Princípio Ativo: {principio_ativo}
- Benefícios: {beneficios_produto}
- Espectro de Ação: {espectro_acao}

**Marca:**
- Empresa: {nome_empresa}
- Central de Conteúdos: {nome_central}

**TAREFA:**
Gere um artigo completo e pronto para publicação, seguindo TODAS as regras de estrutura, linguagem, formatação e persuasão listadas acima. O texto deve ser técnico, persuasivo e fiel ao estilo do documento exemplo.
'''

    # Interface do usuário
    with st.sidebar:
        st.header("📋 Configurações do Post")
        
        titulo_blog = st.text_input("Título do Blog:", "Proteja sua soja de nematoides e pragas de solo")
        cultura = st.text_input("Cultura:", "Soja")
        editoria = st.text_input("Editoria:", "Manejo e Proteção")
        mes_publicacao = st.text_input("Mês de Publicação:", "08/2025")
        objetivo_post = st.text_area("Objetivo do Post:", "Explicar a importância do manejo de nematoides e apresentar soluções via tratamento de sementes")
        url = st.text_input("URL:", "/manejo-e-protecao/proteja-sua-soja-de-nematoides")
        
        st.divider()
        
        problema_principal = st.text_area("Problema Principal/Contexto:", "Solos compactados e com palhada de milho têm favorecido a explosão populacional de nematoides, preocupando produtores para a próxima safra")
        pragas_alvo = st.text_area("Pragas/Alvo Principal:", "Nematoide das galhas (Meloidogyne incognita), Nematoide de cisto (Heterodera glycines)")
        danos_causados = st.text_area("Danos Causados:", "Formação de galhas nas raízes que impedem a absorção de água e nutrientes, paralisando o desenvolvimento da planta e causando amarelecimento")
        solucao_generica = st.text_area("Solução Genérica:", "Adoção de um manejo integrado com genética resistente, rotação de culturas e tratamento de sementes específico")
        
        st.divider()
        
        nome_produto = st.text_input("Nome do Produto:", "NEMATEC®")
        principio_ativo = st.text_input("Princípio Ativo/Diferencial:", "Abamectina, com tripla ação de contato, sistêmica e promotora de crescimento radicular")
        beneficios_produto = st.text_area("Benefícios do Produto:", "Proteção prolongada no sulco de plantio, controle dos estágios juvenis dos nematoides, estímulo ao desenvolvimento de raízes laterais")
        espectro_acao = st.text_area("Espectro de Ação:", "Meloidogyne incognita, Heterodera glycines, Pratylenchulus brachyurus")
        nome_empresa = st.text_input("Nome da Empresa/Marca:", "Syngenta")
        nome_central = st.text_input("Nome da Central de Conteúdos:", "Portal Agro")
        
        st.divider()
        
        # Opção para visualizar regras
        if st.checkbox("📋 Visualizar Regras de Replicação"):
            st.info(regras_replicacao)
        
        gerar_post = st.button("🔄 Gerar Blog Post", type="primary", use_container_width=True)

    # Área principal
    if gerar_post and gemini_api_key:
        with st.spinner("Gerando seu blog post... Isso pode levar alguns segundos"):
            try:
                # Construir o prompt final
                prompt_final = prompt_template.format(
                    regras_replicacao=regras_replicacao,
                    titulo_blog=titulo_blog,
                    cultura=cultura,
                    editoria=editoria,
                    objetivo_post=objetivo_post,
                    problema_principal=problema_principal,
                    pragas_alvo=pragas_alvo,
                    danos_causados=danos_causados,
                    solucao_generica=solucao_generica,
                    nome_produto=nome_produto,
                    principio_ativo=principio_ativo,
                    beneficios_produto=beneficios_produto,
                    espectro_acao=espectro_acao,
                    nome_empresa=nome_empresa,
                    nome_central=nome_central
                )
                
                # Gerar conteúdo com Gemini
                response = client.models.generate_content(
                    model="gemini-1.5-flash",
                    contents=prompt_final
                )
                
                texto_gerado = response.text
                
                # Exibir resultados
                st.success("✅ Blog post gerado com sucesso!")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("📊 Metadados do Post")
                    st.info(f"**Título:** {titulo_blog}")
                    st.info(f"**Cultura:** {cultura}")
                    st.info(f"**Editoria:** {editoria}")
                    st.info(f"**Mês de Publicação:** {mes_publicacao}")
                    st.info(f"**URL:** {url}")
                    
                    # Botão para copiar texto
                    st.download_button(
                        label="📥 Download do Texto",
                        data=texto_gerado,
                        file_name=f"blog_post_{titulo_blog.lower().replace(' ', '_')}.txt",
                        mime="text/plain"
                    )
                
                with col2:
                    st.subheader("🌐 Informações do Produto")
                    st.success(f"**Produto:** {nome_produto}")
                    st.success(f"**Princípio Ativo:** {principio_ativo}")
                    st.success(f"**Empresa:** {nome_empresa}")
                
                st.divider()
                
                st.subheader("📝 Conteúdo Gerado")
                st.markdown(texto_gerado)
                
                # Salvar no MongoDB se conectado
                if mongo_connected:
                    if salvar_no_mongo(titulo_blog, cultura, editoria, mes_publicacao, objetivo_post, url, texto_gerado):
                        st.sidebar.success("✅ Post salvo no banco de dados!")
                
            except Exception as e:
                st.error(f"Erro ao gerar o conteúdo: {str(e)}")
    
    elif not gemini_api_key:
        st.warning("⚠️ Por favor, insira uma API Key válida do Gemini para gerar conteúdos.")

else:
    st.info("🔑 Para começar, insira sua API Key do Gemini na barra lateral.")

# Rodapé
st.divider()
st.caption("🌱 Gerador de Conteúdo Agrícola - Desenvolvido para produtores e empresas do agronegócio")
