# 🎮 ChatDev: Pygame 自動生成工廠 (AI Game Generator)

這是一個基於 **Multi-Agent (多智能體)** 架構的自動化遊戲開發系統。使用者只需輸入一句簡單的遊戲點子（例如："做一個 8 Ball Pool 撞球遊戲"），系統便會自動協調多個 AI 角色進行**設計、編碼、素材生成、測試與自動修復**，最終產出一個可執行的 Pygame 遊戲。

![Project Status](https://img.shields.io/badge/Status-Active-success)
![Python](https://img.shields.io/badge/Python-3.11%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)

---

## ✨ 核心特色 (Core Features)

本專案將軟體開發流程拆解為三條流水線，由不同的 AI 成員負責：

### 1. 🤖 三人協作架構 (The Trio Architecture)

* **Member 1 (Design)**: 擔任 CEO 與 CPO。負責分析使用者需求，產出詳細的 **GDD (遊戲設計文件)**。
* **Member 2 (Core)**: 擔任 Art Director 與 Programmer。負責定義**幾何美術素材 (JSON)**，並根據 GDD 生成 **Python 代碼** 與 **客製化測試腳本 (Fuzzer Logic)**。
* **Member 3 (QA & Testing)**: 擔任 QA Engineer。負責執行 **語法檢查**、**動態壓力測試 (Fuzzer)** 與 **邏輯審查**，並在發現錯誤時自動呼叫工程師修復。

### 2. 🔄 自動修復迴圈 (Auto-Fix Loop)

系統具備強大的自我修復能力，會依次通過三道關卡，確保生成的遊戲不僅能跑，還能玩：

1.  **Syntax Check**: 靜態檢查 Python 語法錯誤 (使用 `ast`)。
2.  **Runtime Fuzzing**: 注入「猴子測試機器人 (Monkey Bot)」，實際執行遊戲並隨機操作，捕捉 **Crash (如 ZeroDivisionError)**。
    * *技術亮點*: 使用 `SDL_AUDIODRIVER=dummy` 隔離音效干擾，精準捕捉 Python 錯誤。
3.  **Logic Review**: AI 閱讀代碼，檢查是否發生「按鍵沒反應」、「畫面未更新」等邏輯問題。

### 3. 🌐 支援多種 LLM 模型

內建適配層，支援切換不同的 AI 提供者：

* **OpenAI** (GPT-4o, GPT-3.5)
* **Groq** (Llama3, Mixtral - 極速生成)
* **Google Gemini**
* **Ollama** (本地端模型)
* **Mistral**

---

## 🛠️ 安裝與設置 (Installation)

### 1. 複製專案

```bash
git clone https://github.com/your-username/llm-game-generator.git
cd llm-game-generator
```

### 2. 安裝依賴套件

```bash
pip install -r requirements.txt
```

*主要依賴: `flask`, `pygame`, `openai`, `python-dotenv`, `google-generativeai`*

### 3. 設定環境變數 (.env)

請在專案根目錄建立 `.env` 檔案，並填入你的 API Key 還有要使用的 Model Name。

```ini
# .env 範例

# 至少需要設定一組 Key
OPENAI_API_KEY=sk-xxxxxx
# GROQ_API_KEY=gsk-xxxxxx
# GOOGLE_API_KEY=AIza-xxxxxx
# OLLAMA_API_KEY=xxxxxx
# MISTRAL_API_KEY=xxxxxx

# 只少需要設定一組 Model Name
OPENAI_MODEL_NAME=gpt-4o-mini
# ......

# 若使用 Ollama (本地)，加上 URL 設定
# OLLAMA_BASE_URL=http://localhost:11434/v1

# Flask 設定
SECRET_KEY=your-secret-key-here
```

---

## 🚀 使用教學 (Usage)

### 1. 啟動 Web 介面

執行主程式 `app.py`：

```bash
python app.py
```

### 2. 開始生成

1.  打開瀏覽器前往 `http://127.0.0.1:5000`。
2.  在側邊欄選擇 **LLM Provider** (如 OpenAI) 和 **Model Name** (如 gpt-4o-mini)。
3.  在輸入框輸入遊戲點子，例如：
    > "A platformer game where a red square jumps over spikes to reach the green door."
4.  點擊 **"Generate"**。

### 3. 查看結果與測試

系統會顯示生成過程的 Log：

* ✅ **GDD 生成**: 顯示遊戲規則。
* ✅ **Code 生成**: 顯示生成的 `main.py`。
* ✅ **測試報告**: 顯示 Fuzzer 壓力測試結果 (Attempt 1/3...)。
    * 如果有錯誤 (Crash)，系統會顯示「修復中...」並自動重試。
* 若成功，點擊 **"Launch Game"** 即可在本地端開啟遊戲視窗。

---

## 📂 專案結構 (Project Structure)

```text
llm-game-generator/
│
├── app.py                  # Flask Web 入口
├── config.py               # 環境變數與設定管理
├── requirements.txt
├── .env                    # API Keys (不須上傳)
│
├── src/
│   ├── utils.py            # LLM 呼叫統一介面 (OpenAI/Groq/Ollama...)
│   │
│   ├── design/             # [Member 1] 設計階段
│   │   ├── chains.py       # CEO/CPO 邏輯
│   │   └── prompts.py      # 設計相關 Prompts
│   │
│   ├── generation/         # [Member 2] 生成階段
│   │   ├── core.py         # 協調美術與程式生成
│   │   ├── asset_gen.py    # 產生 JSON 素材設定
│   │   ├── file_utils.py   # 檔案存取與 Regex 解析
│   │   ├── fuzzer.py       # ✨ 核心功能：代碼注入與壓力測試
│   │   └── prompts.py      # Programmer & Art Prompts
│   │
│   └── testing/            # [Member 3] 測試階段
│       ├── runner.py       # 靜態檢查與遊戲啟動器
│       ├── fixer.py        # 自動修復迴圈邏輯
│       └── prompts.py      # Reviewer/Fixer Prompts
│
└── output/                 # 生成結果目錄
    ├── main.py             # 最終遊戲代碼
    ├── main_fuzz_temp.py   # (暫存) 注入了測試機器人的代碼
    └── fuzz_logic.py       # 動態生成的測試腳本
```

---

## ⚙️ 進階技術細節 (Technical Details)

### Fuzzer (動態壓力測試)

為了避免生成的遊戲「一玩就崩潰」，我們實作了動態 Fuzzer：

1.  **生成測試腳本**: Member 2 在寫遊戲時，會根據 GDD 同步生成一份 `fuzz_logic.py`，描述該遊戲的合法操作（如：按空白鍵跳躍）。
2.  **代碼注入**: Member 3 使用 Regex 將測試邏輯注入到 `main.py` 的主迴圈中，並解決 Scope 變數遮蔽 (`UnboundLocalError`) 與縮排 (`IndentationError`) 問題。
3.  **隔離執行**: 使用 `subprocess` 與虛擬音效驅動 (`SDL_AUDIODRIVER=dummy`) 執行遊戲，過濾 ALSA 雜訊，精準捕捉 Python Runtime Error。

### 幾何美術系統 (Geometric Assets)

為了避免 AI 生成不存在的圖片路徑導致錯誤，本系統採用 **"No Image File"** 策略：

* Art Agent 輸出一份 **JSON** 規格表。
* Programmer Agent 使用 `pygame.draw.rect/circle` 根據 JSON 繪製角色。
* 這確保了 100% 的素材可用性，無需依賴 DALL-E 生成不穩定的圖片。

---

## ⚠️ 常見問題 (Troubleshooting)

**Q: 啟動遊戲時出現 `ALSA lib` 錯誤訊息？**
A: 這是 Linux/WSL 環境下的音效驅動警告，通常不影響遊戲運行。我們的 Fuzzer 會自動忽略這些雜訊。

**Q: 遊戲視窗一閃即逝？**
A: 檢查是否安裝了 `pygame`。如果是透過 WSL 執行，請確保你有安裝 XServer (如 VcXsrv) 來顯示 GUI。

**Q: Ollama 連線失敗？**
A: 請確保 Ollama 服務已啟動 (`ollama serve`)，且 `OLLAMA_BASE_URL` 設定正確 (預設為 `http://localhost:11434/v1`)。

---

## 🤝 貢獻 (Contributing)

歡迎提交 Pull Request！不管是新增 Prompt、支援更多 LLM，或是優化 Fuzzer 邏輯。

---

**Developed with ❤️ by the ChatDev Team**
