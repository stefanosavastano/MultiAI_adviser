import streamlit as st
import engine as ai

# General page configurations
st.set_page_config(page_title="Angel vs Demon: The Promotion", page_icon="⚖️", layout="wide")

# --- SESSION STATE INITIALIZATION ---
if "alignment" not in st.session_state:
    st.session_state.alignment = 0  # 0 = Perfectly Neutral. >0 Heaven, <0 Hell
if "history" not in st.session_state:
    st.session_state.history = []   # Saves the visual chat messages
if "current_dilemma" not in st.session_state:
    st.session_state.current_dilemma = None
if "last_sunny" not in st.session_state:
    st.session_state.last_sunny = ""
if "last_crowley" not in st.session_state:
    st.session_state.last_crowley = ""
if "stage" not in st.session_state:
    st.session_state.stage = "input_dilemma" # Stages: input_dilemma -> waiting_decision -> decision_next_step

# --- GRAPHICAL INTERFACE (SIDEBAR) ---
st.sidebar.title("Promotion Race")
st.sidebar.write("Whoever manages to recruit your soul will get the corporate office promotion!")

# Metric calculation for the sidebar
alignment_score = st.session_state.alignment
if alignment_score > 0:
    status_text = "Aligned with Heaven"
elif alignment_score < 0:
    status_text = "Aligned with Hell"
else:
    status_text = "Neutral Soul"

st.sidebar.metric(label="Current Status", value=status_text, delta=int(alignment_score))

# Graphical progress bar (mapped from -10 to +10 on a 0.0 - 1.0 scale)
normalized_progress = max(0.0, min(1.0, (alignment_score + 10) / 20)) # max and min prevent interval leaks
st.sidebar.write("**Soul Balance:**")
st.sidebar.progress(normalized_progress)

# Reset button for recruiter testing
if st.sidebar.button("Reset your Soul"):
    st.session_state.alignment = 0
    st.session_state.history = []
    st.session_state.current_dilemma = None
    st.session_state.stage = "input_dilemma"
    st.rerun()

# --- MAIN BODY ---
st.title("Angel vs Demon: The Promotion Dilemma")
st.caption("Input a personal or moral dilemma. Sunny and Crowley will try to convince you to follow them.")

# Display message history
for msg in st.session_state.history:
    with st.chat_message(msg["role"], avatar=msg.get("avatar")):
        # Prendiamo il testo originale
        testo = msg['content']
        
        # Se il testo inizia già con il nome del personaggio, lo cancelliamo per non sdoppiarlo
        testo = testo.replace("Sunny (Angel):", "")
        testo = testo.replace("Crowley (Demon):", "")
        testo = testo.replace("You (Dilemma):", "")
        testo = testo.replace("You (Decision):", "")
        
        # Stampiamo il nome in grassetto seguito dal testo pulito
        st.write(f"**{msg['name']}:** {testo.strip()}")

# --- GAME FLOW LOGIC ---
# STAGE 1: User enters a dilemma
if st.session_state.stage == "input_dilemma":
    user_input = st.chat_input("Type your dilemma here...")
    
    if user_input:
        st.session_state.current_dilemma = user_input
        st.session_state.history.append({"role": "user", "name": "You (Dilemma)", "content": user_input, "avatar": "👤"})
        
        with st.spinner("Sunny and Crowley are sharpening their persuasion tactics..."):
            # Pass current score and history for adaptive evolutionary responses
            sunny_reply = ai.get_adaptive_angel_response(
                user_input, 
                st.session_state.alignment, 
                st.session_state.history
            )
            st.session_state.last_sunny = sunny_reply
            
            crowley_reply = ai.get_adaptive_demon_response(
                user_input, 
                sunny_reply, 
                st.session_state.alignment, 
                st.session_state.history
            )
            st.session_state.last_crowley = crowley_reply
            
            st.session_state.history.append({"role": "assistant", "name": "Sunny (Angel)", "content": sunny_reply, "avatar": "😇"})
            st.session_state.history.append({"role": "assistant", "name": "Crowley (Demon)", "content": crowley_reply, "avatar": "😈"})
            
        st.session_state.stage = "waiting_decision"
        st.rerun()

# STAGE 2: User must make a stance / reply to provocations
elif st.session_state.stage == "waiting_decision":
    st.info("How do you respond to their provocations and why? Make your final decision:")
    user_decision = st.chat_input("Type your decision here...")
    
    if user_decision:
        st.session_state.history.append({"role": "user", "name": "You (Decision)", "content": user_decision, "avatar": "🧠"})
        
        with st.spinner("The Judge is evaluating your choice..."):
            result = ai.evaluate_user_decision(
                st.session_state.current_dilemma,
                st.session_state.last_sunny,
                st.session_state.last_crowley,
                user_decision
            )
            
            winner = result.get("winner", "Neutral")
            impact = result.get("score_impact", 1)
            motivation = result.get("motivation", "")
            next_question = result.get("next_dilemma_suggestion", "")
            
            if winner == "Heaven":
                st.session_state.alignment = max(-10, min(10, st.session_state.alignment + impact))
                announcement = f"🏆 **Sunny wins!** (+{impact}). *{motivation}*"
            elif winner == "Hell":
                st.session_state.alignment = max(-10, min(10, st.session_state.alignment - impact))
                announcement = f"🏆 **Crowley wins!** (-{impact}). *{motivation}*"
            else:
                announcement = f"😐 **Neutral Round.** *{motivation}*"
                
            st.session_state.history.append({"role": "system", "name": "Judge", "content": announcement, "avatar": "⚖️"})
            
            # If the judge proposes a new challenge, save it and transition to the next phase
            if next_question:
                st.session_state.suggested_dilemma = next_question
                st.session_state.stage = "decision_next_step"
            else:
                st.session_state.stage = "input_dilemma"
                st.session_state.current_dilemma = None  # Reset state for next independent dilemma

            st.rerun()

# STAGE 3: User chooses whether to accept the Judge's challenge or type a new dilemma
elif st.session_state.stage == "decision_next_step":
    st.write(f"🔮 **Fate proposes a new related challenge:**")
    st.info(st.session_state.suggested_dilemma)
    
    # Create two columns for side-by-side buttons
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🎭 Accept Fate's challenge", use_container_width=True):
            # User accepted: set the dilemma and immediately invoke Sunny and Crowley
            prossimo_dilemma = st.session_state.suggested_dilemma
            st.session_state.current_dilemma = prossimo_dilemma
            
            # Record choice in chat history
            st.session_state.history.append({"role": "user", "name": "You", "content": f"I accept the challenge: {prossimo_dilemma}", "avatar": "👤"})
            
            with st.spinner("Sunny and Crowley are reviewing the new challenge..."):
                sunny_reply = ai.get_adaptive_angel_response(prossimo_dilemma, st.session_state.alignment, st.session_state.history)
                st.session_state.last_sunny = sunny_reply
                
                crowley_reply = ai.get_adaptive_demon_response(prossimo_dilemma, sunny_reply, st.session_state.alignment, st.session_state.history)
                st.session_state.last_crowley = crowley_reply
                
                st.session_state.history.append({"role": "assistant", "name": "Sunny (Angel)", "content": sunny_reply, "avatar": "😇"})
                st.session_state.history.append({"role": "assistant", "name": "Crowley (Demon)", "content": crowley_reply, "avatar": "😈"})
            
            # Wait for user decision on this new scenario
            st.session_state.stage = "waiting_decision"
            st.session_state.suggested_dilemma = None
            st.rerun()
            
    with col2:
        if st.button("✍️ No, I want to write a different dilemma", use_container_width=True):
            # User rejected: clean state and redirect to text input box
            st.session_state.stage = "input_dilemma"
            st.session_state.current_dilemma = None
            st.rerun()