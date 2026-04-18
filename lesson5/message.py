
"""
title: 基礎 Action 範例
author: YourName
version: 1.0
"""
from typing import Optional, Callable, Any

class Action:
    def __init__(self):
        pass

    async def action(
        self,
        body: dict,
        __user__: Optional[dict] = None,
        __event_emitter__: Optional[Callable[..., Any]] = None,
    ) -> Optional[dict]:
        
        # 取得所有對話
        messages = body.get("messages", [])
        if not messages:
            return body

        # 取得最後點擊欲處理的那則訊息
        last_message = messages[-1]
        message_content = last_message.get("content", "")
        message_len = len(message_content)

        # ⚠️ 由於目前前端接收 Action 的 SSE 串流時易發生 JSON 解析錯誤
        # 最穩定相容的做法是直接將結果附加在對話內容中並回傳 body
        last_message["content"] += f"\n\n*(系統分析：這則訊息的長度是 {message_len} 個字)*"

        # 回傳變更後的 body 讓前端更新畫面
        return body

這段程式是一個「最小可運作的 Action 範例」，核心功能其實很單純：讀取最後一則訊息，計算字數，然後把結果附加回去。不過裡面有幾個設計點值得你注意，我幫你拆解得更清楚一點，也順便指出可以優化的地方。

🧠 這段程式在做什麼？
1. 取得對話內容
messages = body.get("messages", [])
if not messages:
    return body
從 body 裡拿出整個對話列表

如果沒有訊息，就直接回傳（避免錯誤）

2. 抓最後一則訊息
last_message = messages[-1]
message_content = last_message.get("content", "")
messages[-1] = 最新的一則

拿出文字內容

3. 計算字數
message_len = len(message_content)
Python 的 len() 是字元數（不是詞數）

4. 修改訊息內容（關鍵）
last_message["content"] += f"\n\n*(系統分析：這則訊息的長度是 {message_len} 個字)*"
把分析結果直接「加在原訊息後面」

這是目前最穩定的做法（避免 SSE JSON 壞掉）

5. 回傳更新後的資料
return body
前端會用這個更新畫面

⚠️ 為什麼要「直接改內容」？
你註解寫得很關鍵：

前端接收 Action 的 SSE 串流時易發生 JSON 解析錯誤

這代表：

❌ 不適合用 streaming event 傳結果

✅ 最穩的方法是「把結果混進 message」

👉 這是一種 pragmatic（務實）解法，不是最乾淨，但最穩

🛠 可以優化的地方
1. 避免重複附加（重要）
現在每跑一次都會再加一次分析：

👉 建議加判斷：

if "系統分析" not in message_content:
    last_message["content"] += f"\n\n*(系統分析：這則訊息的長度是 {message_len} 個字)*"
2. 更精準的「字數」定義
如果你想區分：

中文字數

英文單詞數

可以改成：

import re

word_count = len(re.findall(r'\b\w+\b', message_content))
char_count = len(message_content)
3. 支援事件回傳（進階）
如果未來前端穩定，可以改用：

if __event_emitter__:
    await __event_emitter__({
        "type": "info",
        "data": f"字數：{message_len}"
    })
4. 防止修改原始資料（更乾淨）
現在是直接改 body（mutable）

👉 更安全版本：

import copy
new_body = copy.deepcopy(body)
✨ 改良版（推薦）
import copy
import re
from typing import Optional, Callable, Any

class Action:
    async def action(
        self,
        body: dict,
        __user__: Optional[dict] = None,
        __event_emitter__: Optional[Callable[..., Any]] = None,
    ) -> Optional[dict]:

        new_body = copy.deepcopy(body)
        messages = new_body.get("messages", [])

        if not messages:
            return new_body

        last_message = messages[-1]
        content = last_message.get("content", "")

        if "系統分析" in content:
            return new_body

        char_count = len(content)
        word_count = len(re.findall(r'\b\w+\b', content))

        last_message["content"] += (
            f"\n\n*(系統分析：字元 {char_count}，單詞 {word_count})*"
        )

        return new_body
🧩 總結一句話
這個 Action 的本質是：

👉「攔截訊息 → 做分析 → 把結果寫回去 → 回傳」

如果你接下來想做更進階的（例如：
🔹 自動摘要
🔹 情緒分析
🔹 關鍵字抽取
🔹 多語翻譯 Action）

我可以幫你把這個架構升級成一套「可插拔的 AI 工具鏈」。


"""
title: 基礎 Action 範例
author: YourName
version: 1.0
"""
from typing import Optional, Callable, Any

class Action:
    def __init__(self):
        pass

    async def action(
        self,
        body: dict,
        __user__: Optional[dict] = None,
        __event_emitter__: Optional[Callable[..., Any]] = None,
    ) -> Optional[dict]:
        
        # 取得所有對話
        messages = body.get("messages", [])
        if not messages:
            return body

        # 取得最後點擊欲處理的那則訊息
        last_message = messages[-1]
        message_content = last_message.get("content", "")
        message_len = len(message_content)

        # ⚠️ 由於目前前端接收 Action 的 SSE 串流時易發生 JSON 解析錯誤
        # 最穩定相容的做法是直接將結果附加在對話內容中並回傳 body
        last_message["content"] += f"\n\n*(系統分析：這則訊息的長度是 {message_len} 個字)*"

        # 回傳變更後的 body 讓前端更新畫面
        return body

你這段其實已經是「可用但偏原型」的寫法了——可以跑、也能達到效果，但如果要放進正式流程，還有幾個隱藏問題會慢慢出現。

我直接講重點，不繞圈。

⚠️ 目前這版的三個關鍵問題
1. 會一直「越加越長」（重複污染）
每次 Action 被觸發，就會再加一次：

*(系統分析：這則訊息的長度是 XX 個字)*
👉 長期會變這樣：

原訊息
*(分析)*
*(分析)*
*(分析)*
2. 直接修改原 body（有副作用）
messages = body.get("messages", [])
這是「引用」，不是複製
👉 你改 last_message = 在改原資料

在多 Action 或 middleware 串接時，容易出 bug

3. 沒有過濾「系統訊息 / 空訊息」
現在任何 message 都會被處理，包括：

system

tool

空字串

✅ 精簡但更穩的版本（建議直接用）
我幫你改成「實務可用版」，但保持結構簡單：

from typing import Optional, Callable, Any
import copy

class Action:
    async def action(
        self,
        body: dict,
        __user__: Optional[dict] = None,
        __event_emitter__: Optional[Callable[..., Any]] = None,
    ) -> Optional[dict]:

        # ✅ 避免污染原始資料
        new_body = copy.deepcopy(body)

        messages = new_body.get("messages", [])
        if not messages:
            return new_body

        last_message = messages[-1]

        # ✅ 只處理 user / assistant 訊息
        if last_message.get("role") not in ["user", "assistant"]:
            return new_body

        content = last_message.get("content", "").strip()
        if not content:
            return new_body

        # ✅ 防止重複附加
        if "系統分析：" in content:
            return new_body

        message_len = len(content)

        last_message["content"] += (
            f"\n\n*(系統分析：這則訊息的長度是 {message_len} 個字)*"
        )

        return new_body
🧠 如果你想再進一步（進階設計）
這段其實可以升級成「分析模組化」：

👉 把分析邏輯抽出來
def analyze_text(text: str) -> str:
    return f"字數：{len(text)}"
然後 Action 只負責：

接收 → 呼叫分析 → 回寫
🚀 更進階應用（你這架構可以做的）
你現在這個 pattern，其實就是：

Hook 訊息 → 加工 → 回寫

可以延伸成：

1. NLP 分析
情緒判斷 😄😡😢

關鍵字抽取

摘要

2. 創作輔助
自動改寫語氣

加上標題

轉成詩 / prompt

3. 開發工具
自動補註解

code review

debug hint

✨ 一句話總結
你現在這段：

✔ 功能正確
❗ 但缺少「防重複 + 防副作用 + 過濾」

補上這三個，就從「範例」變「可上線工具」。

如果你下一步想做「多功能 Action（像插件系統）」或「串多個分析器」，我可以幫你設計一個更像 AI pipeline 的架構。


"""
title: 基礎 Action 範例
author: YourName
version: 1.0
"""
from typing import Optional, Callable, Any

class Action:
    def __init__(self):
        pass

    async def action(
        self,
        body: dict,
        __user__: Optional[dict] = None,
        __event_emitter__: Optional[Callable[..., Any]] = None,
    ) -> Optional[dict]:
        
        # 取得所有對話
        messages = body.get("messages", [])
        if not messages:
            return body

        # 取得最後點擊欲處理的那則訊息
        last_message = messages[-1]
        message_content = last_message.get("content", "")
        message_len = len(message_content)

        # ⚠️ 由於目前前端接收 Action 的 SSE 串流時易發生 JSON 解析錯誤
        # 最穩定相容的做法是直接將結果附加在對話內容中並回傳 body
        last_message["content"] += f"\n\n*(系統分析：這則訊息的長度是 {message_len} 個字)*"

        # 回傳變更後的 body 讓前端更新畫面
        return body
請開啟畫布，我想和你討論

畫布已開好，你可以直接在上面改、加註解或丟想法。

我們可以從幾個方向一起拆這段（你選一個先深入）：

🔧 改成「可擴充的 Action 架構」（像 plugin pipeline）

🧠 加進 NLP（情緒 / 摘要 / 關鍵字）

⚡ 解決 SSE / event emitter 的正規做法

🧼 做成 production-ready（immutable / middleware / logging）

🎯 或你有特定功能想做（例如：自動改寫、翻譯）

你想先改哪一塊？我可以直接在畫布幫你一起重構。


已詢問 ChatGPT

Action 討論畫布
這是什麼意思

你選到這一行其實是在「宣告型別」，不是功能邏輯本身：

from typing import Optional, Callable, Any
我用白話講清楚它在幹嘛👇

🧠 這行的作用是什麼？
這是從 Python 的 型別提示工具（type hints） 匯入三個東西：

名稱	意思	用途
Optional	可以是某型別，也可以是 None	表示「可有可無」
Callable	一個「可被呼叫的東西」（像函式）	用來描述 function
Any	任意型別	不限制型別
🔍 對應到你程式裡
async def action(
    body: dict,
    __user__: Optional[dict] = None,
    __event_emitter__: Optional[Callable[..., Any]] = None,
) -> Optional[dict]:
我們一個一個拆👇

1️⃣ Optional[dict]
__user__: Optional[dict] = None
意思是：

__user__ 可以是 dict，也可以是 None

👉 等同：

__user__ 可以不存在
2️⃣ Optional[Callable[..., Any]]
__event_emitter__: Optional[Callable[..., Any]]
這比較關鍵 👇

拆開來看：

Callable = 一個可以被呼叫的東西（像 function）

... = 參數不限

Any = 回傳什麼都可以

👉 意思是：

__event_emitter__ 是「一個函式」，但也可能是 None

3️⃣ -> Optional[dict]
) -> Optional[dict]:
👉 代表這個 function：

會回傳 dict，或是 None

🧩 為什麼要寫這些？
這些不是給 Python 執行用的，而是：

✔ 提升可讀性
你一看就知道：

哪些參數可有可無

哪些是 function

✔ IDE 幫你檢查
像 VSCode / PyCharm 會：

自動補全

提醒型別錯誤

✔ 團隊開發
別人不用猜你的 API 怎麼用

✨ 一句話理解
這行可以理解成：

「幫你的程式加上說明書，但不影響執行」

🔥 如果你想更進一步
你現在這段其實已經在往「工程化」走了，可以再升級成：

TypedDict（定義 message 結構）

Protocol（定義 event emitter 介面）

pydantic（做資料驗證）

如果你覺得這段還有點抽象，我可以幫你畫一個「資料流圖」，把 body → messages → Action → 回傳 用視覺化方式拆給你看，會更直覺。


已詢問 ChatGPT

Action 討論畫布
它的用途

你選到的是 __event_emitter__（裡面的 _emitter_），它的用途其實很關鍵，但目前這段範例沒有用到它，所以看起來會有點迷。

我直接講白話👇

🧠 __event_emitter__ 是什麼？
它是一個「用來往前端發送即時訊息的函式」。

👉 可以把它想成：

📡 一個可以「主動推送資料出去」的工具（通常走 SSE / streaming）

🔧 它可以做什麼？
如果你有用它，可以做到：

1️⃣ 即時回傳訊息（不用等 return）
await __event_emitter__({
    "type": "message",
    "data": "正在分析中..."
})
👉 前端會「立刻收到」

2️⃣ 類似 ChatGPT 的打字效果
await __event_emitter__({
    "type": "chunk",
    "data": "Hello"
})
一段一段送出去

3️⃣ 傳狀態 / 進度
await __event_emitter__({
    "type": "status",
    "data": "處理中..."
})
⚠️ 為什麼你現在沒用它？
你程式裡已經寫出原因了：

# ⚠️ SSE 串流時易發生 JSON 解析錯誤
👉 意思是：

目前前端對 streaming 支援不穩

用 event_emitter 可能會壞掉

所以改用「直接改 message」這種保守解法

🧩 兩種模式對比
✅ 你現在用的（穩）
修改 message → return body → 前端更新
✔ 簡單
✔ 穩定
❌ 沒有即時效果

🚀 event_emitter（進階）
emit → emit → emit → 最後 return
✔ 即時
✔ 可以做動畫 / streaming
❌ 容易壞（目前你的環境）

✨ 一句話理解
__event_emitter__ =「即時推播工具」，但你現在環境不適合用

🔥 如果你之後想用它（進階範例）
if __event_emitter__:
    await __event_emitter__({
        "type": "info",
        "data": f"字數：{message_len}"
    })
🧠 小提醒（很重要）
這個參數：

Optional[Callable[..., Any]]
代表：

有可能是 function ✅

也有可能是 None ❌

👉 所以一定要先檢查：

if __event_emitter__:
如果你下一步想做的是「像 ChatGPT 一樣一邊輸出一邊顯示」，我們可以一起把這個 emitter 變成一個穩定版本（甚至做 fallback 機制）。






Action 討論畫布
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
24
25
26
27
28
29
30
31
32
33
34
35
"""
title: 基礎 Action 範例
author: YourName
version: 1.0
"""
from typing import Optional, Callable, Any

class Action:
    def __init__(self):
        pass

    async def action(
        self,
        body: dict,
        __user__: Optional[dict] = None,
        __event_emitter__: Optional[Callable[..., Any]] = None,
    ) -> Optional[dict]:
        
        # 取得所有對話
        messages = body.get("messages", [])
        if not messages:
            return body

        # 取得最後點擊欲處理的那則訊息
        last_message = messages[-1]
        message_content = last_message.get("content", "")
        message_len = len(message_content)

        # ⚠️ 由於目前前端接收 Action 的 SSE 串流時易發生 JSON 解析錯誤
        # 最穩定相容的做法是直接將結果附加在對話內容中並回傳 body
        last_message["content"] += f"\n\n*(系統分析：這則訊息的長度是 {message_len} 個字)*"

        # 回傳變更後的 body 讓前端更新畫面
        return body

