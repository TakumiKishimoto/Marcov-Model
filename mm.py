from collections import defaultdict
import random
from gtts import gTTS
import os
import platform
import subprocess
import time

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
    filename = f"output_{len(text)}.mp3"
    tts = gTTS(text=text, lang=lang)
    tts.save(filename)
    print(f"音声ファイルを {filename} として保存しました。")
    
    if platform.system() == 'Darwin':  # MacOS
        print(f"afplay {filename} コマンドを実行します。")
        subprocess.run(["afplay", filename])
    else:
        print("MacOS以外のシステムでは、保存された音声ファイルを手動で再生してください。")
    
    os.remove(filename)
    print(f"音声ファイル {filename} を削除しました。")

# 入力テキスト
text = "しかのこのこのここしたんたん"

# マルコフモデルの作成
model = create_markov_model(text)

# 遷移確率の計算
probabilities = calculate_transition_probabilities(model)

print("マルコフモデルに基づく遷移確率:")
for char, transitions in probabilities.items():
    print(f"遷移元: '{char}'")
    for next_char, prob in transitions.items():
        print(f"  → '{next_char}': {prob:.2f}")
    print()

print("\nテキスト生成と読み上げを開始します。プログラムを終了するには Ctrl+C を押してください。")

try:
    while True:
        # テキスト生成
        start_char = 'し'  # 開始文字を'し'に設定
        generated_text = generate_text(probabilities, start_char)
        print(f"\n生成されたテキスト: {generated_text}")

        # 生成されたテキストを読み上げ
        print("生成されたテキストを読み上げています...")
        text_to_speech(generated_text)

        # 次の生成までの待機時間
        # time.sleep(1)  # 5秒待機

except KeyboardInterrupt:
    print("\nプログラムを終了します。")

print("プログラムが終了しました。")