import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from scipy.stats import binom
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="Análise de Overbooking e ROI",
    page_icon="✈️",
    layout="wide"
)

class OverbookingAnalyzer:
    def __init__(self, capacidade=120, taxa_no_show=0.12):
        self.capacidade = capacidade
        self.taxa_no_show = taxa_no_show
        self.prob_comparecimento = 1 - taxa_no_show
        
    def calcular_prob_overbooking(self, passagens_vendidas):
        return 1 - binom.cdf(self.capacidade, passagens_vendidas, self.prob_comparecimento)
    
    def encontrar_max_passagens(self, limite_risco=0.07):
        for n in range(self.capacidade, self.capacidade + 50):
            prob = self.calcular_prob_overbooking(n)
            if prob > limite_risco:
                return n - 1
        return self.capacidade
    
    def analise_financeira(self, passagens_extra, preco_passagem=500, custo_indenizacao=1200):
        passagens_total = self.capacidade + passagens_extra
        prob_overbooking = self.calcular_prob_overbooking(passagens_total)
        
        valor_esperado_excesso = 0
        for k in range(self.capacidade + 1, passagens_total + 1):
            prob_k = binom.pmf(k, passagens_total, self.prob_comparecimento)
            excesso = k - self.capacidade
            valor_esperado_excesso += prob_k * excesso
        
        receita_adicional = passagens_extra * preco_passagem
        custo_esperado = valor_esperado_excesso * custo_indenizacao
        lucro_esperado = receita_adicional - custo_esperado
        
        return {
            'receita_adicional': receita_adicional,
            'custo_esperado': custo_esperado,
            'lucro_esperado': lucro_esperado,
            'prob_overbooking': prob_overbooking
        }

class ROIAnalyzer:
    def __init__(self, investimento=50000, receita_esperada=80000, custo_operacional=10000):
        self.investimento = investimento
        self.receita_esperada = receita_esperada
        self.custo_operacional = custo_operacional
        
    def calcular_roi(self, receita_real=None):
        receita = receita_real if receita_real else self.receita_esperada
        lucro = receita - self.custo_operacional
        return (lucro / self.investimento) * 100
    
    def simulacao_monte_carlo(self, n_simulacoes=10000, media_performance=0.75, std_performance=0.15):
        np.random.seed(42)
        performances = np.random.normal(media_performance, std_performance, n_simulacoes)
        performances = np.clip(performances, 0, 1)
        receitas = performances * self.receita_esperada
        rois = [(receita - self.custo_operacional) / self.investimento * 100 for receita in receitas]
        return {'receitas': receitas, 'rois': rois, 'performances': performances}

# Interface Streamlit
st.title("✈️ Análise de Overbooking e ROI - Aérea Confiável")
st.markdown("**Desenvolvido por: Nícolas Duarte Vasconcellos | Matrícula: 200042343**")

# Sidebar para parâmetros
st.sidebar.header("📊 Parâmetros de Entrada")

# Parâmetros de Overbooking
st.sidebar.subheader("✈️ Overbooking")
capacidade = st.sidebar.number_input("Capacidade da Aeronave", value=120, min_value=50, max_value=500)
taxa_no_show = st.sidebar.slider("Taxa de No-Show (%)", min_value=5.0, max_value=25.0, value=12.0, step=0.5) / 100
passagens_vendidas = st.sidebar.number_input("Passagens Vendidas", value=130, min_value=capacidade, max_value=capacidade+50)

# Parâmetros de ROI
st.sidebar.subheader("💰 ROI")
investimento = st.sidebar.number_input("Investimento Inicial (R$)", value=50000, min_value=10000, max_value=200000)
receita_esperada = st.sidebar.number_input("Receita Esperada (R$)", value=80000, min_value=20000, max_value=200000)
custo_operacional = st.sidebar.number_input("Custo Operacional (R$)", value=10000, min_value=5000, max_value=50000)

# Instanciar analisadores
analyzer = OverbookingAnalyzer(capacidade, taxa_no_show)
roi_analyzer = ROIAnalyzer(investimento, receita_esperada, custo_operacional)

# Tabs principais
tab1, tab2, tab3, tab4 = st.tabs(["📊 Dashboard", "✈️ Overbooking", "💰 ROI", "📈 Simulações"])

with tab1:
    st.header("📊 Dashboard Executivo")
    
    # Métricas principais
    col1, col2, col3, col4 = st.columns(4)
    
    prob_overbooking = analyzer.calcular_prob_overbooking(passagens_vendidas) * 100
    roi_esperado = roi_analyzer.calcular_roi()
    max_passagens = analyzer.encontrar_max_passagens()
    analise_fin = analyzer.analise_financeira(passagens_vendidas - capacidade)
    
    with col1:
        st.metric(
            "Probabilidade Overbooking", 
            f"{prob_overbooking:.2f}%",
            delta=f"{'✅ OK' if prob_overbooking <= 7 else '⚠️ Alto'}"
        )
    
    with col2:
        st.metric(
            "ROI Esperado",
            f"{roi_esperado:.1f}%",
            delta=f"{'🚀 Excelente' if roi_esperado > 100 else '📈 Bom' if roi_esperado > 50 else '⚠️ Baixo'}"
        )
    
    with col3:
        st.metric(
            "Máx. Passagens (7%)",
            f"{max_passagens}",
            delta=f"{passagens_vendidas - max_passagens} acima do limite"
        )
    
    with col4:
        st.metric(
            "Lucro Esperado",
            f"R$ {analise_fin['lucro_esperado']:,.0f}",
            delta=f"{'💰 Lucrativo' if analise_fin['lucro_esperado'] > 0 else '💸 Prejuízo'}"
        )
    
    # Gráfico de risco vs passagens
    st.subheader("🎯 Análise de Risco")
    passagens_range = np.arange(capacidade, capacidade + 31)
    riscos = [analyzer.calcular_prob_overbooking(n) * 100 for n in passagens_range]
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=passagens_range, y=riscos,
        mode='lines+markers',
        name='Risco de Overbooking',
        line=dict(color='blue', width=3)
    ))
    fig.add_hline(y=7, line_dash="dash", line_color="red", 
                  annotation_text="Limite de Risco (7%)")
    fig.add_vline(x=passagens_vendidas, line_dash="dot", line_color="green",
                  annotation_text=f"Situação Atual ({passagens_vendidas})")
    
    fig.update_layout(
        title="Risco de Overbooking vs Passagens Vendidas",
        xaxis_title="Passagens Vendidas",
        yaxis_title="Probabilidade de Overbooking (%)",
        height=400
    )
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.header("✈️ Análise Detalhada de Overbooking")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📋 Parâmetros Atuais")
        st.write(f"**Capacidade:** {capacidade} lugares")
        st.write(f"**Passagens Vendidas:** {passagens_vendidas}")
        st.write(f"**Taxa No-Show:** {taxa_no_show*100:.1f}%")
        st.write(f"**Prob. Comparecimento:** {(1-taxa_no_show)*100:.1f}%")
        
        st.subheader("🎯 Resultados")
        st.write(f"**Prob. Overbooking:** {prob_overbooking:.2f}%")
        st.write(f"**Status:** {'✅ Dentro do limite' if prob_overbooking <= 7 else '⚠️ Acima do limite'}")
        st.write(f"**Máx. Passagens (7%):** {max_passagens}")
    
    with col2:
        st.subheader("💰 Análise Financeira")
        preco_passagem = st.number_input("Preço por Passagem (R$)", value=500, min_value=100, max_value=2000)
        custo_indenizacao = st.number_input("Custo de Indenização (R$)", value=1200, min_value=500, max_value=5000)
        
        resultado_fin = analyzer.analise_financeira(
            passagens_vendidas - capacidade, 
            preco_passagem, 
            custo_indenizacao
        )
        
        st.metric("Receita Adicional", f"R$ {resultado_fin['receita_adicional']:,.2f}")
        st.metric("Custo Esperado", f"R$ {resultado_fin['custo_esperado']:,.2f}")
        st.metric("Lucro Esperado", f"R$ {resultado_fin['lucro_esperado']:,.2f}")
    
    # Tabela de cenários
    st.subheader("📊 Tabela de Cenários")
    cenarios_data = []
    for n in range(capacidade, capacidade + 21):
        prob = analyzer.calcular_prob_overbooking(n) * 100
        resultado = analyzer.analise_financeira(n - capacidade, preco_passagem, custo_indenizacao)
        cenarios_data.append({
            'Passagens': n,
            'Prob. Overbooking (%)': f"{prob:.2f}",
            'Lucro Esperado (R$)': f"{resultado['lucro_esperado']:,.0f}",
            'Status': '✅ OK' if prob <= 7 else '⚠️ Alto Risco'
        })
    
    df_cenarios = pd.DataFrame(cenarios_data)
    st.dataframe(df_cenarios, use_container_width=True)

with tab3:
    st.header("💰 Análise de ROI do Sistema")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Parâmetros do Investimento")
        st.write(f"**Investimento Inicial:** R$ {investimento:,.2f}")
        st.write(f"**Receita Esperada:** R$ {receita_esperada:,.2f}")
        st.write(f"**Custo Operacional:** R$ {custo_operacional:,.2f}")
        st.write(f"**Lucro Esperado:** R$ {receita_esperada - custo_operacional:,.2f}")
        
        st.metric("ROI Calculado", f"{roi_esperado:.2f}%")
    
    with col2:
        st.subheader("🎯 Análise de Sensibilidade")
        
        # Análise de sensibilidade para diferentes custos
        custos_test = np.arange(5000, 25001, 2500)
        rois_test = [(receita_esperada - custo) / investimento * 100 for custo in custos_test]
        
        fig_sens = go.Figure()
        fig_sens.add_trace(go.Scatter(
            x=custos_test, y=rois_test,
            mode='lines+markers',
            name='ROI vs Custo Operacional'
        ))
        fig_sens.add_hline(y=50, line_dash="dash", line_color="green",
                          annotation_text="ROI Objetivo (50%)")
        
        fig_sens.update_layout(
            title="Sensibilidade: ROI vs Custo Operacional",
            xaxis_title="Custo Operacional (R$)",
            yaxis_title="ROI (%)",
            height=300
        )
        st.plotly_chart(fig_sens, use_container_width=True)
    
    # Cenários de ROI
    st.subheader("🎲 Cenários de Performance")
    
    col1, col2, col3 = st.columns(3)
    
    # Cenário Pessimista (70% da receita)
    with col1:
        roi_pessimista = roi_analyzer.calcular_roi(receita_esperada * 0.7)
        st.metric("Cenário Pessimista", f"{roi_pessimista:.1f}%", "70% da receita")
    
    # Cenário Realista (85% da receita)
    with col2:
        roi_realista = roi_analyzer.calcular_roi(receita_esperada * 0.85)
        st.metric("Cenário Realista", f"{roi_realista:.1f}%", "85% da receita")
    
    # Cenário Otimista (100% da receita)
    with col3:
        roi_otimista = roi_analyzer.calcular_roi(receita_esperada)
        st.metric("Cenário Otimista", f"{roi_otimista:.1f}%", "100% da receita")

with tab4:
    st.header("📈 Simulações Monte Carlo")
    
    # Parâmetros da simulação
    col1, col2 = st.columns(2)
    with col1:
        n_simulacoes = st.selectbox("Número de Simulações", [1000, 5000, 10000], index=2)
        media_performance = st.slider("Performance Média", 0.5, 1.0, 0.75, 0.05)
    
    with col2:
        std_performance = st.slider("Desvio Padrão", 0.05, 0.3, 0.15, 0.01)
        seed = st.number_input("Seed (Reprodutibilidade)", value=42, min_value=1, max_value=1000)
    
    if st.button("🔄 Executar Simulação"):
        np.random.seed(seed)
        simulacao = roi_analyzer.simulacao_monte_carlo(n_simulacoes, media_performance, std_performance)
        
        # Estatísticas da simulação
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("ROI Médio", f"{np.mean(simulacao['rois']):.2f}%")
        
        with col2:
            st.metric("ROI Mediano", f"{np.median(simulacao['rois']):.2f}%")
        
        with col3:
            prob_positivo = (np.array(simulacao['rois']) > 0).mean() * 100
            st.metric("ROI Positivo", f"{prob_positivo:.1f}%")
        
        with col4:
            prob_50 = (np.array(simulacao['rois']) > 50).mean() * 100
            st.metric("ROI > 50%", f"{prob_50:.1f}%")
        
        # Gráficos da simulação
        col1, col2 = st.columns(2)
        
        with col1:
            fig_hist = px.histogram(
                x=simulacao['rois'], 
                title="Distribuição do ROI",
                labels={'x': 'ROI (%)', 'y': 'Frequência'},
                nbins=50
            )
            fig_hist.add_vline(x=roi_esperado, line_dash="dash", line_color="red",
                              annotation_text=f"ROI Esperado: {roi_esperado:.1f}%")
            st.plotly_chart(fig_hist, use_container_width=True)
        
        with col2:
            fig_scatter = px.scatter(
                x=np.array(simulacao['performances']) * 100,
                y=simulacao['receitas'],
                title="Performance vs Receita",
                labels={'x': 'Performance (%)', 'y': 'Receita (R$)'}
            )
            st.plotly_chart(fig_scatter, use_container_width=True)
        
        # Tabela de percentis
        st.subheader("📊 Análise de Percentis")
        percentis = [10, 25, 50, 75, 90]
        dados_percentis = []
        
        for p in percentis:
            roi_p = np.percentile(simulacao['rois'], p)
            receita_p = np.percentile(simulacao['receitas'], p)
            dados_percentis.append({
                'Percentil': f"{p}°",
                'ROI (%)': f"{roi_p:.2f}",
                'Receita (R$)': f"R$ {receita_p:,.0f}"
            })
        
        df_percentis = pd.DataFrame(dados_percentis)
        st.dataframe(df_percentis, use_container_width=True)

# Conclusões
st.header("🎯 Conclusões e Recomendações")

col1, col2 = st.columns(2)

with col1:
    st.subheader("✈️ Overbooking")
    if prob_overbooking <= 7:
        st.success(f"✅ Risco aceitável: {prob_overbooking:.2f}%")
        st.write("A estratégia atual está dentro dos limites de risco estabelecidos.")
    else:
        st.warning(f"⚠️ Risco elevado: {prob_overbooking:.2f}%")
        st.write(f"Recomenda-se reduzir para máximo de {max_passagens} passagens.")

with col2:
    st.subheader("💰 Sistema ROI")
    if roi_esperado > 100:
        st.success(f"🚀 ROI excelente: {roi_esperado:.2f}%")
        st.write("Investimento altamente recomendado.")
    elif roi_esperado > 50:
        st.success(f"📈 ROI bom: {roi_esperado:.2f}%")
        st.write("Investimento recomendado com monitoramento.")
    else:
        st.warning(f"⚠️ ROI baixo: {roi_esperado:.2f}%")
        st.write("Revisar parâmetros do investimento.")

st.markdown("---")
st.markdown("**Desenvolvido por Nícolas Duarte Vasconcellos (200042343) | UnB - Engenharia de Produção**")
