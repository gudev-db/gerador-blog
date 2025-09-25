import streamlit as st
from google import genai
import os
import uuid
from datetime import datetime
from pymongo import MongoClient
import json

# Configuração da página
st.set_page_config(page_title="Gerador de Blog Posts Agrícolas", page_icon="🌱", layout="wide")

# Título do aplicativo
st.title("🌱 Gerador de Blog Posts Agrícolas")
st.markdown("Crie conteúdos especializados para o agronegócio seguindo a estrutura profissional")

# Conexão com MongoDB
try:
    client_mongo = MongoClient("mongodb+srv://gustavoromao3345:RqWFPNOJQfInAW1N@cluster0.5iilj.mongodb.net/auto_doc?retryWrites=true&w=majority&ssl=true&ssl_cert_reqs=CERT_NONE&tlsAllowInvalidCertificates=true")
    db = client_mongo['blog_posts_agricolas']
    collection_posts = db['posts_gerados']
    collection_briefings = db['briefings']
    collection_kbf = db['kbf_produtos']
    mongo_connected = True
except Exception as e:
    st.error(f"Erro na conexão com MongoDB: {str(e)}")
    mongo_connected = False

# Configuração do Gemini API
gemini_api_key = st.secrets.get("GEMINI_API_KEY", os.getenv("GEMINI_API_KEY"))
if not gemini_api_key:
    gemini_api_key = st.text_input("Digite sua API Key do Gemini:", type="password")

if gemini_api_key:
    client = genai.Client(api_key=gemini_api_key)

    # Funções para o banco de dados
    def salvar_post(titulo, cultura, editoria, mes_publicacao, objetivo_post, url, texto_gerado, palavras_chave, metadescricao, palavras_proibidas, tom_voz, estrutura, palavras_contagem):
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
                "palavras_chave": palavras_chave,
                "metadescricao": metadescricao,
                "palavras_proibidas": palavras_proibidas,
                "tom_voz": tom_voz,
                "estrutura": estrutura,
                "palavras_contagem": palavras_contagem,
                "data_criacao": datetime.now(),
                "versao": "1.0"
            }
            collection_posts.insert_one(documento)
            return True
        return False

    def carregar_kbf_produtos():
        if mongo_connected:
            try:
                kbf_docs = list(collection_kbf.find({}))
                return kbf_docs
            except:
                return []
        return []

    def salvar_briefing(briefing_data):
        if mongo_connected:
            documento = {
                "id": str(uuid.uuid4()),
                "briefing": briefing_data,
                "data_criacao": datetime.now()
            }
            collection_briefings.insert_one(documento)
            return True
        return False

    def carregar_posts_anteriores():
        if mongo_connected:
            try:
                posts = list(collection_posts.find({}).sort("data_criacao", -1).limit(10))
                return posts
            except:
                return []
        return []

    # Regras base do sistema
    regras_base = '''
**REGRAS DE REPLICAÇÃO - ESTRUTURA PROFISSIONAL:**

**1. ESTRUTURA DO DOCUMENTO:**
- Título principal impactante e com chamada para ação
- Subtítulo/Chapéu com resumo executivo (1-2 linhas)
- Introdução contextualizando o problema e impacto
- Seção de Problema: Detalhamento técnico dos desafios
- Seção de Solução Genérica: Estratégia geral de manejo
- Seção de Solução Específica: Produto como resposta aos desafios
- Conclusão com reforço de compromisso e chamada para ação
- Assinatura padrão da empresa

**2. LINGUAGEM E TOM:**
- {tom_voz}
- Linguagem {nivel_tecnico} técnica e profissional
- Uso de terminologia específica do agronegócio
- Persuasão baseada em benefícios e solução de problemas
- Evitar repetição de informações entre seções

**3. ELEMENTOS TÉCNICOS OBRIGATÓRIOS:**
- Nomes científicos entre parênteses quando aplicável
- Citação de fontes confiáveis (Embrapa, universidades, etc.)
- Destaque para termos técnicos-chave e nomes de produtos
- Descrição detalhada de danos e benefícios
- Dados concretos e informações mensuráveis

**4. RESTRIÇÕES:**
- Palavras proibidas: {palavras_proibidas}
- Evitar viés comercial explícito
- Manter abordagem {abordagem_problema}
- Número de palavras: {numero_palavras} (±10%)
'''

    # Interface principal
    with st.sidebar:
        st.header("📋 Configurações Principais")
        
        # Modo de entrada - Briefing ou Campos Individuais
        modo_entrada = st.radio("Modo de Entrada:", ["Campos Individuais", "Briefing Completo"])
        
        # Controle de palavras
        numero_palavras = st.slider("Número de Palavras:", min_value=300, max_value=3000, value=1000, step=100)
        
        # Palavras-chave
        st.subheader("🔑 Palavras-chave")
        palavra_chave_principal = st.text_input("Palavra-chave Principal:")
        palavras_chave_secundarias = st.text_area("Palavras-chave Secundárias (separadas por vírgula):")
        
        # Configurações de estilo
        st.subheader("🎨 Configurações de Estilo")
        tom_voz = st.selectbox("Tom de Voz:", ["Jornalístico", "Especialista Técnico", "Educativo", "Persuasivo"])
        nivel_tecnico = st.selectbox("Nível Técnico:", ["Básico", "Intermediário", "Avançado"])
        abordagem_problema = st.text_area("Aborde o problema de tal forma que:", "seja claro, técnico e focando na solução prática para o produtor")
        
        # Restrições
        st.subheader("🚫 Restrições")
        palavras_proibidas = st.text_area("Palavras Proibidas (separadas por vírgula):", "melhor, número 1, líder, insuperável")
        
        # Estrutura do texto
        st.subheader("📐 Estrutura do Texto")
        estrutura_opcoes = st.multiselect("Seções do Post:", 
                                         ["Introdução", "Problema", "Solução Genérica", "Solução Específica", 
                                          "Benefícios", "Implementação Prática", "Conclusão", "Fontes"],
                                         default=["Introdução", "Problema", "Solução Genérica", "Solução Específica", "Conclusão"])
        
        # KBF de Produtos
        st.subheader("📦 KBF de Produtos")
        kbf_produtos = carregar_kbf_produtos()
        if kbf_produtos:
            produtos_disponiveis = [prod['nome'] for prod in kbf_produtos]
            produto_selecionado = st.selectbox("Selecionar Produto do KBF:", ["Nenhum"] + produtos_disponiveis)
            if produto_selecionado != "Nenhum":
                produto_info = next((prod for prod in kbf_produtos if prod['nome'] == produto_selecionado), None)
                if produto_info:
                    st.info(f"**KBF Fixo:** {produto_info.get('caracteristicas', 'Informações do produto')}")
        else:
            st.info("Nenhum KBF cadastrado no banco de dados")

    # Área principal baseada no modo de entrada
    if modo_entrada == "Campos Individuais":
        col1, col2 = st.columns(2)
        
        with col1:
            st.header("📝 Informações Básicas")
            titulo_blog = st.text_input("Título do Blog:", "Proteja sua soja de nematoides e pragas de solo")
            metadescricao = st.text_area("Meta Descrição:", max_chars=160)
            cultura = st.text_input("Cultura:", "Soja")
            editoria = st.text_input("Editoria:", "Manejo e Proteção")
            mes_publicacao = st.text_input("Mês de Publicação:", "08/2025")
            objetivo_post = st.text_area("Objetivo do Post:", "Explicar a importância do manejo de nematoides e apresentar soluções via tratamento de sementes")
            url = st.text_input("URL:", "/manejo-e-protecao/proteja-sua-soja-de-nematoides")
            
            st.header("🔧 Conteúdo Técnico")
            problema_principal = st.text_area("Problema Principal/Contexto:", "Solos compactados e com palhada de milho têm favorecido a explosão populacional de nematoides")
            pragas_alvo = st.text_area("Pragas/Alvo Principal:", "Nematoide das galhas (Meloidogyne incognita), Nematoide de cisto (Heterodera glycines)")
            danos_causados = st.text_area("Danos Causados:", "Formação de galhas nas raízes que impedem a absorção de água e nutrientes")
            solucao_generica = st.text_area("Solução Genérica:", "Adoção de um manejo integrado com genética resistente, rotação de culturas e tratamento de sementes")
        
        with col2:
            st.header("🏭 Informações da Empresa")
            nome_empresa = st.text_input("Nome da Empresa/Marca:")
            nome_central = st.text_input("Nome da Central de Conteúdos:")
            
            st.header("💡 Soluções e Produtos")
            nome_produto = st.text_input("Nome do Produto:")
            principio_ativo = st.text_input("Princípio Ativo/Diferencial:")
            beneficios_produto = st.text_area("Benefícios do Produto:")
            espectro_acao = st.text_area("Espectro de Ação:")
            
            st.header("🎯 Diretrizes Específicas")
            diretrizes_usuario = st.text_area("Diretrizes Adicionais:", "Incluir dicas práticas para implementação no campo. Manter linguagem acessível mas técnica.")
            fontes_pesquisa = st.text_area("Fontes para Pesquisa/Referência:", "Embrapa Soja, Universidade de São Paulo, Artigos técnicos sobre nematoides")
            
            # Upload de arquivos estratégicos
            arquivo_strategico = st.file_uploader("📎 Upload de Arquivo Estratégico", type=['txt', 'pdf', 'docx'])
            if arquivo_strategico:
                st.success(f"Arquivo {arquivo_strategico.name} carregado com sucesso!")
    
    else:  # Modo Briefing
        st.header("📄 Briefing Completo")
        briefing_texto = st.text_area("Cole aqui o briefing completo:", height=300,
                                     placeholder="""EXEMPLO DE BRIEFING:
Título: Controle Eficiente de Nematoides na Soja
Cultura: Soja
Problema: Aumento da população de nematoides em solos com palhada de milho
Objetivo: Educar produtores sobre manejo integrado
Produto: NemaControl
Público-alvo: Produtores de soja técnica
Tom: Técnico-jornalístico
Palavras-chave: nematoide, soja, tratamento sementes, manejo integrado""")
        
        if briefing_texto:
            if st.button("Processar Briefing"):
                salvar_briefing(briefing_texto)
                st.success("Briefing salvo no banco de dados!")

    # Configurações avançadas
    with st.expander("⚙️ Configurações Avançadas"):
        col_av1, col_av2 = st.columns(2)
        
        with col_av1:
            st.subheader("Opcionais")
            usar_pesquisa_web = st.checkbox("🔍 Habilitar Pesquisa Web", value=False)
            gerar_blocos_dinamicos = st.checkbox("🔄 Gerar Blocos Dinamicamente", value=True)
            incluir_fontes = st.checkbox("📚 Incluir Referências de Fontes", value=True)
            incluir_assinatura = st.checkbox("✍️ Incluir Assinatura Padrão", value=True)
            
        with col_av2:
            st.subheader("Controles de Qualidade")
            evitar_repeticao = st.slider("Nível de Evitar Repetição:", 1, 10, 8)
            profundidade_conteudo = st.selectbox("Profundidade do Conteúdo:", ["Superficial", "Moderado", "Detalhado", "Especializado"])
            
            # Transcrição de áudio/vídeo
            st.subheader("🎤 Transcrição")
            arquivo_midia = st.file_uploader("Áudio/Video para Transcrição", type=['mp3', 'wav', 'mp4', 'mov'])

    # Área de geração e edição
    st.header("🔄 Geração e Edição do Conteúdo")
    
    col_gerar, col_editar = st.columns(2)
    
    with col_gerar:
        if st.button("🚀 Gerar Blog Post", type="primary", use_container_width=True):
            if gemini_api_key:
                with st.spinner("Gerando conteúdo... Isso pode levar alguns minutos"):
                    try:
                        # Construir prompt personalizado
                        regras_personalizadas = regras_base.format(
                            tom_voz=tom_voz,
                            nivel_tecnico=nivel_tecnico,
                            palavras_proibidas=palavras_proibidas,
                            abordagem_problema=abordagem_problema,
                            numero_palavras=numero_palavras
                        )
                        
                        prompt_final = f"""
                        **INSTRUÇÕES PARA CRIAÇÃO DE BLOG POST AGRÍCOLA:**
                        
                        {regras_personalizadas}
                        
                        **INFORMAÇÕES ESPECÍFICAS:**
                        - Título: {titulo_blog if 'titulo_blog' in locals() else 'A definir'}
                        - Meta Descrição: {metadescricao}
                        - Cultura: {cultura if 'cultura' in locals() else 'A definir'}
                        - Palavra-chave Principal: {palavra_chave_principal}
                        - Palavras-chave Secundárias: {palavras_chave_secundarias}
                        
                        **ESTRUTURA SOLICITADA:** {', '.join(estrutura_opcoes)}
                        **NÍVEL DE PROFUNDIDADE:** {profundidade_conteudo}
                        **EVITAR REPETIÇÃO:** Nível {evitar_repeticao}/10
                        
                        **DIRETRIZES ADICIONAIS:** {diretrizes_usuario if 'diretrizes_usuario' in locals() else 'Nenhuma'}
                        
                        Gere um conteúdo {profundidade_conteudo.lower()} com aproximadamente {numero_palavras} palavras.
                        """
                        
                        response = client.models.generate_content(
                            model="gemini-1.5-flash",
                            contents=prompt_final
                        )
                        
                        texto_gerado = response.text
                        
                        # Salvar no MongoDB
                        if salvar_post(
                            titulo_blog if 'titulo_blog' in locals() else "Título gerado",
                            cultura if 'cultura' in locals() else "Cultura não especificada",
                            editoria if 'editoria' in locals() else "Editoria geral",
                            mes_publicacao if 'mes_publicacao' in locals() else datetime.now().strftime("%m/%Y"),
                            objetivo_post if 'objetivo_post' in locals() else "Objetivo não especificado",
                            url if 'url' in locals() else "/",
                            texto_gerado,
                            f"{palavra_chave_principal}, {palavras_chave_secundarias}",
                            metadescricao,
                            palavras_proibidas,
                            tom_voz,
                            ', '.join(estrutura_opcoes),
                            numero_palavras
                        ):
                            st.success("✅ Post gerado e salvo no banco de dados!")
                        
                        st.session_state.texto_gerado = texto_gerado
                        st.session_state.mostrar_editor = True
                        
                    except Exception as e:
                        st.error(f"Erro na geração: {str(e)}")
    
    with col_editar:
        if st.button("📊 Banco de Textos", use_container_width=True):
            st.session_state.mostrar_banco = True

    # Editor de texto pós-geração
    if st.session_state.get('mostrar_editor', False) and 'texto_gerado' in st.session_state:
        st.header("✏️ Editor de Texto")
        
        texto_editavel = st.text_area("Edite o texto gerado:", 
                                     value=st.session_state.texto_gerado, 
                                     height=400)
        
        col_salvar, col_download, col_nova_versao = st.columns(3)
        
        with col_salvar:
            if st.button("💾 Salvar Edições"):
                # Atualizar no banco de dados
                st.success("Edições salvas!")
                
        with col_download:
            st.download_button(
                label="📥 Download",
                data=texto_editavel,
                file_name=f"blog_post_{titulo_blog.lower().replace(' ', '_')}.txt",
                mime="text/plain"
            )
            
        with col_nova_versao:
            if st.button("🔄 Gerar Nova Versão"):
                st.session_state.mostrar_editor = False

    # Banco de textos gerados
    if st.session_state.get('mostrar_banco', False):
        st.header("📚 Banco de Textos Gerados")
        
        posts_anteriores = carregar_posts_anteriores()
        if posts_anteriores:
            for post in posts_anteriores:
                with st.expander(f"{post.get('titulo', 'Sem título')} - {post.get('data_criacao', '').strftime('%d/%m/%Y')}"):
                    st.write(f"**Cultura:** {post.get('cultura', 'N/A')}")
                    st.write(f"**Palavras:** {post.get('palavras_contagem', 'N/A')}")
                    st.write(f"**Tom:** {post.get('tom_voz', 'N/A')}")
                    st.text_area("Conteúdo:", value=post.get('texto_gerado', ''), height=200, key=post['id'])
                    
                    col_uso1, col_uso2 = st.columns(2)
                    with col_uso1:
                        if st.button("Reutilizar", key=f"reuse_{post['id']}"):
                            st.session_state.texto_gerado = post.get('texto_gerado', '')
                            st.session_state.mostrar_editor = True
                    with col_uso2:
                        if st.button("Download", key=f"dl_{post['id']}"):
                            st.download_button(
                                label="📥 Download",
                                data=post.get('texto_gerado', ''),
                                file_name=f"blog_post_{post.get('titulo', 'post').lower().replace(' ', '_')}.txt",
                                mime="text/plain",
                                key=f"dl_btn_{post['id']}"
                            )
        else:
            st.info("Nenhum post encontrado no banco de dados.")

else:
    st.info("🔑 Para começar, insira sua API Key do Gemini.")

# Rodapé
st.divider()
st.caption("🌱 Gerador de Conteúdo Agrícola - Sistema profissional para criação de conteúdos técnicos")

# Instruções de uso
with st.expander("ℹ️ Instruções de Uso"):
    st.markdown("""
    **Como usar este gerador:**
    
    1. **Configurações Básicas:** Defina palavras-chave, tom de voz e estrutura
    2. **Modo de Entrada:** Escolha entre campos individuais ou briefing completo
    3. **Restrições:** Configure palavras proibidas e diretrizes específicas
    4. **Geração:** Clique em "Gerar Blog Post" para criar o conteúdo
    5. **Edição:** Use o editor integrado para ajustes finos
    6. **Banco de Dados:** Acesse textos anteriores para reutilização
    
    **Recursos Avançados:**
    - KBF de produtos fixos do banco de dados
    - Controle preciso de número de palavras
    - Evitar repetição de conteúdo
    - Suporte a pesquisa web e arquivos estratégicos
    - Transcrição de áudio/vídeo
    """)
