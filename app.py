import streamlit as st
import sqlite3
from datetime import datetime, timedelta

# --- Configuração do Banco de Dados SQLite ---
DB_NAME = 'medicacao_pet.db'

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    # Tabela para armazenar as doses de medicação e seu status
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS doses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data TEXT NOT NULL,
            horario TEXT NOT NULL,
            medicamento TEXT NOT NULL,
            dosagem TEXT NOT NULL,
            observacao_geral TEXT,
            administrado BOOLEAN NOT NULL DEFAULT 0,
            observacao_dose TEXT,
            -- Adicionando uma restrição UNIQUE para evitar duplicatas de doses na mesma data/horário/medicamento
            UNIQUE(data, horario, medicamento, dosagem)
        )
    ''')
    conn.commit()
    conn.close()

# --- Funções para interagir com o Banco de Dados ---
def add_dose(data, horario, medicamento, dosagem):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO doses (data, horario, medicamento, dosagem) VALUES (?, ?, ?, ?)",
                       (data, horario, medicamento, dosagem))
        conn.commit()
    except sqlite3.IntegrityError:
        # Esta exceção será levantada se a restrição UNIQUE for violada (dose já existe)
        pass # Ignora a inserção se a dose já existe
    finally:
        conn.close()

def get_doses_by_date(date_str):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, horario, medicamento, dosagem, administrado, observacao_dose FROM doses WHERE data = ? ORDER BY horario", (date_str,))
    doses = cursor.fetchall()
    conn.close()
    return doses

def update_dose_status(dose_id, status):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("UPDATE doses SET administrado = ? WHERE id = ?", (status, dose_id))
    conn.commit()
    conn.close()

def update_daily_observation(date_str, obs_geral):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    # Atualiza a observação geral para qualquer dose existente naquele dia
    cursor.execute("UPDATE doses SET observacao_geral = ? WHERE data = ?", (obs_geral, date_str))
    conn.commit()
    # Se nenhuma linha foi afetada, significa que não havia doses para aquele dia,
    # então insere uma dose "fictícia" apenas para armazenar a observação geral.
    if cursor.rowcount == 0:
        try:
            cursor.execute("INSERT INTO doses (data, horario, medicamento, dosagem, observacao_geral) VALUES (?, ?, ?, ?, ?)", (date_str, '00:00', 'OBS_DIARIA_FICTICIA', '0', obs_geral))
            conn.commit()
        except sqlite3.IntegrityError:
            pass # Se por algum motivo a dose fictícia já existe, ignora
    conn.close()


def get_daily_observation(date_str):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    # Pega a observação geral de qualquer dose para aquele dia
    cursor.execute("SELECT observacao_geral FROM doses WHERE data = ? AND observacao_geral IS NOT NULL LIMIT 1", (date_str,))
    obs = cursor.fetchone()
    conn.close()
    return obs[0] if obs else ""

def update_dose_observation(dose_id, obs_dose):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("UPDATE doses SET observacao_dose = ? WHERE id = ?", (obs_dose, dose_id))
    conn.commit()
    conn.close()

# --- Dados da sua prescrição (Adaptados para a estrutura do banco) ---
# Usaremos 'DD/MM/YYYY' como formato de data para exibir e para o banco.
# Os horários devem ser em formato 'HH:MM'.

MEDICAMENTOS = {
    "26/07/2025": [
        {"horario": "14:00", "nome": "Diprona 1g", "dosagem": "1 comprimido"},
        {"horario": "18:00", "nome": "Seclac", "dosagem": "2 comprimidos"},
        {"horario": "22:00", "nome": "Metronidazol 400mg", "dosagem": "1 e 1/2 comprimido"},
        {"horario": "22:00", "nome": "Amoxicilina 500mg + clavulanato de potássio 125mg", "dosagem": "1 cápsula"}
    ],
    "27/07/2025": [
        {"horario": "07:30", "nome": "Gaviz 20mg", "dosagem": "2 comprimidos", "obs": "Manhã (em jejum) - Aguardar 30 minutos para alimentar e dar outras medicações."},
        {"horario": "08:00", "nome": "Mellis Vet 4mg", "dosagem": "1 comprimido", "obs": "APÓS SE ALIMENTAR"},
        {"horario": "08:45", "nome": "Cloridrato de tramadol 100mg", "dosagem": "1 comprimido"},
        {"horario": "10:00", "nome": "Metronidazol 400mg", "dosagem": "1 e 1/2 comprimido"},
        {"horario": "10:00", "nome": "Amoxicilina 500mg + clavulanato de potássio 125mg", "dosagem": "1 cápsula"},
        {"horario": "14:00", "nome": "Diprona 1g", "dosagem": "1 comprimido"},
        {"horario": "18:00", "nome": "Seclac", "dosagem": "2 comprimidos"},
        {"horario": "20:45", "nome": "Cloridrato de tramadol 100mg", "dosagem": "1 comprimido"},
        {"horario": "22:00", "nome": "Metronidazol 400mg", "dosagem": "1 e 1/2 comprimido"},
        {"horario": "22:00", "nome": "Amoxicilina 500mg + clavulanato de potássio 125mg", "dosagem": "1 cápsula"}
    ],
    "28/07/2025": [
        {"horario": "07:30", "nome": "Gaviz 20mg", "dosagem": "2 comprimidos", "obs": "Manhã (em jejum) - Aguardar 30 minutos para alimentar e dar outras medicações."},
        {"horario": "08:00", "nome": "Mellis Vet 4mg", "dosagem": "1 comprimido", "obs": "APÓS SE ALIMENTAR"},
        {"horario": "08:45", "nome": "Cloridrato de tramadol 100mg", "dosagem": "1 comprimido"},
        {"horario": "10:00", "nome": "Metronidazol 400mg", "dosagem": "1 e 1/2 comprimido"},
        {"horario": "10:00", "nome": "Amoxicilina 500mg + clavulanato de potássio 125mg", "dosagem": "1 cápsula"},
        {"horario": "14:00", "nome": "Diprona 1g", "dosagem": "1 comprimido"},
        {"horario": "18:00", "nome": "Seclac", "dosagem": "2 comprimidos"},
        {"horario": "20:45", "nome": "Cloridrato de tramadol 100mg", "dosagem": "1 comprimido"},
        {"horario": "22:00", "nome": "Metronidazol 400mg", "dosagem": "1 e 1/2 comprimido"},
        {"horario": "22:00", "nome": "Amoxicilina 500mg + clavulanato de potássio 125mg", "dosagem": "1 cápsula"}
    ],
    "29/07/2025": [
        {"horario": "07:30", "nome": "Gaviz 20mg", "dosagem": "2 comprimidos", "obs": "Manhã (em jejum) - Aguardar 30 minutos para alimentar e dar outras medicações."},
        {"horario": "08:00", "nome": "Mellis Vet 4mg", "dosagem": "1 comprimido", "obs": "APÓS SE ALIMENTAR"},
        {"horario": "08:45", "nome": "Cloridrato de tramadol 100mg", "dosagem": "1 comprimido"},
        {"horario": "10:00", "nome": "Metronidazol 400mg", "dosagem": "1 e 1/2 comprimido"},
        {"horario": "10:00", "nome": "Amoxicilina 500mg + clavulanato de potássio 125mg", "dosagem": "1 cápsula"},
        {"horario": "14:00", "nome": "Diprona 1g", "dosagem": "1 comprimido", "obs": "Última dose"},
        {"horario": "18:00", "nome": "Seclac", "dosagem": "2 comprimidos"},
        {"horario": "20:45", "nome": "Cloridrato de tramadol 100mg", "dosagem": "1 comprimido"},
        {"horario": "22:00", "nome": "Metronidazol 400mg", "dosagem": "1 e 1/2 comprimido"},
        {"horario": "22:00", "nome": "Amoxicilina 500mg + clavulanato de potássio 125mg", "dosagem": "1 cápsula"}
    ],
    "30/07/2025": [
        {"horario": "07:30", "nome": "Gaviz 20mg", "dosagem": "2 comprimidos", "obs": "Manhã (em jejum) - Aguardar 30 minutos para alimentar e dar outras medicações."},
        {"horario": "08:00", "nome": "Mellis Vet 4mg", "dosagem": "1 comprimido", "obs": "APÓS SE ALIMENTAR - Última dose"},
        {"horario": "08:45", "nome": "Cloridrato de tramadol 100mg", "dosagem": "1 comprimido", "obs": "Última dose"},
        {"horario": "10:00", "nome": "Metronidazol 400mg", "dosagem": "1 e 1/2 comprimido"},
        {"horario": "10:00", "nome": "Amoxicilina 500mg + clavulanato de potássio 125mg", "dosagem": "1 cápsula"},
        {"horario": "18:00", "nome": "Seclac", "dosagem": "2 comprimidos"},
        {"horario": "22:00", "nome": "Metronidazol 400mg", "dosagem": "1 e 1/2 comprimido"},
        {"horario": "22:00", "nome": "Amoxicilina 500mg + clavulanato de potássio 125mg", "dosagem": "1 cápsula"}
    ],
    "31/07/2025": [
        {"horario": "07:30", "nome": "Gaviz 20mg", "dosagem": "2 comprimidos", "obs": "Manhã (em jejum) - Aguardar 30 minutos para alimentar e dar outras medicações."},
        {"horario": "10:00", "nome": "Metronidazol 400mg", "dosagem": "1 e 1/2 comprimido"},
        {"horario": "10:00", "nome": "Amoxicilina 500mg + clavulanato de potássio 125mg", "dosagem": "1 cápsula"},
        {"horario": "18:00", "nome": "Seclac", "dosagem": "2 comprimidos"},
        {"horario": "22:00", "nome": "Metronidazol 400mg", "dosagem": "1 e 1/2 comprimido"},
        {"horario": "22:00", "nome": "Amoxicilina 500mg + clavulanato de potássio 125mg", "dosagem": "1 cápsula"}
    ],
    "01/08/2025": [
        {"horario": "07:30", "nome": "Gaviz 20mg", "dosagem": "2 comprimidos", "obs": "Manhã (em jejum) - Aguardar 30 minutos para alimentar e dar outras medicações."},
        {"horario": "10:00", "nome": "Metronidazol 400mg", "dosagem": "1 e 1/2 comprimido", "obs": "Última dose"},
        {"horario": "10:00", "nome": "Amoxicilina 500mg + clavulanato de potássio 125mg", "dosagem": "1 cápsula"},
        {"horario": "18:00", "nome": "Seclac", "dosagem": "2 comprimidos"},
        {"horario": "22:00", "nome": "Amoxicilina 500mg + clavulanato de potássio 125mg", "dosagem": "1 cápsula"}
    ],
    "02/08/2025": [
        {"horario": "07:30", "nome": "Gaviz 20mg", "dosagem": "2 comprimidos", "obs": "Manhã (em jejum) - Aguardar 30 minutos para alimentar e dar outras medicações."},
        {"horario": "10:00", "nome": "Amoxicilina 500mg + clavulanato de potássio 125mg", "dosagem": "1 cápsula"},
        {"horario": "18:00", "nome": "Seclac", "dosagem": "2 comprimidos"},
        {"horario": "22:00", "nome": "Amoxicilina 500mg + clavulanato de potássio 125mg", "dosagem": "1 cápsula"}
    ],
    "03/08/2025": [
        {"horario": "07:30", "nome": "Gaviz 20mg", "dosagem": "2 comprimidos", "obs": "Manhã (em jejum) - Aguardar 30 minutos para alimentar e dar outras medicações."},
        {"horario": "10:00", "nome": "Amoxicilina 500mg + clavulanato de potássio 125mg", "dosagem": "1 cápsula"},
        {"horario": "18:00", "nome": "Seclac", "dosagem": "2 comprimidos"},
        {"horario": "22:00", "nome": "Amoxicilina 500mg + clavulanato de potássio 125mg", "dosagem": "1 cápsula"}
    ],
    "04/08/2025": [
        {"horario": "07:30", "nome": "Gaviz 20mg", "dosagem": "2 comprimidos", "obs": "Última dose - Manhã (em jejum) - Aguardar 30 minutos para alimentar e dar outras medicações."},
        {"horario": "10:00", "nome": "Amoxicilina 500mg + clavulanato de potássio 125mg", "dosagem": "1 cápsula"},
        {"horario": "18:00", "nome": "Seclac", "dosagem": "2 comprimidos"},
        {"horario": "22:00", "nome": "Amoxicilina 500mg + clavulanato de potássio 125mg", "dosagem": "1 cápsula", "obs": "Última dose"}
    ]
}


# --- Inicialização do Streamlit App ---
st.set_page_config(layout="wide")
st.title("🐾 Agenda de Medicação da Nala 🐾")

# Inicializa o banco de dados e popula com dados se estiver vazio
init_db() # Garante que a tabela está criada

# Para cada dia na sua lista de medicamentos de prescrição
for date_str, meds in MEDICAMENTOS.items():
    for med in meds:
        # Tenta adicionar a dose. Se já existir (devido à restrição UNIQUE), será ignorado.
        add_dose(date_str, med["horario"], med["nome"], med["dosagem"])


# --- Lógica para navegação entre dias ---
today = datetime.now()
if 'current_date' not in st.session_state:
    st.session_state.current_date = today

col1, col2, col3 = st.columns([1, 2, 1])
with col1:
    if st.button("⬅️ Dia Anterior"):
        st.session_state.current_date -= timedelta(days=1)
with col2:
    st.markdown(f"<h3 style='text-align: center;'>{st.session_state.current_date.strftime('%d/%m/%Y')}</h3>", unsafe_allow_html=True)
with col3:
    if st.button("Dia Seguinte ➡️"):
        st.session_state.current_date += timedelta(days=1)
if st.button("Voltar para Hoje"):
    st.session_state.current_date = today

current_date_str_db = st.session_state.current_date.strftime('%d/%m/%Y') # Formato para consulta no DB

# --- Exibir a agenda do dia atual ---
st.header("Medicamentos do Dia:")

# Exibir Observação Geral do Dia
obs_geral_dia = get_daily_observation(current_date_str_db)
nova_obs_geral = st.text_area("Observações Gerais do Dia:", value=obs_geral_dia, key=f"obs_geral_{current_date_str_db}")
if nova_obs_geral != obs_geral_dia:
    update_daily_observation(current_date_str_db, nova_obs_geral)
    st.experimental_rerun() # Recarrega para mostrar a observação atualizada

doses_do_dia = get_doses_by_date(current_date_str_db)

if not doses_do_dia:
    st.info("Nenhuma medicação agendada para este dia.")
else:
    # Ordenar as doses por horário para exibir corretamente
    # Filtra doses "fictícias" de OBS_DIARIA_FICTICIA, se houver, para não mostrar na lista de meds
    doses_para_exibir = [d for d in doses_do_dia if d[2] != 'OBS_DIARIA_FICTICIA']
    doses_do_dia_ordenadas = sorted(doses_para_exibir, key=lambda x: datetime.strptime(x[1], '%H:%M').time())

    for dose in doses_do_dia_ordenadas:
        dose_id, horario, medicamento, dosagem, administrado, observacao_dose = dose

        # Destacar a próxima dose
        is_next_dose = False
        current_time = datetime.now().strftime('%H:%M')
        # Comparar apenas se for o dia atual e o horário for no futuro e ainda não administrado
        if st.session_state.current_date.date() == today.date() and \
           datetime.strptime(horario, '%H:%M').time() > datetime.strptime(current_time, '%H:%M').time() and \
           not administrado:
             is_next_dose = True

        col_horario, col_med, col_status, col_btn, col_obs = st.columns([0.8, 2, 1, 1, 2])

        with col_horario:
            # CORRIGIDO: styler para style AQUI
            st.markdown(f"**{'<span style=\"color: #28a745;\">' if is_next_dose else ''}{horario}{'</span>' if is_next_dose else ''}**", unsafe_allow_html=True)
        with col_med:
            # REMOVIDO: a tag <span> do medicamento e dosagem para evitar a exibição literal
            st.markdown(f"**{medicamento} - {dosagem}**") # Apenas texto simples em negrito

            # Adicionar observações específicas da prescrição, se houver
            original_obs = ""
            # Procura a observação na estrutura MEDICAMENTOS (nossa "receita" estática)
            for med_data in MEDICAMENTOS.get(current_date_str_db, []):
                if med_data["horario"] == horario and med_data["nome"] == medicamento:
                    original_obs = med_data.get("obs", "")
                    break
            if original_obs:
                st.info(f"*(Obs. Prescrição: {original_obs})*")


        with col_status:
            if administrado:
                st.success("✅ Administrado")
            else:
                st.warning("⏳ Pendente")

        with col_btn:
            # Somente mostra o botão se não estiver administrado
            if not administrado:
                if st.button("Marcar como administrado", key=f"btn_{dose_id}"):
                    update_dose_status(dose_id, True)
                    st.experimental_rerun() # Recarregar a página para atualizar o status
            else:
                # Opção de "desmarcar" caso tenha marcado errado
                if st.button("Desmarcar", key=f"btn_desmarcar_{dose_id}"):
                    update_dose_status(dose_id, False)
                    st.experimental_rerun()


        with col_obs:
            nova_obs_dose = st.text_input("Observação da dose:", value=observacao_dose if observacao_dose else "", key=f"obs_dose_{dose_id}")
            if nova_obs_dose != (observacao_dose if observacao_dose else ""):
                update_dose_observation(dose_id, nova_obs_dose)
                st.experimental_rerun() # Recarrega para mostrar a observação atualizada

        st.markdown("---") # Linha divisória para separar as doses

st.markdown("---")
st.write("Desenvolvido com ❤️ para a Nalinha!")
