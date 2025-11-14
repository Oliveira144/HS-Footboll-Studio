import streamlit as st
from collections import Counter, deque, defaultdict

class FootballStudioSuperInteligente:
    def __init__(self, saldo_inicial=1000, max_historico=500):
        self.valor_carta = {str(i): i for i in range(2, 11)}
        self.valor_carta.update({'J':11, 'Q':12, 'K':13, 'A':14})
        self.historico = deque(maxlen=max_historico)
        self.saldo = saldo_inicial
        self.pesos = {'freq_simples': 0.25, 'markov_ord1': 0.35, 'markov_ord2': 0.25, 'streaks': 0.15}

    def validar_carta(self, carta):
        return carta in self.valor_carta

    def calcular_resultado(self, casa, visitante):
        val_casa = self.valor_carta[casa]
        val_visitante = self.valor_carta[visitante]
        if val_casa > val_visitante:
            return 'Casa'
        elif val_visitante > val_casa:
            return 'Visitante'
        else:
            return 'Empate'

    def registrar_rodada(self, casa, visitante):
        res = self.calcular_resultado(casa, visitante)
        self.historico.append((casa, visitante, res))
        return res

    def frequencia_simples(self):
        res = [r[2] for r in self.historico]
        c = Counter(res)
        total = len(res)
        if total == 0:
            return {k:0 for k in ['Casa','Visitante','Empate']}
        return {k: c[k]/total for k in ['Casa','Visitante','Empate']}

    def cadeia_markov_ordem1(self):
        res = [r[2] for r in self.historico]
        trans = Counter()
        total = Counter()
        for i in range(len(res)-1):
            trans[(res[i], res[i+1])] +=1
            total[res[i]] +=1
        probs = {}
        for (a,b), count in trans.items():
            probs[(a,b)] = count/total[a]
        return probs

    def cadeia_markov_ordem2(self):
        res = [r[2] for r in self.historico]
        trans = Counter()
        total = Counter()
        for i in range(len(res)-2):
            key = (res[i], res[i+1])
            trans[(key, res[i+2])] +=1
            total[key] +=1
        probs = {}
        for (key,b), count in trans.items():
            probs[(key,b)] = count/total[key]
        return probs

    def analisar_streaks(self):
        res = [r[2] for r in self.historico]
        streaks = defaultdict(int)
        if not res:
            return streaks
        atual = res[0]
        cont = 1
        for i in range(1,len(res)):
            if res[i] == atual:
                cont +=1
            else:
                streaks[(atual, cont)] +=1
                atual = res[i]
                cont = 1
        streaks[(atual, cont)] +=1
        total_streaks = sum(streaks.values())
        prob_streaks = {}
        for (estado,length), count in streaks.items():
            prob_streaks[(estado,length)] = count/total_streaks if total_streaks>0 else 0
        return prob_streaks

    def prever_proximo(self):
        if len(self.historico) < 10:
            freq = self.frequencia_simples()
            return max(freq, key=freq.get), 'Baixa'

        freq = self.frequencia_simples()
        markov1 = self.cadeia_markov_ordem1()
        markov2 = self.cadeia_markov_ordem2()
        streaks = self.analisar_streaks()
        ultimo = self.historico[-1][2]
        penultimo = self.historico[-2][2] if len(self.historico)>1 else None

        decisao = {estado:0 for estado in ['Casa','Visitante','Empate']}

        for e in decisao:
            decisao[e] += freq.get(e,0) * self.pesos['freq_simples']

        for e in decisao:
            decisao[e] += markov1.get((ultimo, e),0) * self.pesos['markov_ord1']

        if penultimo:
            for e in decisao:
                decisao[e] += markov2.get(((penultimo, ultimo), e), 0) * self.pesos['markov_ord2']

        prob_reversao = False
        streak_max = max((length for (state,length) in streaks if state==ultimo), default=0)
        if streak_max >= 3:
            prob_reversao = True

        if prob_reversao:
            decisao[ultimo] *= 0.4
            outros = [e for e in decisao if e != ultimo]
            distrib = (1 - decisao[ultimo]) / len(outros)
            for e in outros:
                decisao[e] += distrib

        melhor = max(decisao, key=decisao.get)
        confianca = decisao[melhor]

        nivel_confianca = 'Alta' if confianca > 0.6 else ('Média' if confianca > 0.4 else 'Baixa')

        return melhor, nivel_confianca

    def sugerir_aposta(self):
        pred, conf = self.prever_proximo()
        return f'Sugestão Super Inteligente: Aposte na {pred} (Confiança: {conf})'

    def apostar(self, aposta, valor, casa, visitante):
        if valor <= 0 or valor > self.saldo:
            return False, "Valor inválido ou saldo insuficiente."
        if aposta not in ['Casa', 'Visitante', 'Empate']:
            return False, "Aposta inválida."
        if not (self.validar_carta(casa) and self.validar_carta(visitante)):
            return False, "Carta(s) inválida(s)."

        resultado = self.registrar_rodada(casa, visitante)
        ganho = 0
        if aposta == resultado:
            ganho = valor * 11 if resultado == 'Empate' else valor
            self.saldo += ganho
        else:
            self.saldo -= valor
        return True, (resultado, ganho, self.saldo)

    def mostrar_historico(self):
        if not self.historico:
            return ["Nenhuma rodada registrada."]
        linhas = []
        for i, (c, v, r) in enumerate(self.historico, 1):
            linhas.append(f"{i}: Casa {c} - Visitante {v} => Resultado: {r}")
        return linhas

# Streamlit interface
st.title("Football Studio Super Inteligente")

if 'jogo' not in st.session_state:
    st.session_state.jogo = FootballStudioSuperInteligente()

jogo = st.session_state.jogo

st.write(f"Saldo atual: {jogo.saldo}")

with st.form(key='aposta_form'):
    aposta = st.selectbox("Aposte em:", ["Casa", "Visitante", "Empate"])
    valor = st.number_input("Valor da aposta:", min_value=1, step=1)
    casa = st.text_input("Carta da Casa (2-10, J, Q, K, A):").upper()
    visitante = st.text_input("Carta do Visitante (2-10, J, Q, K, A):").upper()
    submit = st.form_submit_button("Registrar Aposta")

if submit:
    sucesso, resultado = jogo.apostar(aposta, valor, casa, visitante)
    if sucesso:
        res, ganho, saldo = resultado
        st.success(f"Resultado da rodada: {res}")
        if ganho > 0:
            st.success(f"Você ganhou {ganho} unidades!")
        else:
            st.warning(f"Você perdeu {valor} unidades.")
        st.write(f"Saldo atualizado: {saldo}")
    else:
        st.error(f"Erro: {resultado}")

st.subheader("Sugestão de Aposta")
st.write(jogo.sugerir_aposta())

st.subheader("Histórico das Rodadas")
historico = jogo.mostrar_historico()
for linha in historico:
    st.text(linha)
