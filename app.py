import streamlit as st
import pandas as pd
from datetime import datetime, timezone, timedelta

# 日本時間 (JST)
JST = timezone(timedelta(hours=9))

st.set_page_config(
    page_title="移動に関する福祉用具：ワークシート＆小テスト",
    page_icon="♿",
    layout="centered",
)

# =========================================================
# ルビ表示・スマホ最適化用カスタムCSS
# =========================================================
st.markdown("""
<style>
  .ruby-box {
    font-family: "UD Digi Kyokasho N-R", "BIZ UDPGothic", "Meiryo", sans-serif;
    font-size: 16px;
    line-height: 2.35;
    color: #222;
  }
  ruby { ruby-align: center; }
  rt { font-size: 0.58em; color: #444; font-weight: normal; line-height: 1; }
  
  .title-banner {
    background: linear-gradient(135deg, #1b4f72 0%, #2874a6 100%);
    color: #ffffff;
    padding: 16px 20px;
    border-radius: 10px;
    margin-bottom: 18px;
    line-height: 2.2;
  }
  .title-banner h1 {
    font-size: 22px;
    margin: 0;
    color: #ffffff;
  }
  .title-banner rt { color: #f7dc6f; }

  .case-card {
    background: #f8f9f9;
    border: 1.5px solid #2874a6;
    border-left: 6px solid #1b4f72;
    padding: 14px 16px;
    border-radius: 8px;
    margin-bottom: 14px;
    line-height: 2.35;
  }
  .case-title {
    font-size: 18px;
    font-weight: bold;
    color: #1b4f72;
    margin-bottom: 8px;
  }
  .quiz-card {
    background: #ffffff;
    border: 1px solid #bdc3c7;
    border-left: 5px solid #2874a6;
    padding: 12px 16px;
    border-radius: 8px;
    margin-bottom: 8px;
    line-height: 2.35;
  }
  .explanation-box {
    background: #fdedec;
    border-left: 5px solid #c0392b;
    padding: 12px 15px;
    border-radius: 6px;
    margin-top: 8px;
    margin-bottom: 16px;
    color: #78281f;
    line-height: 2.3;
  }
  .explanation-box.correct {
    background: #eafaf1;
    border-left-color: #27ae60;
    color: #145a32;
  }
</style>
""", unsafe_allow_html=True)

# =========================================================
# Googleスプレッドシート連携関数（任意・st.secrets設定時のみ動作）
# =========================================================
def save_to_gsheet(sheet_name: str, row_data: list) -> bool:
    """
    .streamlit/secrets.toml に gcp_service_account と spreadsheet_id が
    設定されている場合のみ自動でGoogleスプレッドシートに追記する。
    未設定の場合はスキップしてCSVダウンロードのみで完結する。
    """
    if "gcp_service_account" not in st.secrets or "spreadsheet_id" not in st.secrets:
        return False
    try:
        import gspread
        from google.oauth2.service_account import Credentials

        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive",
        ]
        creds = Credentials.from_service_account_info(
            st.secrets["gcp_service_account"], scopes=scopes
        )
        client = gspread.authorize(creds)
        sh = client.open_by_key(st.secrets["spreadsheet_id"])
        try:
            ws = sh.worksheet(sheet_name)
        except gspread.WorksheetNotFound:
            ws = sh.add_worksheet(title=sheet_name, rows=1000, cols=20)
        ws.append_row(row_data, value_input_option="USER_ENTERED")
        return True
    except Exception as e:
        st.warning(f"スプレッドシート保存エラー: {e}")
        return False

# =========================================================
# ヘッダー・学生情報入力欄
# =========================================================
st.markdown("""
<div class="title-banner ruby-box">
  <h1>♿ <ruby>生活支援技術<rt>せいかつしえんぎじゅつ</rt></ruby>：<ruby>移動<rt>いどう</rt></ruby>の<ruby>福祉用具<rt>ふくしようぐ</rt></ruby>（ワークシート＆<ruby>小<rt>しょう</rt></ruby>テスト）</h1>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="ruby-box">
  <strong>👤 <ruby>学生情報<rt>がくせいじょうほう</rt></ruby>を<ruby>入力<rt>にゅうりょく</rt></ruby>してください</strong>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    student_class = st.selectbox(
        "クラス（Class）",
        ["26A", "26B", "25A", "25B", "24B", "その他"],
        index=0
    )
    student_id = st.text_input("学籍番号（がくせきばんごう）", placeholder="例: 926001")
with col2:
    group_name = st.text_input("班名（はんめい・ワークシート用）", placeholder="例: 1班")
    student_name = st.text_input("氏名（ニックネーム）", placeholder="例: Your nickname")

st.divider()

# タブ構成
tab1, tab2 = st.tabs([
    "📝 ① 事例検討ワークシート（じれいけんとう）",
    "✅ ② 確認小テスト・全5問（かくにんしょうテスト）"
])

# =========================================================
# タブ1：事例検討ワークシート
# =========================================================
with tab1:
    st.markdown("""
    <div class="ruby-box">
      <p><ruby>以下<rt>いか</rt></ruby>の【<ruby>事例<rt>じれい</rt></ruby>A】【<ruby>事例<rt>じれい</rt></ruby>B】を<ruby>読<rt>よ</rt></ruby>み、<strong><ruby>最<rt>もっと</rt></ruby>も<ruby>適切<rt>てきせつ</rt></ruby>な<ruby>福祉用具<rt>ふくしようぐ</rt></ruby>を1つ<ruby>選<rt>えら</rt></ruby>び</strong>、その<ruby>根拠<rt>こんきょ</rt></ruby>（なぜそれが<ruby>良<rt>よ</rt></ruby>いのか、なぜ<ruby>他<rt>ほか</rt></ruby>の<ruby>選択肢<rt>せんたくし</rt></ruby>は<ruby>不適切<rt>ふてきせつ</rt></ruby>なのか）をグループで<ruby>話<rt>はな</rt></ruby>し<ruby>合<rt>あ</rt></ruby>って<ruby>入力<rt>にゅうりょく</rt></ruby>してください。</p>
    </div>
    """, unsafe_allow_html=True)

    # --- 事例A ---
    st.markdown("""
    <div class="case-card ruby-box">
      <div class="case-title">【<ruby>事例<rt>じれい</rt></ruby>A】82<ruby>歳女性<rt>さいじょせい</rt></ruby>（<ruby>要介護<rt>ようかいご</rt></ruby>2・<ruby>自宅<rt>じたく</rt></ruby>での<ruby>一人暮<rt>ひとりぐ</rt></ruby>らし）</div>
      <ul>
        <li><strong><ruby>身体状況<rt>しんたいじょうきょう</rt></ruby></strong>：<ruby>変形性膝関節症<rt>へんけいせいしつかんせつしょう</rt></ruby>により<ruby>両膝<rt>りょうひざ</rt></ruby>に<ruby>強<rt>つよ</rt></ruby>い<ruby>痛<rt>いた</rt></ruby>みがある。<ruby>立位保持<rt>りついほじ</rt></ruby>は<ruby>可能<rt>かのう</rt></ruby>だが、<ruby>一歩目<rt>いっぽめ</rt></ruby>を<ruby>踏<rt>ふ</rt></ruby>み<ruby>出<rt>だ</rt></ruby>す<ruby>際<rt>さい</rt></ruby>にふらつきがある。また、<ruby>加齢<rt>かれい</rt></ruby>により<ruby>握力<rt>あくりょく</rt></ruby>が<ruby>低下<rt>ていか</rt></ruby>している（<ruby>左右<rt>さゆう</rt></ruby>とも12kg<ruby>程度<rt>ていど</rt></ruby>）。<ruby>認知機能<rt>にんちきのう</rt></ruby>に<ruby>問題<rt>もんだい</rt></ruby>はない。</li>
        <li><strong><ruby>生活環境<rt>せいかつかんきょう</rt></ruby></strong>：<ruby>自宅内<rt>じたくない</rt></ruby>はバリアフリー<ruby>改修済<rt>かいしゅうず</rt></ruby>みで<ruby>段差<rt>だんさ</rt></ruby>はなく、<ruby>廊下幅<rt>ろうかはば</rt></ruby>も<ruby>広<rt>ひろ</rt></ruby>い。「<ruby>日中<rt>にっちゅう</rt></ruby>はベッドで<ruby>寝<rt>ね</rt></ruby>てばかりいず、トイレや<ruby>食堂<rt>しょくどう</rt></ruby>まで<ruby>自分<rt>じぶん</rt></ruby>で<ruby>歩<rt>ある</rt></ruby>いて<ruby>移動<rt>いどう</rt></ruby>したい」と<ruby>強<rt>つよ</rt></ruby>く<ruby>希望<rt>きぼう</rt></ruby>している。</li>
      </ul>
    </div>
    """, unsafe_allow_html=True)

    case_a_options = [
        "① T字杖（ティーじづえ）",
        "② 四点杖（よんてんづえ）",
        "③ 固定型［ピックアップ］歩行器（こていがたほこうき）",
        "④ 前腕支持型四輪歩行車（ぜんわんしじがたよんりんほこうしゃ）"
    ]
    case_a_choice = st.radio(
        "【事例A】1. 選定した福祉用具（せんていしたふくしようぐ）",
        case_a_options,
        index=None,
        key="case_a_choice"
    )
    case_a_reason = st.text_area(
        "【事例A】2. 選定の根拠（せんていのこんきょ：他の用具を除外した理由を含む）",
        placeholder="両膝の痛みや握力低下、家屋環境の視点から理由を入力してください...",
        height=100,
        key="case_a_reason"
    )

    st.divider()

    # --- 事例B ---
    st.markdown("""
    <div class="case-card ruby-box">
      <div class="case-title">【<ruby>事例<rt>じれい</rt></ruby>B】78<ruby>歳男性<rt>さいだんせい</rt></ruby>（<ruby>要介護<rt>ようかいご</rt></ruby>4・<ruby>介護老人福祉施設<rt>かいごろうじんふくししせつ</rt></ruby>に<ruby>入所中<rt>にゅうしょちゅう</rt></ruby>）</div>
      <ul>
        <li><strong><ruby>身体状況<rt>しんたいじょうきょう</rt></ruby></strong>：<ruby>脳梗塞後遺症<rt>のうこうそくこういしょう</rt></ruby>により<ruby>右片麻痺<rt>みぎかたまひ</rt></ruby>および<ruby>重度<rt>じゅうど</rt></ruby>の<ruby>体幹機能障害<rt>たいかんきのうしょうがい</rt></ruby>がある。<ruby>自力<rt>じりき</rt></ruby>での<ruby>座位保持<rt>ざいほじ</rt></ruby>が<ruby>難<rt>むずか</rt></ruby>しく、<ruby>標準型車<rt>ひょうじゅんがたくるま</rt></ruby>いすに<ruby>座<rt>すわ</rt></ruby>ると15<ruby>分<rt>ふん</rt></ruby>ほどで<ruby>身体<rt>しんたい</rt></ruby>が<ruby>右側<rt>みぎがわ</rt></ruby>に<ruby>傾<rt>かたむ</rt></ruby>き、お<ruby>尻<rt>しり</rt></ruby>が<ruby>前<rt>まえ</rt></ruby>に<ruby>滑<rt>すべ</rt></ruby>って「<ruby>仙骨座<rt>せんこつずわ</rt></ruby>り」になってしまう。<ruby>仙骨部<rt>せんこつぶ</rt></ruby>に<ruby>発赤<rt>ほっせき</rt></ruby>（<ruby>褥瘡<rt>じょくそう</rt></ruby>の<ruby>初期症状<rt>しょきしょうじょう</rt></ruby>）がみられる。</li>
        <li><strong><ruby>生活環境<rt>せいかつかんきょう</rt></ruby></strong>：<ruby>離床<rt>りしょう</rt></ruby>してデイルームで<ruby>過<rt>す</rt></ruby>ごす<ruby>時間<rt>じかん</rt></ruby>を<ruby>増<rt>ふ</rt></ruby>やしたい。<ruby>移動<rt>いどう</rt></ruby>はすべて<ruby>介護職<rt>かいごしょく</rt></ruby>が<ruby>介助<rt>かいじょ</rt></ruby>して<ruby>行<rt>おこな</rt></ruby>う。</li>
      </ul>
    </div>
    """, unsafe_allow_html=True)

    case_b_options = [
        "① 自走用標準型車いす（じそうようひょうじゅんがたくるまいす）",
        "② 介助用標準型車いす（かいじょようひょうじゅんがたくるまいす）",
        "③ リクライニング型車いす（りくらいにんぐがたくるまいす）",
        "④ ティルト・リクライニング型車いす［モジュラー調整機能付き］"
    ]
    case_b_choice = st.radio(
        "【事例B】1. 選定した福祉用具（せんていしたふくしようぐ）",
        case_b_options,
        index=None,
        key="case_b_choice"
    )
    case_b_reason = st.text_area(
        "【事例B】2. 選定の根拠（せんていのこんきょ：仙骨部の発赤予防の視点を含む）",
        placeholder="仙骨座りや剪断力（ずれ力）、姿勢保持の視点から理由を入力してください...",
        height=100,
        key="case_b_reason"
    )

    if st.button("📨 ワークシートを提出して解説を見る（ていしゅつ）", type="primary", use_container_width=True):
        if not student_id or not student_name:
            st.error("⚠️ 上部の「学籍番号（がくせきばんごう）」と「氏名（しめい）」を入力してください。")
        elif not case_a_choice or not case_b_choice:
            st.error("⚠️ 事例A・事例Bの両方の福祉用具を選択してください。")
        else:
            now_str = datetime.now(JST).strftime("%Y-%m-%d %H:%M:%S")
            ws_row = [
                now_str, student_class, group_name, student_id, student_name,
                case_a_choice, case_a_reason, case_b_choice, case_b_reason
            ]
            saved = save_to_gsheet("ワークシート回答", ws_row)
            st.success("✅ ワークシートの回答を記録しました！以下の解説を確認しましょう。")

            # 事例A・Bの判定と模範解答表示
            is_a_ok = case_a_choice.startswith("④")
            st.markdown(f"""
            <div class="explanation-box {'correct' if is_a_ok else ''} ruby-box">
              <strong>【<ruby>事例<rt>じれい</rt></ruby>A <ruby>模範解答<rt>もはんかいとう</rt></ruby>】 ④ <ruby>前腕支持型四輪歩行車<rt>ぜんわんしじがたよんりんほこうしゃ</rt></ruby></strong><br>
              <ruby>両膝<rt>りょうひざ</rt></ruby>に<ruby>痛<rt>いた</rt></ruby>みがあるため、<ruby>片手<rt>かたて</rt></ruby>で<ruby>持<rt>も</rt></ruby>つ<ruby>杖<rt>つえ</rt></ruby>（①・②）では<ruby>両下肢<rt>りょうかし</rt></ruby>の<ruby>免荷<rt>めんか</rt></ruby>（<ruby>体重<rt>たいじゅう</rt></ruby>の<ruby>分散<rt>ぶんさん</rt></ruby>）が<ruby>不十分<rt>ふじゅうぶん</rt></ruby>です。また、<ruby>握力<rt>あくりょく</rt></ruby>が<ruby>低下<rt>ていか</rt></ruby>しているため、<ruby>毎回持<rt>まいかいも</rt></ruby>ち<ruby>上<rt>あ</rt></ruby>げる③<ruby>固定型歩行器<rt>こていがたほこうき</rt></ruby>は<ruby>負担<rt>ふたん</rt></ruby>が<ruby>大<rt>おお</rt></ruby>きくなります。<ruby>段差<rt>だんさ</rt></ruby>のない<ruby>広<rt>ひろ</rt></ruby>い<ruby>屋内環境<rt>おくないかんきょう</rt></ruby>であり、<ruby>前腕<rt>ぜんわん</rt></ruby>で<ruby>体重<rt>たいじゅう</rt></ruby>を<ruby>預<rt>あず</rt></ruby>けながら<ruby>押<rt>お</rt></ruby>して<ruby>進<rt>すす</rt></ruby>める④が<ruby>最<rt>もっと</rt></ruby>も<ruby>安全<rt>あんぜん</rt></ruby>で<ruby>自立支援<rt>じりつしえん</rt></ruby>につながります。
            </div>
            """, unsafe_allow_html=True)

            is_b_ok = case_b_choice.startswith("④")
            st.markdown(f"""
            <div class="explanation-box {'correct' if is_b_ok else ''} ruby-box">
              <strong>【<ruby>事例<rt>じれい</rt></ruby>B <ruby>模範解答<rt>もはんかいとう</rt></ruby>】 ④ ティルト・リクライニング<ruby>型車<rt>がたくるま</rt></ruby>いす（モジュラー<ruby>調整機能付<rt>ちょうせいきのうつ</rt></ruby>き）</strong><br>
              <ruby>体幹保持<rt>たいかんほじ</rt></ruby>が<ruby>困難<rt>こんなん</rt></ruby>で<ruby>仙骨座<rt>せんこつずわ</rt></ruby>り・<ruby>発赤<rt>ほっせき</rt></ruby>があるため<ruby>標準型<rt>ひょうじゅんがた</rt></ruby>（①・②）は<ruby>不適<rt>ふてき</rt></ruby>です。また、<ruby>単<rt>たん</rt></ruby>なる③リクライニング<ruby>型<rt>がた</rt></ruby>では<ruby>背<rt>せ</rt></ruby>もたれを<ruby>倒<rt>たお</rt></ruby>した<ruby>際<rt>さい</rt></ruby>に<ruby>背中<rt>せなか</rt></ruby>とお<ruby>尻<rt>しり</rt></ruby>に「ずれ<ruby>力<rt>りょく</rt></ruby>（<ruby>剪断力<rt>せんだんりょく</rt></ruby>）」が<ruby>働<rt>はたら</rt></ruby>き、<ruby>仙骨部<rt>せんこつぶ</rt></ruby>の<ruby>発赤<rt>ほっせき</rt></ruby>を<ruby>悪化<rt>あっか</rt></ruby>させます。<ruby>座面角度<rt>ざめんかくど</rt></ruby>を<ruby>保<rt>たも</rt></ruby>ったまま<ruby>傾<rt>かたむ</rt></ruby>けて<ruby>除圧<rt>じょあつ</rt></ruby>と<ruby>姿勢保持<rt>しせいほじ</rt></ruby>ができる④が<ruby>最適<rt>さいてき</rt></ruby>です。
            </div>
            """, unsafe_allow_html=True)

            # CSVダウンロードボタン
            df_ws = pd.DataFrame([ws_row], columns=[
                "提出日時", "クラス", "班名", "学籍番号", "氏名",
                "事例A選択", "事例A根拠", "事例B選択", "事例B根拠"
            ])
            csv_ws = df_ws.to_csv(index=False, encoding="utf-8-sig")
            st.download_button(
                label="📥 ワークシート回答CSVをダウンロード",
                data=csv_ws,
                file_name=f"worksheet_{student_class}_{student_id}.csv",
                mime="text/csv"
            )

# =========================================================
# タブ2：確認小テスト（全5問）
# =========================================================
with tab2:
    st.markdown("""
    <div class="ruby-box">
      <p><strong><ruby>次<rt>つぎ</rt></ruby>の<ruby>記述<rt>きじゅつ</rt></ruby>について、<ruby>適切<rt>てきせつ</rt></ruby>なものには「○」、<ruby>不適切<rt>ふてきせつ</rt></ruby>なものには「×」を<ruby>選<rt>えら</rt></ruby>びなさい。</strong></p>
    </div>
    """, unsafe_allow_html=True)

    quiz_data = [
        {
            "no": 1,
            "q_html": "<strong>【<ruby>問<rt>とい</rt></ruby>1】</strong> T<ruby>字杖<rt>じづえ</rt></ruby>の<ruby>長<rt>なが</rt></ruby>さを<ruby>調整<rt>ちょうせい</rt></ruby>する<ruby>際<rt>さい</rt></ruby>、<ruby>利用者<rt>りようしゃ</rt></ruby>が<ruby>靴<rt>くつ</rt></ruby>を<ruby>履<rt>は</rt></ruby>いて<ruby>自然立位<rt>しぜんりつい</rt></ruby>をとった<ruby>状態<rt>じょうたい</rt></ruby>で、<ruby>大転子<rt>だいてんし</rt></ruby>の<ruby>高<rt>たか</rt></ruby>さ（<ruby>肘関節<rt>ちゅうかんせつ</rt></ruby>が<ruby>約<rt>やく</rt></ruby>30<ruby>度屈曲<rt>どくっきょく</rt></ruby>する<ruby>位置<rt>いち</rt></ruby>）にグリップがくるように<ruby>合<rt>あ</rt></ruby>わせた。",
            "ans": "○",
            "exp_html": "<ruby>杖<rt>つえ</rt></ruby>のフィッティングの<ruby>基本<rt>きほん</rt></ruby>です。<ruby>大転子<rt>だいてんし</rt></ruby>の<ruby>位置<rt>いち</rt></ruby>、<ruby>肘関節屈曲約<rt>ちゅうかんせつくっきょくやく</rt></ruby>30<ruby>度<rt>ど</rt></ruby>、または「<ruby>身長<rt>しんちょう</rt></ruby>÷2＋2〜3cm」の<ruby>基準<rt>きじゅん</rt></ruby>を<ruby>覚<rt>おぼ</rt></ruby>えておきましょう。"
        },
        {
            "no": 2,
            "q_html": "<strong>【<ruby>問<rt>とい</rt></ruby>2】</strong> <ruby>多点杖<rt>たてんづえ</rt></ruby>（<ruby>四点杖<rt>よんてんづえ</rt></ruby>）はT<ruby>字杖<rt>じづえ</rt></ruby>よりも<ruby>支持基底面<rt>しじきていめん</rt></ruby>が<ruby>広<rt>ひろ</rt></ruby>いため、<ruby>凹凸<rt>おうとつ</rt></ruby>のある<ruby>砂利道<rt>じゃりみち</rt></ruby>や<ruby>階段<rt>かいだん</rt></ruby>の<ruby>昇降<rt>しょうこう</rt></ruby>において<ruby>最<rt>もっと</rt></ruby>も<ruby>安全<rt>あんぜん</rt></ruby>に<ruby>使用<rt>しよう</rt></ruby>できる。",
            "ans": "×",
            "exp_html": "<ruby>多点杖<rt>たてんづえ</rt></ruby>は4つの<ruby>脚<rt>あし</rt></ruby>すべてが<ruby>床<rt>ゆか</rt></ruby>に<ruby>接地<rt>せっち</rt></ruby>して<ruby>初<rt>はじ</rt></ruby>めて<ruby>安定<rt>あんてい</rt></ruby>します。<ruby>凹凸<rt>おうとつ</rt></ruby>のある<ruby>道<rt>みち</rt></ruby>や<ruby>坂道<rt>さかみち</rt></ruby>、<ruby>狭<rt>せま</rt></ruby>い<ruby>階段<rt>かいだん</rt></ruby>の<ruby>踏<rt>ふ</rt></ruby>み<ruby>面<rt>づら</rt></ruby>では<ruby>脚<rt>あし</rt></ruby>が<ruby>浮<rt>う</rt></ruby>いてしまい、かえって<ruby>転倒<rt>てんとう</rt></ruby>リスクが<ruby>高<rt>たか</rt></ruby>まります。"
        },
        {
            "no": 3,
            "q_html": "<strong>【<ruby>問<rt>とい</rt></ruby>3】</strong> <ruby>足腰<rt>あしこし</rt></ruby>が<ruby>弱<rt>よわ</rt></ruby>り、<ruby>立位<rt>りつい</rt></ruby>バランスが<ruby>不安定<rt>ふあんてい</rt></ruby>になった<ruby>利用者<rt>りようしゃ</rt></ruby>から「<ruby>体重<rt>たいじゅう</rt></ruby>をかけて<ruby>歩<rt>ある</rt></ruby>きたい」と<ruby>相談<rt>そうだん</rt></ruby>されたため、<ruby>買<rt>か</rt></ruby>い<ruby>物<rt>もの</rt></ruby>カゴのついたシルバーカーの<ruby>購入<rt>こうにゅう</rt></ruby>を<ruby>勧<rt>すす</rt></ruby>めた。",
            "ans": "×",
            "exp_html": "シルバーカーは<ruby>自立歩行<rt>じりつほこう</rt></ruby>ができる<ruby>人<rt>ひと</rt></ruby>の「<ruby>荷物運搬<rt>にもつうんぱん</rt></ruby>・<ruby>休憩用<rt>きゅうけいよう</rt></ruby>」であり、<ruby>体重<rt>たいじゅう</rt></ruby>を<ruby>預<rt>あず</rt></ruby>けると<ruby>転倒<rt>てんとう</rt></ruby>する<ruby>恐<rt>おそ</rt></ruby>れがあります。<ruby>体重<rt>たいじゅう</rt></ruby>を<ruby>支<rt>ささ</rt></ruby>えるには「<ruby>歩行器<rt>ほこうき</rt></ruby>（<ruby>歩行車<rt>ほこうしゃ</rt></ruby>）」を<ruby>選定<rt>せんてい</rt></ruby>します。"
        },
        {
            "no": 4,
            "q_html": "<strong>【<ruby>問<rt>とい</rt></ruby>4】</strong> <ruby>車<rt>くるま</rt></ruby>いすに<ruby>深<rt>ふか</rt></ruby>く<ruby>腰掛<rt>こしか</rt></ruby>けた<ruby>際<rt>さい</rt></ruby>、<ruby>座面<rt>ざめん</rt></ruby>シートの<ruby>前端<rt>ぜんたん</rt></ruby>が<ruby>膝窩<rt>しつか</rt></ruby>（<ruby>膝<rt>ひざ</rt></ruby>の<ruby>裏<rt>うら</rt></ruby>）にぴったりと<ruby>密着<rt>みっちゃく</rt></ruby>している<ruby>状態<rt>じょうたい</rt></ruby>が、<ruby>最<rt>もっと</rt></ruby>も<ruby>安定<rt>あんてい</rt></ruby>した<ruby>適切<rt>てきせつ</rt></ruby>な<ruby>奥行<rt>おくゆ</rt></ruby>きである。",
            "ans": "×",
            "exp_html": "<ruby>座面前端<rt>ざめんぜんたん</rt></ruby>と<ruby>膝裏<rt>ひざうら</rt></ruby>が<ruby>密着<rt>みっちゃく</rt></ruby>していると、<ruby>膝窩<rt>しつか</rt></ruby>の<ruby>血管<rt>けっかん</rt></ruby>や<ruby>神経<rt>しんけい</rt></ruby>を<ruby>圧迫<rt>あっぱく</rt></ruby>し、お<ruby>尻<rt>しり</rt></ruby>を<ruby>前<rt>まえ</rt></ruby>にずらす「<ruby>仙骨座<rt>せんこつずわ</rt></ruby>り」の<ruby>原因<rt>げんいん</rt></ruby>になります。<ruby>指<rt>ゆび</rt></ruby>2〜3<ruby>本分<rt>ぼんぶん</rt></ruby>（3〜5cm）の<ruby>隙間<rt>すきま</rt></ruby>が<ruby>必要<rt>ひつよう</rt></ruby>です。"
        },
        {
            "no": 5,
            "q_html": "<strong>【<ruby>問<rt>とい</rt></ruby>5】</strong> <ruby>車<rt>くるま</rt></ruby>いすのタイヤの<ruby>空気圧<rt>くうきあつ</rt></ruby>が<ruby>不足<rt>ふそく</rt></ruby>していると、<ruby>駐車<rt>ちゅうしゃ</rt></ruby>ブレーキを<ruby>正<rt>ただ</rt></ruby>しくかけても<ruby>車輪<rt>しゃりん</rt></ruby>が<ruby>動<rt>うご</rt></ruby>いてしまう<ruby>危険<rt>きけん</rt></ruby>がある。",
            "ans": "○",
            "exp_html": "<ruby>標準型車<rt>ひょうじゅんがたくるま</rt></ruby>いすの<ruby>駐車<rt>ちゅうしゃ</rt></ruby>ブレーキは、タイヤの<ruby>表面<rt>ひょうめん</rt></ruby>にストッパーを<ruby>押<rt>お</rt></ruby>し<ruby>当<rt>あ</rt></ruby>てて<ruby>止<rt>と</rt></ruby>める<ruby>構造<rt>こうぞう</rt></ruby>です。<ruby>空気<rt>くうき</rt></ruby>が<ruby>抜<rt>ぬ</rt></ruby>けているとストッパーが<ruby>食<rt>く</rt></ruby>い<ruby>込<rt>こ</rt></ruby>まず、<ruby>移乗時<rt>いじょうじ</rt></ruby>の<ruby>転倒事故<rt>てんとうじこ</rt></ruby>につながります。"
        }
    ]

    user_answers = {}
    for q in quiz_data:
        st.markdown(f'<div class="quiz-card ruby-box">{q["q_html"]}</div>', unsafe_allow_html=True)
        user_answers[q["no"]] = st.radio(
            f"問{q['no']}の回答",
            ["○", "×"],
            index=None,
            horizontal=True,
            key=f"q_{q['no']}",
            label_visibility="collapsed"
        )

    if st.button("💯 採点して結果を提出する（さいてん・ていしゅつ）", type="primary", use_container_width=True):
        if not student_id or not student_name:
            st.error("⚠️ 上部の「学籍番号（がくせきばんごう）」と「氏名（しめい）」を入力してください。")
        elif None in user_answers.values():
            st.error("⚠️ すべての問題（問1〜問5）に回答してください。")
        else:
            score = sum(1 for q in quiz_data if user_answers[q["no"]] == q["ans"])
            now_str = datetime.now(JST).strftime("%Y-%m-%d %H:%M:%S")
            quiz_row = [
                now_str, student_class, student_id, student_name, score,
                user_answers[1], user_answers[2], user_answers[3], user_answers[4], user_answers[5]
            ]
            save_to_gsheet("小テスト結果", quiz_row)

            st.subheader(f"🎯 得点（とくてん）： {score} / 5 点")
            if score == 5:
                st.balloons()
                st.success("🎉 満点です！福祉用具の特性とフィッティング基準をしっかり理解できています。")
            else:
                st.info("間違えた問題の解説を読んで復習しておきましょう。")

            for q in quiz_data:
                u_ans = user_answers[q["no"]]
                is_correct = (u_ans == q["ans"])
                mark = "⭕ 正解！" if is_correct else "❌ 不正解"
                st.markdown(f"""
                <div class="explanation-box {'correct' if is_correct else ''} ruby-box">
                  <strong>【<ruby>問<rt>とい</rt></ruby>{q['no']}】 {mark}</strong>
                  （あなたの<ruby>回答<rt>かいとう</rt></ruby>：<strong>{u_ans}</strong> ／ <ruby>正解<rt>せいかい</rt></ruby>：<strong>{q['ans']}</strong>）<br>
                  {q['exp_html']}
                </div>
                """, unsafe_allow_html=True)

            df_quiz = pd.DataFrame([quiz_row], columns=[
                "提出日時", "クラス", "学籍番号", "氏名", "得点",
                "問1", "問2", "問3", "問4", "問5"
            ])
            csv_quiz = df_quiz.to_csv(index=False, encoding="utf-8-sig")
            st.download_button(
                label="📥 小テスト結果CSVをダウンロード",
                data=csv_quiz,
                file_name=f"quiz_{student_class}_{student_id}.csv",
                mime="text/csv"
            )