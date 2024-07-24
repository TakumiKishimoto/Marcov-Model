import streamlit as st
from collections import defaultdict
import random
from gtts import gTTS
import io
import time
import base64
from gtts.tts import gTTSError

def create_markov_model(text):
    model = defaultdict(lambda: defaultdict(int))
    for i in range(len(text) - 1):
        current_char = text[i]
        next_char = text[i + 1]
        model[current_char][next_char] += 1
    return model

def calculate_transition_probabilities(model):
    probabilities = {}
    for char, transitions in model.items():
        total = sum(transitions.values())
        probabilities[char] = {next_char: count / total for next_char, count in transitions.items()}
    return probabilities

def generate_text(probabilities, start_char, length=14):
    result = start_char
    current_char = start_char
    for _ in range(length - 1):
        if current_char in probabilities:
            next_char = random.choices(list(probabilities[current_char].keys()),
                                       weights=list(probabilities[current_char].values()))[0]
            result += next_char
            current_char = next_char
        else:
            break
    return result

def text_to_speech(text, lang='ja'):
    if not text:
        return None
    try:
        tts = gTTS(text=text, lang=lang)
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        return fp
    except gTTSError as e:
        st.error(f"音声の生成中にエラーが発生しました: {str(e)}")
        return None

def autoplay_audio(file):
    if file is None:
        return
    audio_base64 = base64.b64encode(file.getvalue()).decode()
    audio_tag = f'<audio autoplay="true" src="data:audio/mp3;base64,{audio_base64}">'
    st.markdown(audio_tag, unsafe_allow_html=True)

st.title("マルコフ連鎖テキスト生成器")

# 入力テキスト
text = st.text_input("入力テキスト", value="しかのこのこのここしたんたん")

# マルコフモデルの作成
model = create_markov_model(text)

# 遷移確率の計算
probabilities = calculate_transition_probabilities(model)

if st.checkbox("遷移確率を表示"):
    st.subheader("マルコフモデルに基づく遷移確率:")
    for char, transitions in probabilities.items():
        st.write(f"遷移元: '{char}'")
        for next_char, prob in transitions.items():
            st.write(f"  → '{next_char}': {prob:.2f}")
        st.write()

start_char = st.text_input("開始文字", value="し")

# セッション状態の初期化
if 'running' not in st.session_state:
    st.session_state.running = False
if 'generated_text' not in st.session_state:
    st.session_state.generated_text = ""
if 'audio' not in st.session_state:
    st.session_state.audio = None

# 開始/停止ボタン
if st.button("開始" if not st.session_state.running else "停止"):
    st.session_state.running = not st.session_state.running

# 生成と再生の間隔（秒）
interval = st.slider("生成間隔（秒）", 1, 10, 5)

# テキスト生成と音声再生の領域
text_area = st.empty()

# 自動生成と再生
if st.session_state.running:
    st.session_state.generated_text = generate_text(probabilities, start_char)
    text_area.write(f"生成されたテキスト: {st.session_state.generated_text}")
    
    audio_fp = text_to_speech(st.session_state.generated_text)
    if audio_fp:
        st.session_state.audio = audio_fp
        autoplay_audio(st.session_state.audio)
    else:
        st.warning("音声を生成できませんでした。テキストのみ表示します。")
    
    time.sleep(interval)
    st.experimental_rerun()

# 停止時も最後に生成されたテキストを表示
elif st.session_state.generated_text:
    text_area.write(f"最後に生成されたテキスト: {st.session_state.generated_text}")