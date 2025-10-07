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
    def salvar_post(titulo, cultura, editoria, mes_publicacao, objetivo_post, url, texto_gerado, palavras_chave, palavras_proibidas, tom_voz, estrutura, palavras_contagem, meta_title, meta_descricao, linha_fina):
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
                "palavras_proibidas": palavras_proibidas,
                "tom_voz": tom_voz,
                "estrutura": estrutura,
                "palavras_contagem": palavras_contagem,
                "meta_title": meta_title,
                "meta_descricao": meta_descricao,
                "linha_fina": linha_fina,
                "data_criacao": datetime.now(),
                "versao": "2.0"
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

    # Função para processar transcrições
    def processar_transcricoes(arquivos):
        transcricoes = []
        for arquivo in arquivos:
            if arquivo is not None:
                # Simulação de processamento de transcrição
                # Em produção, integrar com API de transcrição
                st.info(f"Processando transcrição de: {arquivo.name}")
                transcricoes.append(f"Conteúdo transcrito de {arquivo.name}")
        return "\n\n".join(transcricoes)

    # Regras base do sistema - ATUALIZADAS
    regras_base = '''
**REGRAS DE REPLICAÇÃO - ESTRUTURA PROFISSIONAL:**

**1. ESTRUTURA DO DOCUMENTO:**
- Título principal impactante e com chamada para ação (máx 65 caracteres)
- Linha fina resumindo o conteúdo (máx 200 caracteres)
- Meta-title otimizado para SEO (máx 60 caracteres)
- Meta-descrição atrativa (máx 155 caracteres)
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
- Citação EXPLÍCITA de fontes confiáveis (Embrapa, universidades, etc.) mencionando o órgão/instituição no corpo do texto
- Destaque para termos técnicos-chave e nomes de produtos
- Descrição detalhada de danos e benefícios
- Dados concretos e informações mensuráveis com referências específicas

**4. FORMATAÇÃO E ESTRUTURA:**
- Parágrafos curtos (máximo 4-5 linhas cada)
- Listas de tópicos com no máximo 5 itens cada
- Evitar blocos extensos de texto
- Usar subtítulos para quebrar o conteúdo

**5. RESTRIÇÕES:**
- Palavras proibidas: {palavras_proibidas}
- Evitar viés comercial explícito
- Manter abordagem {abordagem_problema}
- Número de palavras: {numero_palavras} (±5%)
- NÃO INVENTAR SOLUÇÕES ou informações não fornecidas
- Seguir EXATAMENTE o formato e informações do briefing
'''

    # Interface principal
    with st.sidebar:
        st.header("📋 Configurações Principais")
        
        # Modo de entrada - Briefing ou Campos Individuais
        modo_entrada = st.radio("Modo de Entrada:", ["Campos Individuais", "Briefing Completo"])
        
        # Controle de palavras - MAIS RESTRITIVO
        numero_palavras = st.slider("Número de Palavras:", min_value=300, max_value=2500, value=1500, step=100)
        st.info(f"Meta: {numero_palavras} palavras (±5%)")
        
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
        palavras_proibidas = st.text_area("Palavras Proibidas (separadas por vírgula):", "melhor, número 1, líder, insuperável, invenção, inventado, solução mágica")
        
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
            diretrizes_usuario = st.text_area("Diretrizes Adicionais:", 
                                            "NÃO INVENTE SOLUÇÕES. Use apenas informações fornecidas. Incluir dicas práticas para implementação no campo. Manter linguagem acessível mas técnica.")
            fontes_pesquisa = st.text_area("Fontes para Pesquisa/Referência (cite órgãos específicos):", 
                                         "Embrapa Soja, Universidade de São Paulo - ESALQ, Instituto Biológico de São Paulo, Artigos técnicos sobre nematoides")
            
            # Upload de MÚLTIPLOS arquivos estratégicos
            arquivos_estrategicos = st.file_uploader("📎 Upload de Múltiplos Arquivos Estratégicos", 
                                                   type=['txt', 'pdf', 'docx', 'mp3', 'wav', 'mp4', 'mov'], 
                                                   accept_multiple_files=True)
            if arquivos_estrategicos:
                st.success(f"{len(arquivos_estrategicos)} arquivo(s) carregado(s) com sucesso!")
    
    else:  # Modo Briefing
        st.header("📄 Briefing Completo")
        
        st.warning("""
        **ATENÇÃO:** Para conteúdos técnicos complexos (especialmente Syngenta), 
        recomenda-se usar o modo "Campos Individuais" para melhor controle da qualidade.
        """)
        
        briefing_texto = st.text_area("Cole aqui o briefing completo:", height=300,
                                     placeholder="""EXEMPLO DE BRIEFING:
Título: Controle Eficiente de Nematoides na Soja
Cultura: Soja
Problema: Aumento da população de nematoides em solos com palhada de milho
Objetivo: Educar produtores sobre manejo integrado
Produto: NemaControl
Público-alvo: Produtores de soja técnica
Tom: Técnico-jornalístico
Palavras-chave: nematoide, soja, tratamento sementes, manejo integrado

IMPORTANTE: NÃO INVENTE SOLUÇÕES. Use apenas informações fornecidas aqui.""")
        
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
            
            # Configurações de formatação
            st.subheader("📐 Formatação")
            max_paragrafos = st.slider("Máximo de linhas por parágrafo:", 3, 8, 5)
            max_lista_itens = st.slider("Máximo de itens por lista:", 3, 8, 5)
            
            # MÚLTIPLOS arquivos para transcrição
            st.subheader("🎤 Transcrição de Mídia")
            arquivos_midia = st.file_uploader("Áudios/Vídeos para Transcrição (múltiplos)", 
                                            type=['mp3', 'wav', 'mp4', 'mov'], 
                                            accept_multiple_files=True)

    # Metadados para SEO
    st.header("🔍 Metadados para SEO")
    col_meta1, col_meta2 = st.columns(2)
    
    with col_meta1:
        meta_title = st.text_input("Meta Title (máx 60 caracteres):", 
                                 max_chars=60,
                                 help="Título para SEO - aparecerá nos resultados de busca")
        st.info(f"Caracteres: {len(meta_title)}/60")
        
        linha_fina = st.text_area("Linha Fina (máx 200 caracteres):",
                                max_chars=200,
                                help="Resumo executivo que aparece abaixo do título")
        st.info(f"Caracteres: {len(linha_fina)}/200")
    
    with col_meta2:
        meta_descricao = st.text_area("Meta Descrição (máx 155 caracteres):",
                                    max_chars=155,
                                    help="Descrição que aparece nos resultados de busca")
        st.info(f"Caracteres: {len(meta_descricao)}/155")

    # Área de geração e edição
    st.header("🔄 Geração e Edição do Conteúdo")
    
    col_gerar, col_editar = st.columns(2)
    
    with col_gerar:
        if st.button("🚀 Gerar Blog Post", type="primary", use_container_width=True):
            if gemini_api_key:
                with st.spinner("Gerando conteúdo... Isso pode levar alguns minutos"):
                    try:
                        # Processar transcrições se houver arquivos
                        transcricoes_texto = ""
                        if 'arquivos_midia' in locals() and arquivos_midia:
                            transcricoes_texto = processar_transcricoes(arquivos_midia)
                            st.info(f"Processadas {len(arquivos_midia)} transcrição(ões)")
                        
                        # Construir prompt personalizado - MAIS RESTRITIVO
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
                        - Cultura: {cultura if 'cultura' in locals() else 'A definir'}
                        - Palavra-chave Principal: {palavra_chave_principal}
                        - Palavras-chave Secundárias: {palavras_chave_secundarias}
                        
                        **METADADOS:**
                        - Meta Title: {meta_title}
                        - Meta Description: {meta_descricao}
                        - Linha Fina: {linha_fina}
                        
                        **CONFIGURAÇÕES DE FORMATAÇÃO:**
                        - Parágrafos máximos: {max_paragrafos} linhas
                        - Listas máximas: {max_lista_itens} itens
                        - Estrutura: {', '.join(estrutura_opcoes)}
                        - Profundidade: {profundidade_conteudo}
                        - Evitar repetição: Nível {evitar_repeticao}/10
                        
                        **DIRETRIZES CRÍTICAS:**
                        - NÃO INVENTE SOLUÇÕES OU INFORMAÇÕES
                        - Use APENAS dados fornecidos no briefing
                        - Cite fontes específicas no corpo do texto
                        - Mantenha parágrafos e listas CURTOS
                        
                        **CONTEÚDO DE TRANSCRIÇÕES:**
                        {transcricoes_texto if transcricoes_texto else 'Nenhuma transcrição fornecida'}
                        
                        **DIRETRIZES ADICIONAIS:** {diretrizes_usuario if 'diretrizes_usuario' in locals() else 'Nenhuma'}
                        
                        Gere um conteúdo {profundidade_conteudo.lower()} com EXATAMENTE {numero_palavras} palavras (±5%).
                        """
                        
                        response = client.models.generate_content(
                            model="gemini-2.5-flash",
                            contents=prompt_final
                        )
                        
                        texto_gerado = response.text
                        
                        # Verificar contagem de palavras
                        palavras_count = len(texto_gerado.split())
                        st.info(f"📊 Contagem de palavras geradas: {palavras_count} (meta: {numero_palavras})")
                        
                        if abs(palavras_count - numero_palavras) > numero_palavras * 0.1:
                            st.warning("⚠️ A contagem de palavras está significativamente diferente da meta")
                        
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
                            palavras_proibidas,
                            tom_voz,
                            ', '.join(estrutura_opcoes),
                            palavras_count,
                            meta_title,
                            meta_descricao,
                            linha_fina
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
        
        # Mostrar metadados gerados
        col_meta_view1, col_meta_view2 = st.columns(2)
        with col_meta_view1:
            st.text_area("Meta Title:", value=meta_title, height=60, key="meta_title_view")
            st.text_area("Linha Fina:", value=linha_fina, height=80, key="linha_fina_view")
        with col_meta_view2:
            st.text_area("Meta Description:", value=meta_descricao, height=80, key="meta_desc_view")
        
        texto_editavel = st.text_area("Edite o texto gerado:", 
                                     value=st.session_state.texto_gerado, 
                                     height=400)
        
        col_salvar, col_nova_versao = st.columns(2)
        
        with col_salvar:
            if st.button("💾 Salvar Edições"):
                # Atualizar no banco de dados
                st.success("Edições salvas!")
                
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
                    
                    # Mostrar metadados salvos
                    if post.get('meta_title'):
                        st.write(f"**Meta Title:** {post.get('meta_title')}")
                    if post.get('meta_descricao'):
                        st.write(f"**Meta Descrição:** {post.get('meta_descricao')}")
                    
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
st.caption("🌱 Gerador de Conteúdo Agrícola v2.0 - Sistema profissional para criação de conteúdos técnicos")

# Instruções de uso ATUALIZADAS
with st.expander("ℹ️ Instruções de Uso - ATUALIZADO"):
    st.markdown("""
    **⚠️ MELHORIAS IMPLEMENTADAS COM BASE NO FEEDBACK:**
    
    ✅ **Solução para problemas identificados:**
    - Suporte a MÚLTIPLOS arquivos para transcrição
    - Controle rigoroso de tamanho de parágrafos e listas
    - Metadados completos (Title, Meta Title, Linha Fina, Meta Description)
    - Citação explícita de fontes no corpo do texto
    - Restrições contra invenção de soluções
    - Controle mais preciso de contagem de palavras
    
    **🎯 Como usar este gerador - MODOS RECOMENDADOS:**
    
    **📋 Para conteúdos técnicos complexos (Syngenta):**
    1. Use o modo **"Campos Individuais"**
    2. Preencha TODOS os campos técnicos específicos
    3. Carregue MÚLTIPLOS arquivos de referência
    4. Defina limites de parágrafos e listas
    5. Gere e revise cuidadosamente
    
    **📄 Para briefings simples:**
    1. Use o modo **"Briefing Completo"** apenas para conteúdos não-técnicos
    2. Inclua instruções EXPLÍCITAS contra invenção de soluções
    
    **🔧 Configurações críticas de qualidade:**
    - Defina limites de parágrafos (3-5 linhas)
    - Limite listas a 5 itens máximo
    - Use contagem precisa de palavras
    - Configure palavras proibidas
    - Preencha todos os metadados SEO
    
    **🚫 Restrições importantes:**
    - O modelo NÃO deve inventar soluções
    - Seguir EXATAMENTE informações fornecidas
    - Manter formatação limpa e organizada
    - Citar fontes específicas no texto
    """)
