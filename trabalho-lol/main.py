import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

@st.cache_data
def load_data(files):
    data = {}
    for file in files:
        file_name = file.name.replace(".csv", "")
        data[file_name] = pd.read_csv(file)
    return data

def apply_filters(df, team, position):
    if team != 'Todos' and 'team' in df.columns:
        df = df[df['team'] == team]
    if position != 'Todas' and 'position' in df.columns:
        df = df[df['position'] == position]
    return df

st.markdown("""
    <style>
        .title { color: #2C3E50; font-size: 2.4em; font-weight: bold; }
        .subtitle { color: #34495E; font-size: 1.6em; font-weight: bold; margin-top: 20px; }
        .section { margin-top: 30px; }
        .expander { background-color: #F0F3F4; border-radius: 8px; padding: 10px; }
        .separator { border-top: 1px solid #BDC3C7; margin-top: 20px; margin-bottom: 20px; }
    </style>
""", unsafe_allow_html=True)

st.markdown("<div class='title'>🏆 Análise Comparativa do Campeonato de League of Legends (2020 vs 2022)</div>", unsafe_allow_html=True)
st.markdown("Bem-vindo ao dashboard de análise de dados do Campeonato de League of Legends! Aqui você pode visualizar e comparar o desempenho de jogadores e equipes entre os anos de 2020 e 2022. Use os filtros ao lado para refinar os dados.")

uploaded_files_20 = st.file_uploader("📂 Escolha os arquivos do Campeonato de 2020", type='csv', accept_multiple_files=True)
uploaded_files_22 = st.file_uploader("📂 Escolha os arquivos do Campeonato de 2022", type='csv', accept_multiple_files=True)

if uploaded_files_20 and uploaded_files_22:
    data_20 = load_data(uploaded_files_20)
    data_22 = load_data(uploaded_files_22)

    df_20_players_main = data_20.get('wc_players_main')
    df_22_players_main = data_22.get('wc_players_main')
    df_20_team_main = data_20.get('wc_teams_main')
    df_22_team_main = data_22.get('wc_teams_main')

    if df_20_players_main is not None:
        st.write("Dados de 2020 carregados com sucesso:")
        st.write(df_20_players_main.head())
    else:
        st.error("⚠️ Não foi possível carregar os dados de 2020.")
    
    if df_22_players_main is not None:
        st.write("Dados de 2022 carregados com sucesso:")
        st.write(df_22_players_main.head())
    else:
        st.error("⚠️ Não foi possível carregar os dados de 2022.")

    if df_20_players_main is not None and df_22_players_main is not None:
        with st.sidebar:
            st.header("🎚️ Filtros para Análise")
            st.write("Refine a análise de dados utilizando os filtros abaixo.")
            
            teams = ['Todos'] + list(df_20_players_main['team'].unique()) if 'team' in df_20_players_main.columns else ['Todos']
            selected_team = st.selectbox("Equipe", teams)

            positions = ['Todas'] + list(df_20_players_main['position'].unique()) if 'position' in df_20_players_main.columns else ['Todas']
            selected_position = st.selectbox("Posição", positions)

        df_20_filtered = apply_filters(df_20_players_main, selected_team, selected_position)
        df_22_filtered = apply_filters(df_22_players_main, selected_team, selected_position)

        st.markdown("<div class='separator'></div>", unsafe_allow_html=True)

        st.markdown("<div class='subtitle'>📊 Estatísticas Gerais dos Jogadores (2020 vs 2022)</div>", unsafe_allow_html=True)
        st.write("Comparação de estatísticas descritivas dos jogadores. As métricas incluem desempenho médio por equipe e posição.")
        col1, col2 = st.columns(2)
        with col1:
            st.write("**Dados de 2020:**")
            st.write(df_20_filtered.describe())
        with col2:
            st.write("**Dados de 2022:**")
            st.write(df_22_filtered.describe())

        st.markdown("<div class='section'><h3>📈 Distribuição do Winrate dos Jogadores</h3></div>", unsafe_allow_html=True)
        st.write("Distribuição da taxa de vitória (Winrate) dos jogadores para os anos de 2020 e 2022.")
        if 'winrate' in df_20_filtered.columns and 'winrate' in df_22_filtered.columns:
            fig, ax = plt.subplots(1, 2, figsize=(12, 6))
            sns.histplot(df_20_filtered['winrate'], kde=True, ax=ax[0], color='blue')
            ax[0].set_title('Distribuição de Winrate - 2020')
            ax[0].set_xlabel('Winrate')
            ax[0].set_ylabel('Frequência')

            sns.histplot(df_22_filtered['winrate'], kde=True, ax=ax[1], color='red')
            ax[1].set_title('Distribuição de Winrate - 2022')
            ax[1].set_xlabel('Winrate')
            ax[1].set_ylabel('Frequência')

            st.pyplot(fig)

        st.markdown("<div class='separator'></div>", unsafe_allow_html=True)

        attribute_columns = ['kills', 'deaths', 'assists', 'gold_per_minute']
        avg_attributes_20 = df_20_filtered.groupby('position')[attribute_columns].mean()
        avg_attributes_22 = df_22_filtered.groupby('position')[attribute_columns].mean()

        comparison_df = pd.merge(avg_attributes_20, avg_attributes_22, on='position', how='outer', suffixes=('_2020', '_2022')).fillna(0)
        st.markdown("<div class='subtitle'>📊 Média de Atributos por Posição (2020 vs 2022)</div>", unsafe_allow_html=True)
        st.write("Média de atributos por posição de cada jogador, como 'kills', 'deaths' e 'gold_per_minute'.")
        st.bar_chart(comparison_df)

    if df_20_team_main is not None and df_22_team_main is not None:
        st.markdown("<div class='separator'></div>", unsafe_allow_html=True)

        team_metric_columns = ["games_played", "wins", "loses", "average_game_duration", "kills", "deaths", "kd"]
        filtered_team_metric_columns = [col for col in team_metric_columns if col in df_20_team_main.columns and pd.api.types.is_numeric_dtype(df_20_team_main[col])]

        avg_metrics_20_teams = df_20_team_main[filtered_team_metric_columns].mean()
        avg_metrics_22_teams = df_22_team_main[filtered_team_metric_columns].mean()

        comparison_data_teams = pd.DataFrame({
            '2020': avg_metrics_20_teams,
            '2022': avg_metrics_22_teams
        }, index=filtered_team_metric_columns)

        st.markdown("<div class='subtitle'>🏅 Média de Métricas das Equipes (2020 vs 2022)</div>", unsafe_allow_html=True)
        st.write("Comparação de métricas principais das equipes, como jogos jogados, vitórias, derrotas e taxa de KD.")
        st.bar_chart(comparison_data_teams)

else:
    st.error("⚠️ Por favor, carregue todos os arquivos necessários para 2020 e 2022.")
