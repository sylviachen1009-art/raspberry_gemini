# test.py 程式說明

## 這個程式是什麼？

這是一個 **Open WebUI 的 Filter（過濾器）插件**。
Filter 的作用是在使用者送出訊息給 AI 之前，或 AI 回應之後，插入自訂的處理邏輯。

---

## 整體架構

```
Filter 類別
├── Valves（系統管理員設定）
├── UserValves（一般使用者設定）
├── __init__（初始化）
├── inlet（進入前處理）
└── outlet（輸出後處理）
```

---

## 逐段說明

### 1. 模組標頭（檔案最上方的字串）

```python
"""
title: Example Filter
author: open-webui
version: 0.1
"""
```

這是插件的基本資訊，Open WebUI 會讀取這些欄位來顯示插件名稱、作者等。

---

### 2. 匯入套件

```python
from pydantic import BaseModel, Field
from typing import Optional
```

- `pydantic`：用來定義資料模型，並自動驗證欄位型別與預設值。
- `Optional`：表示某個參數可以是 `None`（可選的）。

---

### 3. Valves（系統管理員的設定閥）

```python
class Valves(BaseModel):
    priority: int = Field(default=0, ...)
    max_turns: int = Field(default=8, ...)
```

- 這是給**系統管理員**設定的參數。
- `priority`：這個 Filter 的執行優先順序，數字越小越先執行，預設為 `0`。
- `max_turns`：整個系統允許的最大對話輪數，預設為 `8`。
  - 例如：設為 8，代表一個對話最多來回 8 次。

---

### 4. UserValves（使用者自己的設定閥）

```python
class UserValves(BaseModel):
    max_turns: int = Field(default=4, ...)
```

- 這是給**一般使用者**自己設定的參數。
- `max_turns`：使用者自己設定的最大對話輪數，預設為 `4`。
- 最終生效的輪數會取 `UserValves.max_turns` 和 `Valves.max_turns` 兩者中**較小的值**，避免使用者繞過系統限制。

---

### 5. `__init__`（初始化方法）

```python
def __init__(self):
    self.valves = self.Valves()
```

- 當 Filter 被載入時自動執行。
- 建立一個 `Valves` 實例，套用預設的系統設定。
- 被註解掉的 `self.file_handler = True` 是一個選用旗標，啟用後可以讓這個 Filter 自行處理檔案上傳邏輯，而不走 WebUI 的預設流程。

---

### 6. `inlet`（入口處理 — 訊息送出前）

```python
def inlet(self, body: dict, __user__: Optional[dict] = None) -> dict:
```

- **觸發時機**：使用者按下送出，訊息還沒傳給 AI 之前。
- **用途**：可以在這裡檢查、修改、或拒絕請求。

#### 邏輯說明：

```python
if __user__.get("role", "admin") in ["user", "admin"]:
```
只對角色是 `user` 或 `admin` 的人套用限制。

```python
messages = body.get("messages", [])
max_turns = min(__user__["valves"].max_turns, self.valves.max_turns)
```
取出目前的對話訊息列表，並計算實際允許的最大輪數（取使用者設定和系統設定的最小值）。

```python
if len(messages) > max_turns:
    raise Exception(f"Conversation turn limit exceeded. Max turns: {max_turns}")
```
如果對話訊息數量超過限制，就拋出錯誤，阻止這次請求繼續送出。

---

### 7. `outlet`（出口處理 — AI 回應後）

```python
def outlet(self, body: dict, __user__: Optional[dict] = None) -> dict:
```

- **觸發時機**：AI 回應完成後，結果回傳給使用者之前。
- **用途**：可以在這裡修改 AI 的回應內容，或做記錄分析。
- 目前這個範例只有印出 log，沒有修改任何內容，直接回傳原始 `body`。

---

## 資料流程圖

```
使用者輸入訊息
      ↓
  [ inlet ]  ← 在這裡檢查對話輪數，超過就擋下來
      ↓
   AI 處理
      ↓
  [ outlet ] ← 在這裡可以修改或記錄 AI 的回應
      ↓
使用者看到回應
```

---

## 重點總結

| 項目 | 說明 |
|------|------|
| `Valves.max_turns` | 系統層級的對話上限（預設 8） |
| `UserValves.max_turns` | 使用者層級的對話上限（預設 4） |
| 實際上限 | 取兩者的最小值，防止使用者超出系統限制 |
| `inlet` | 訊息送出前的守門員 |
| `outlet` | AI 回應後的後處理器 |
