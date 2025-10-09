import streamlit as st

# --- Funções de manipulação do histórico ---
def update_history(new_value):
    if len(st.session_state.history) >= 9:
        st.session_state.history.pop()
    st.session_state.history.insert(0, new_value)

def clear_history():
    st.session_state.history = []

# --- Funções de análise ---
def count_alternations(history):
    count = 0
    for i in range(len(history) - 1):
        if history[i] != history[i + 1] and history[i] != '🟡' and history[i + 1] != '🟡':
            count += 1
    return count

def count_consecutive_repetitions(history):
    count = max_count = 1
    for i in range(1, len(history)):
        if history[i] == history[i - 1] and history[i] != '🟡':
            count += 1
            max_count = max(max_count, count)
        else:
            count = 1
    return max_count

def find_doubles_blocks(history):
    blocks, i = 0, 0
    while i < len(history) - 1:
        if history[i] == history[i + 1] and history[i] != '🟡':
            blocks += 1
            i += 2
        else:
            i += 1
    return blocks

def find_triples_blocks(history):
    blocks, i = 0, 0
    while i < len(history) - 2:
        if history[i] == history[i + 1] == history[i + 2] and history[i] != '🟡':
            blocks += 1
            i += 3
        else:
            i += 1
    return blocks

def is_mirror_pattern(history):
    n = len(history)
    if n < 6:
        return False
    mid = n // 2
    for i in range(mid):
        left = history[i]
        right = history[n - 1 - i]
        if left == '🟡' or right == '🟡':
            continue
        if left != right:
            return False
    return True

def contains_draw_in_last_n(history, n):
    return '🟡' in history[:n]

def detect_zigzag_break(history):
    for i in range(len(history) - 3):
        segment = history[i:i+4]
        if segment[0] == segment[2] and segment[1] == segment[3] and segment[0] != segment[1] and '🟡' not in segment:
            return True
    return False

# --- Sistema unificado de padrões ---
def detect_pattern(history):
    if len(history) < 4:
        return 'Insuficientes dados', None

    alternations = count_alternations(history)
    max_reps = count_consecutive_repetitions(history)
    doubles = find_doubles_blocks(history)
    triples = find_triples_blocks(history)
    mirror = is_mirror_pattern(history)
    draws = history.count('🟡')
    zigzag_break = detect_zigzag_break(history)

    if alternations >= 4 and max_reps <= 2 and not contains_draw_in_last_n(history, 3):
        if len(history) >= 6 and history[4] == history[5]:
            return 'Surf 🌊', "Ciclo de 4 a 8 alternâncias, pico na 5ª-6ª em repetição. Após empate 🟡, apostar inversão (lado oposto)."
        return 'Surf 🌊', "Alternância suave, após 4 alternâncias apostar repetição da última cor."

    if 3 <= alternations <= 6 and max_reps == 1:
        if contains_draw_in_last_n(history, 3):
            return 'Ping-Pong 🏓', "Alternância limpa, após empate apostar inversão. Na 5ª jogada apostar repetição da última cor."
        return 'Ping-Pong 🏓', "Alternância direta e limpa; preparar para quebra após 3+ alternâncias."

    if doubles >= 1 and max_reps == 2:
        return 'Alternância Suja 🔁', "Duplas indicam microquebras. Após dupla apostar alternância (cor oposta). Após duas duplas, preparar inversão."

    if zigzag_break and doubles >= 1 and max_reps >= 2 and draws <= 1 and len(history) >= 6:
        return 'Zig-Zag ⚡', "Simula alternância com reversões duplas. Apostar inversão após dupla; após empate apostar lado anterior."

    if doubles >= 2:
        if doubles >= 3:
            return '2x2 (Duplas) 🟦', "Ciclo de 3 a 4 blocos. Após 3ª dupla, apostar inversão total."
        return '2x2 (Duplas) 🟦', "Duplas alternadas. Após 2ª dupla preparar inversão."

    if triples >= 2:
        return '3x3 (Triplas) 🔺', "Triplas alternadas. Após 2ª tripla apostar lado oposto. Se empate, valor reduzido."

    if mirror:
        return 'Espelhado 🪞', "Sequência refletida. Após centro apostar repetição da metade anterior."

    if draws >= 1 and doubles >= 2 and alternations >= 1:
        return 'Colapso / Reverso Quântico 🌀', "Padrão irregular. Evitar apostas. Reentrar após ciclo limpo."

    if contains_draw_in_last_n(history, 1):
        return 'Âncora (Empate) ⚓', "Após empate apostar no lado oposto da última cor. Novo empate: inverter novamente."

    if draws >= 2 and doubles >= 1 and triples >= 1:
        return 'Camuflado 🕵️‍♂️', "Mistura de padrões. Apostar só após 2 blocos coerentes limpos."

    return 'Padrão Desconhecido', 'Sem sugestão clara'

# --- Nível de manipulação ---
def calculate_manipulation_level(history):
    alternations = count_alternations(history)
    draws = history.count('🟡')
    max_reps = count_consecutive_repetitions(history)
    doubles = find_doubles_blocks(history)
    triples = find_triples_blocks(history)

    if alternations <= 2 and draws == 0 and max_reps <= 2:
        return 1
    elif draws <= 2 and max_reps <= 2 and doubles <= 1:
        return 3
    elif alternations >= 4 and draws >= 1:
        return 5
    elif max_reps >= 3 or doubles >= 3:
        return 7
    elif triples >= 2 or draws >= 3 or doubles >= 4:
        return 9
    return 4

# --- Normalizar predição ---
def normalize_prediction(pred_raw):
    keys = ['🔴', '🔵', '🟡']
    total = sum(pred_raw.get(k, 0) for k in keys)
    if total == 0:
        return {k: 33 for k in keys}
    return {k: round(pred_raw.get(k, 0) / total * 100) for k in keys}

# --- Previsão ---
def predict_next(history, manipulation_level, pattern):
    if not history:
        return {'🔴': 33, '🔵': 33, '🟡': 34}
    last = history[0]
    inverse = '🔴' if last == '🔵' else '🔵'

    if pattern.startswith('Surf'):
        if contains_draw_in_last_n(history, 1) and len(history) > 1:
            return {history[1]: 70, '🟡': 10, last: 20}
        return {last: 75, '🟡': 5, inverse: 20}

    if pattern.startswith('Ping-Pong'):
        if contains_draw_in_last_n(history, 1) and len(history) > 1:
            return {history[1]: 80, '🟡': 10, last: 10}
        return {last: 70, '🟡': 10, inverse: 20}

    if pattern.startswith('Alternância Suja'):
        return {inverse: 70, last: 25, '🟡': 5}

    if pattern.startswith('Zig-Zag'):
        return {inverse: 75, last: 20, '🟡': 5}

    if pattern.startswith('2x2'):
        return {inverse: 80, last: 15, '🟡': 5}

    if pattern.startswith('3x3'):
        return {inverse: 80, last: 15, '🟡': 5}

    if pattern.startswith('Espelhado'):
        return {last: 70, '🟡': 10, inverse: 20}

    if pattern.startswith('Colapso'):
        return {'🔴': 33, '🔵': 33, '🟡': 34}

    if pattern.startswith('Âncora'):
        return {inverse: 75, last: 20, '🟡': 5}

    if pattern.startswith('Camuflado'):
        return {'🔴': 33, '🔵': 33, '🟡': 34}

    return {'🔴': 33, '🔵': 33, '🟡': 34}

# --- Algoritmo híbrido de análise e sugestão ---
def hybrid_analysis_and_suggestion(history):
    pattern, strategy = detect_pattern(history)
    level = calculate_manipulation_level(history)

    if not history or len(history) < 4:
        return pattern, strategy, level, 'Aguardando dados suficientes para análise.'

    if contains_draw_in_last_n(history, 1):
        last = history[0]
        opposite = '🔴' if last == '🔵' else '🔵'
        return pattern, strategy, level, f'Após empate, aposte na inversão: {opposite}'

    if pattern == 'Surf 🌊':
        last = history[0]
        return pattern, strategy, level, f'Aposte na última cor: {last}'

    if pattern.startswith('3x3'):
        last = history[0]
        opposite = '🔴' if last == '🔵' else '🔵'
        return pattern, strategy, level, f'Após segunda tripla, aposte no oposto: {opposite}'

    bet_text = suggest_bet(pattern, history)
    return pattern, strategy, level, bet_text

# --- Sugestões simples baseadas em padrões ---
def suggest_bet(pattern, history):
    if not history or len(history) < 2:
        return 'Aguardando mais dados.'

    if pattern == 'Insuficientes dados':
        return 'Dados insuficientes.'

    last = history[0]
    opposite = '🔴' if last == '🔵' else '🔵'

    if pattern == 'Surf 🌊':
        if '🟡' in history[:3]:
            return f'Aposte na inversão: {opposite}'
        return f'Aposte na última cor: {last}'

    if pattern == 'Ping-Pong 🏓':
        if '🟡' in history[:3]:
            return f'Aposte na inversão: {opposite}'
        return f'Aposte na última cor: {last}'

    if pattern == 'Alternância Suja 🔁':
        return f'Aposte na alternância: {opposite}'

    if pattern == 'Zig-Zag ⚡':
        return f'Aposte na inversão após dupla: {opposite}'

    if pattern.startswith('2x2'):
        return f'Aposte no lado oposto após segunda dupla: {opposite}'

    if pattern.startswith('3x3'):
        if '🟡' in history[:3]:
            return f'Após empate, inverta e reduza aposta: {opposite}'
        return f'Aposte na inversão após 2 triplas: {opposite}'

    if pattern == 'Espelhado 🪞':
        return f'Repita metade anterior: {last}'

    if pattern == 'Colapso / Reverso Quântico 🌀':
        return 'Não apostar; aguarde padrão limpo.'

    if pattern == 'Âncora (Empate) ⚓':
        if '🟡' in history[:2]:
            if len(history) > 2 and history[2] == last:
                return f'Aposte no mesmo lado após empate: {last}'
            return f'Aposte na inversão: {opposite}'
        return f'Aposte na inversão: {opposite}'

    if pattern == 'Camuflado 🕵️‍♂️':
        return 'Aposte após confirmação de blocos limpos.'

    return 'Sem sugestão clara.'

# --- Sinal de alerta ---
def alert_signal(level):
    if 4 <= level <= 6:
        return '🟢 Brecha Detectada'
    elif 7 <= level <= 8:
        return '🟡 Risco Médio'
    elif level == 9:
        return '🔴 Manipulação Alta'
    else:
        return '🟢 Normal'

# --- Inicialização estado ---
if 'history' not in st.session_state:
    st.session_state.history = []

# --- Interface aprimorada ---
st.title("Football Studio - Análise Híbrida & Sistema Unificado (Cartas Físicas)")

# Botões de controle na parte principal para melhor usabilidade
col1, col2, col3, col4 = st.columns(4)
if col1.button("🔴"):
    update_history("🔴")
if col2.button("🔵"):
    update_history("🔵")
if col3.button("🟡"):
    update_history("🟡")
if col4.button("Limpar Histórico"):
    clear_history()

st.markdown("---")

# Histórico exibido com destaque
st.subheader("Histórico (mais recente → mais antigo):")
if st.session_state.history:
    hist_display = " ".join(st.session_state.history)
    st.markdown(f"<div style='font-size: 2rem'>{hist_display}</div>", unsafe_allow_html=True)
else:
    st.write("Nenhum resultado registrado.")

st.markdown("---")

# Analise híbrida completa
pattern, strategy, level, bet_recommendation = hybrid_analysis_and_suggestion(st.session_state.history)
prediction_raw = predict_next(st.session_state.history, level, pattern)
prediction = normalize_prediction(prediction_raw)
alert_msg = alert_signal(level)

# Exibir resultados
st.subheader("Resumo da Análise")
st.markdown(f"- **Padrão Detectado:** {pattern}")
st.markdown(f"- **Descrição do Padrão / Estratégia:** {strategy}")
st.markdown(f"- **Nível de Manipulação:** {level}")
st.markdown(f"- **Sinal de Alerta:** {alert_msg}")

st.subheader("Previsão da Próxima Jogada")
if not st.session_state.history or pattern == "Insuficientes dados":
    st.write("Não há dados suficientes para previsão.")
else:
    st.write(f"🔴 {prediction['🔴']}% | 🔵 {prediction['🔵']}% | 🟡 {prediction['🟡']}%")

st.subheader("Sugestão de Aposta")
st.write(bet_recommendation)
