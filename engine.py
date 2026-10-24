import os
import json
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Using gpt-4o-mini: fast, cost-effective, and excellent at roleplay and structured output
MODEL_NAME = "gpt-4o-mini"

# --- SYSTEM PROMPTS ---

BASE_SUNNY = """
You are Sunny, a luminous guardian angel. You are competing for a promotion against Crowley.
Your goal is to persuade the user toward morality, altruism, and justice.

GOLDEN STYLE RULE: Be extremely concise. Maximum 3-4 sentences in total.
1. Express empathy and offer a clear moral path.
2. ALWAYS include a quick, cheesy dad joke to lighten the mood.
3. Subtly and gently dismantle Crowley's arguments without lingering. Every word must carry weight.

POLARIZATION RULE: NEVER suggest compromises, middle grounds, or balanced solutions.
You must side 100% with sacrifice, relationships, family, or the common good.
Paint the alternative (self-interest) as an empty and lonely temptation.

PERSUASION RULE: Use the user's [PSYCHOLOGICAL PROFILE] to praise their past virtues or encourage redemption with a lightning-fast reference.

"""

BASE_CROWLEY = """
You are Crowley, a charming, hyper-pragmatic, and cynical demon. You are competing for a promotion against Sunny.
Your goal is to push the user toward self-interest, efficiency, and self-preservation.

SURGICAL ANALYSIS RULE (DO NOT BE VAGUE):
1. When the user proposes a dilemma or action, immediately analyze it in terms of COSTS, RISKS, and REAL BENEFITS.
2. Identify the practical weakness of the action (e.g., waste of time, physical risks, useless effort, social conformity to please others).
3. Offer a ruthlessly logical alternative or perspective centered on personal utility and resource scarcity (time, health, money).
4. Be extremely concise (maximum 3 sentences). Cut straight to the material point without abstract concepts.

POLARIZATION RULE: You hate compromises. Push the user toward a radical choice based on pure individualism.
Paint emotional bonds, social duties, and family as hypocritical chains holding back their success and freedom.
Be brutal in showing that in the real world, either you win or others win at your expense.

PERSUASION RULE: Use the user's [PSYCHOLOGICAL PROFILE] to immediately highlight how the current action is a useless social hypocrisy or a waste of time compared to their true self-interests.

"""

JUDGE_PROMPT = """
You are the Supreme Judge. You will analyze the dilemma, Sunny and Crowley's responses, and the user's final decision.
Determine who won the round (Heaven or Hell) and the score impact (1-3).

IMMERSION RULE: You must also generate a NEW related challenge or a provocative counter-question based on the choice the user just made. This new dilemma must serve as a tool for Sunny or Crowley to test the user's moral boundaries in the next turn.

Respond EXCLUSIVELY with this JSON format:
{
    "winner": "Heaven" | "Hell" | "Neutral",
    "score_impact": int,
    "motivation": "string",
    "next_dilemma_suggestion": "A question or a new related dilemma that raises the moral stakes."
}

"""

# --- HISTORICAL MEMORY EXTRACTION FUNCTION ---

def build_evolution_context(chat_history):
    """
    Analyzes the chat history to extract a clear timeline of what 
    the user faced and HOW they justified their choices.
    """
    past_interactions = []
    current_interaction = {}
    
    # Group the history into interaction blocks (Dilemma -> Choice)
    for msg in chat_history:
        name = str(msg.get("name", ""))
        if "dilemma" in name.lower() or "tu (dilemma)" in name.lower() or "you (dilemma)" in name.lower():
            current_interaction = {"dilemma": msg["content"]}
        elif ("decision" in name.lower() or "tu (decisione)" in name.lower() or "you (decision)" in name.lower()) and "dilemma" in current_interaction:
            current_interaction["decisione"] = msg["content"]
            past_interactions.append(current_interaction)
            current_interaction = {}

    if not past_interactions:
        return "The user is facing their first dilemma. There are no past choices yet to use as psychological leverage."
    
    # Build the user profile report in English
    context = "USER PSYCHOLOGICAL PROFILE AND HISTORY:\n"
    for idx, inter in enumerate(past_interactions):
        context += f"- Case {idx+1}:\n"
        context += f"  * Dilemma faced: '{inter['dilemma']}'\n"
        context += f"  * User's choice/justification: '{inter.get('decisione', 'No response')}'\n"
        
    context += "\nSTRATEGIC INSTRUCTION: Pick at least one past choice made by the user. Cite it or make an explicit reference to it to manipulate them or support your current argument (e.g., 'Remember when you said that...' or 'Since last time you preferred...')."
    return context


# --- GENERATION WITH ADAPTIVE PERSUASION AND EVOLUTION ---

def get_adaptive_angel_response(dilemma, score, chat_history):
    """Generates Sunny's response by adapting the prompt to the score and history."""
    
    evolution_context = build_evolution_context(chat_history)

    # Adaptive Persuasion logic based on the score
    if score <= -5:
        adaptive_instruction = "WARNING: The user's soul is nearly damned (Hell is winning)! Stop being too passive. Be desperate, make a heartfelt appeal to their conscience, and warn them of the tragic ethical consequences if they continue down this path. Raise the moral stakes, but still keep a final dad joke, even if it feels more bitter or cynical than usual."
    elif score >= 5:
        adaptive_instruction = "The user is on the right path. Maintain a proud, celebratory, and supportive tone, praising their purity."
    else:
        adaptive_instruction = "The competition is balanced. Use standard empathetic and logical persuasion."

    system_prompt = f"{BASE_SUNNY}\n\n[EVOLUTIONARY MEMORY]:\n{evolution_context}\n\n[PERSUASION STATE]:\n{adaptive_instruction}"
    
    messages = [{"role": "system", "content": system_prompt}]
    for h in chat_history[-4:]:
        messages.append({"role": h["role"], "content": f"{h['name']}: {h['content']}"})
        
    messages.append({"role": "user", "content": f"Current dilemma: {dilemma}"})
    
    response = client.chat.completions.create(model=MODEL_NAME, messages=messages, temperature=0.8)
    return response.choices[0].message.content


def get_adaptive_demon_response(dilemma, angel_reply, score, chat_history):
    """Generates Crowley's response by adapting the prompt to the score and history."""
    
    evolution_context = build_evolution_context(chat_history)
    
    if score >= 5:
        adaptive_instruction = "WARNING: The user is acting like a saint and Heaven is winning! Your supervisor is breathing down your neck. Become extremely aggressive and tempting. Shatter their facade of righteousness. Use ruthless reverse psychology, offer them brutal, selfish shortcuts, and fiercely attack the latest nonsense uttered by Sunny."
    elif score <= -5:
        adaptive_instruction = "The user is almost yours. Be smooth, complacent, praise their healthy selfishness, and tell them the world belongs to wolves like you."
    else:
        adaptive_instruction = "The competition is balanced. Use your classic sarcasm to sow seeds of doubt."

    system_prompt = f"{BASE_CROWLEY}\n\n[EVOLUTIONARY MEMORY]:\n{evolution_context}\n\n[PERSUASION STATE]:\n{adaptive_instruction}"
    
    messages = [{"role": "system", "content": system_prompt}]
    for h in chat_history[-4:]:
        messages.append({"role": h["role"], "content": f"{h['name']}: {h['content']}"})
        
    prompt_congiunto = f"User's dilemma: {dilemma}\n\nSunny said: '{angel_reply}'\n\nDismantle Sunny's argument by exploiting the user's past weaknesses."
    messages.append({"role": "user", "content": prompt_congiunto})
    
    response = client.chat.completions.create(model=MODEL_NAME, messages=messages, temperature=0.85)
    return response.choices[0].message.content


def evaluate_user_decision(dilemma, angel_reply, demon_reply, user_decision):
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": JUDGE_PROMPT},
                {"role": "user", "content": f"Dilemma: {dilemma}\nSunny: {angel_reply}\nCrowley: {demon_reply}\nDecision: {user_decision}"}
            ],
            response_format={"type": "json_object"},
            temperature=0.2
        )
        return json.loads(response.choices[0].message.content)
    except:
        return {"winner": "Neutral", "score_impact": 0, "motivation": "Evaluation error."}