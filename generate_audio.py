#!/usr/bin/env python3
# 百人一首 VOICEVOX 音声ファイル自動生成スクリプト
#
# 使い方:
#   1. VOICEVOX を起動しておく
#   2. pip install requests
#   3. python generate_audio.py
#      (再実行時は --skip-existing で生成済みをスキップ)
#   4. audio/ フォルダに 200 ファイル (001_kami.mp3 〜 100_shimo.mp3) が生成される
#
# 所要時間: 10〜20 分程度

import argparse
import io
import json
import os
import subprocess
import sys
import time

import requests

VOICEVOX_URL = "http://localhost:50021"
OUTPUT_DIR = "audio"
MP3_BITRATE = "128k"

# ===== 百人一首データ =====
HYAKUNIN_ISSHU = [
    {"id": 1, "author": "天智天皇",
     "kami_yomi": "あきのたの かりほのいほの とまをあらみ",
     "shimo_yomi": "わがころもでは つゆにぬれつつ"},
    {"id": 2, "author": "持統天皇",
     "kami_yomi": "はるすぎて なつきにけらし しろたえの",
     "shimo_yomi": "ころもほすちょう あまのかぐやま"},
    {"id": 3, "author": "柿本人麻呂",
     "kami_yomi": "あしびきの やまどりのおの しだりおの",
     "shimo_yomi": "ながながしよを ひとりかもねむ"},
    {"id": 4, "author": "山部赤人",
     "kami_yomi": "たごのうらに うちいでてみれば しろたえの",
     "shimo_yomi": "ふじのたかねに ゆきはふりつつ"},
    {"id": 5, "author": "猿丸大夫",
     "kami_yomi": "おくやまに もみじふみわけ なくしかの",
     "shimo_yomi": "こえきくときぞ あきはかなしき"},
    {"id": 6, "author": "中納言家持",
     "kami_yomi": "かささぎの わたせるはしに おくしもの",
     "shimo_yomi": "しろきをみれば よぞふけにける"},
    {"id": 7, "author": "阿倍仲麻呂",
     "kami_yomi": "あまのはら ふりさけみれば かすがなる",
     "shimo_yomi": "みかさのやまに いでしつきかも"},
    {"id": 8, "author": "喜撰法師",
     "kami_yomi": "わがいおは みやこのたつみ しかぞすむ",
     "shimo_yomi": "よをうじやまと ひとはいうなり"},
    {"id": 9, "author": "小野小町",
     "kami_yomi": "はなのいろは うつりにけりな いたずらに",
     "shimo_yomi": "わがみよにふる ながめせしまに"},
    {"id": 10, "author": "蝉丸",
     "kami_yomi": "これやこの ゆくもかえるも わかれては",
     "shimo_yomi": "しるもしらぬも おうさかのせき"},
    {"id": 11, "author": "参議篁",
     "kami_yomi": "わたのはら やそしまかけて こぎいでぬと",
     "shimo_yomi": "ひとにはつげよ あまのつりぶね"},
    {"id": 12, "author": "僧正遍昭",
     "kami_yomi": "あまつかぜ くものかよいじ ふきとじよ",
     "shimo_yomi": "おとめのすがた しばしとどめむ"},
    {"id": 13, "author": "陽成院",
     "kami_yomi": "つくばねの みねよりおつる みなのかわ",
     "shimo_yomi": "こいぞつもりて ふちとなりぬる"},
    {"id": 14, "author": "河原左大臣",
     "kami_yomi": "みちのくの しのぶもじずり たれゆえに",
     "shimo_yomi": "みだれそめにし われならなくに"},
    {"id": 15, "author": "光孝天皇",
     "kami_yomi": "きみがため はるののにいでて わかなつむ",
     "shimo_yomi": "わがころもでに ゆきはふりつつ"},
    {"id": 16, "author": "中納言行平",
     "kami_yomi": "たちわかれ いなばのやまの みねにおうる",
     "shimo_yomi": "まつとしきかば いまかえりこむ"},
    {"id": 17, "author": "在原業平朝臣",
     "kami_yomi": "ちはやぶる かみよもきかず たつたがわ",
     "shimo_yomi": "からくれないに みずくくるとは"},
    {"id": 18, "author": "藤原敏行朝臣",
     "kami_yomi": "すみのえの きしによるなみ よるさえや",
     "shimo_yomi": "ゆめのかよいじ ひとめよくらむ"},
    {"id": 19, "author": "伊勢",
     "kami_yomi": "なにわがた みじかきあしの ふしのまも",
     "shimo_yomi": "あわでこのよを すぐしてよとや"},
    {"id": 20, "author": "元良親王",
     "kami_yomi": "わびぬれば いまはたおなじ なにわなる",
     "shimo_yomi": "みをつくしても あわむとぞおもう"},
    {"id": 21, "author": "素性法師",
     "kami_yomi": "いまこむと いいしばかりに ながつきの",
     "shimo_yomi": "ありあけのつきを まちいでつるかな"},
    {"id": 22, "author": "文屋康秀",
     "kami_yomi": "ふくからに あきのくさきの しおるれば",
     "shimo_yomi": "むべやまかぜを あらしというらむ"},
    {"id": 23, "author": "大江千里",
     "kami_yomi": "つきみれば ちぢにものこそ かなしけれ",
     "shimo_yomi": "わがみひとつの あきにはあらねど"},
    {"id": 24, "author": "菅家",
     "kami_yomi": "このたびは ぬさもとりあえず たむけやま",
     "shimo_yomi": "もみじのにしき かみのまにまに"},
    {"id": 25, "author": "三条右大臣",
     "kami_yomi": "なにしおわば おうさかやまの さねかずら",
     "shimo_yomi": "ひとにしられで くるよしもがな"},
    {"id": 26, "author": "貞信公",
     "kami_yomi": "おぐらやま みねのもみじば こころあらば",
     "shimo_yomi": "いまひとたびの みゆきまたなむ"},
    {"id": 27, "author": "中納言兼輔",
     "kami_yomi": "みかのはら わきてながるる いずみがわ",
     "shimo_yomi": "いつみきとてか こいしかるらむ"},
    {"id": 28, "author": "源宗于朝臣",
     "kami_yomi": "やまざとは ふゆぞさびしさ まさりける",
     "shimo_yomi": "ひとめもくさも かれぬとおもえば"},
    {"id": 29, "author": "凡河内躬恒",
     "kami_yomi": "こころあてに おらばやおらむ はつしもの",
     "shimo_yomi": "おきまどわせる しらぎくのはな"},
    {"id": 30, "author": "壬生忠岑",
     "kami_yomi": "ありあけの つれなくみえし わかれより",
     "shimo_yomi": "あかつきばかり うきものはなし"},
    {"id": 31, "author": "坂上是則",
     "kami_yomi": "あさぼらけ ありあけのつきと みるまでに",
     "shimo_yomi": "よしののさとに ふれるしらゆき"},
    {"id": 32, "author": "春道列樹",
     "kami_yomi": "やまがわに かぜのかけたる しがらみは",
     "shimo_yomi": "ながれもあえぬ もみじなりけり"},
    {"id": 33, "author": "紀友則",
     "kami_yomi": "ひさかたの ひかりのどけき はるのひに",
     "shimo_yomi": "しずこころなく はなのちるらむ"},
    {"id": 34, "author": "藤原興風",
     "kami_yomi": "たれをかも しるひとにせむ たかさごの",
     "shimo_yomi": "まつもむかしの ともならなくに"},
    {"id": 35, "author": "紀貫之",
     "kami_yomi": "ひとはいさ こころもしらず ふるさとは",
     "shimo_yomi": "はなぞむかしの かににおいける"},
    {"id": 36, "author": "清原深養父",
     "kami_yomi": "なつのよは まだよいながら あけぬるを",
     "shimo_yomi": "くものいずこに つきやどるらむ"},
    {"id": 37, "author": "文屋朝康",
     "kami_yomi": "しらつゆに かぜのふきしく あきののは",
     "shimo_yomi": "つらぬきとめぬ たまぞちりける"},
    {"id": 38, "author": "右近",
     "kami_yomi": "わすらるる みをばおもわず ちかいてし",
     "shimo_yomi": "ひとのいのちの おしくもあるかな"},
    {"id": 39, "author": "参議等",
     "kami_yomi": "あさじうの おののしのはら しのぶれど",
     "shimo_yomi": "あまりてなどか ひとのこいしき"},
    {"id": 40, "author": "平兼盛",
     "kami_yomi": "しのぶれど いろにいでにけり わがこいは",
     "shimo_yomi": "ものやおもうと ひとのとうまで"},
    {"id": 41, "author": "壬生忠見",
     "kami_yomi": "こいすちょう わがなはまだき たちにけり",
     "shimo_yomi": "ひとしれずこそ おもいそめしか"},
    {"id": 42, "author": "清原元輔",
     "kami_yomi": "ちぎりきな かたみにそでを しぼりつつ",
     "shimo_yomi": "すえのまつやま なみこさじとは"},
    {"id": 43, "author": "権中納言敦忠",
     "kami_yomi": "あいみての のちのこころに くらぶれば",
     "shimo_yomi": "むかしはものを おもわざりけり"},
    {"id": 44, "author": "中納言朝忠",
     "kami_yomi": "あうことの たえてしなくは なかなかに",
     "shimo_yomi": "ひとをもみをも うらみざらまし"},
    {"id": 45, "author": "謙徳公",
     "kami_yomi": "あわれとも いうべきひとは おもおえで",
     "shimo_yomi": "みのいたずらに なりぬべきかな"},
    {"id": 46, "author": "曾禰好忠",
     "kami_yomi": "ゆらのとを わたるふなびと かじをたえ",
     "shimo_yomi": "ゆくえもしらぬ こいのみちかな"},
    {"id": 47, "author": "恵慶法師",
     "kami_yomi": "やえむぐら しげれるやどの さびしきに",
     "shimo_yomi": "ひとこそみえね あきはきにけり"},
    {"id": 48, "author": "源重之",
     "kami_yomi": "かぜをいたみ いわうつなみの おのれのみ",
     "shimo_yomi": "くだけてものを おもうころかな"},
    {"id": 49, "author": "大中臣能宣朝臣",
     "kami_yomi": "みかきもり えじのたくひの よるはもえ",
     "shimo_yomi": "ひるはきえつつ ものをこそおもえ"},
    {"id": 50, "author": "藤原義孝",
     "kami_yomi": "きみがため おしからざりし いのちさえ",
     "shimo_yomi": "ながくもがなと おもいけるかな"},
    {"id": 51, "author": "藤原実方朝臣",
     "kami_yomi": "かくとだに えやはいぶきの さしもぐさ",
     "shimo_yomi": "さしもしらじな もゆるおもいを"},
    {"id": 52, "author": "藤原道信朝臣",
     "kami_yomi": "あけぬれば くるるものとは しりながら",
     "shimo_yomi": "なおうらめしき あさぼらけかな"},
    {"id": 53, "author": "右大将道綱母",
     "kami_yomi": "なげきつつ ひとりぬるよの あくるまは",
     "shimo_yomi": "いかにひさしき ものとかはしる"},
    {"id": 54, "author": "儀同三司母",
     "kami_yomi": "わすれじの ゆくすえまでは かたければ",
     "shimo_yomi": "きょうをかぎりの いのちともがな"},
    {"id": 55, "author": "大納言公任",
     "kami_yomi": "たきのおとは たえてひさしく なりぬれど",
     "shimo_yomi": "なこそながれて なおきこえけれ"},
    {"id": 56, "author": "和泉式部",
     "kami_yomi": "あらざらむ このよのほかの おもいでに",
     "shimo_yomi": "いまひとたびの あうこともがな"},
    {"id": 57, "author": "紫式部",
     "kami_yomi": "めぐりあいて みしやそれとも わかぬまに",
     "shimo_yomi": "くもがくれにし よわのつきかな"},
    {"id": 58, "author": "大弐三位",
     "kami_yomi": "ありまやま いなのささはら かぜふけば",
     "shimo_yomi": "いでそよひとを わすれやはする"},
    {"id": 59, "author": "赤染衛門",
     "kami_yomi": "やすらわで ねなましものを さよふけて",
     "shimo_yomi": "かたぶくまでの つきをみしかな"},
    {"id": 60, "author": "小式部内侍",
     "kami_yomi": "おおえやま いくののみちの とおければ",
     "shimo_yomi": "まだふみもみず あまのはしだて"},
    {"id": 61, "author": "伊勢大輔",
     "kami_yomi": "いにしえの ならのみやこの やえざくら",
     "shimo_yomi": "きょうここのえに においぬるかな"},
    {"id": 62, "author": "清少納言",
     "kami_yomi": "よをこめて とりのそらねは はかるとも",
     "shimo_yomi": "よにおうさかの せきはゆるさじ"},
    {"id": 63, "author": "左京大夫道雅",
     "kami_yomi": "いまはただ おもいたえなむ とばかりを",
     "shimo_yomi": "ひとづてならで いうよしもがな"},
    {"id": 64, "author": "権中納言定頼",
     "kami_yomi": "あさぼらけ うじのかわぎり たえだえに",
     "shimo_yomi": "あらわれわたる せぜのあじろぎ"},
    {"id": 65, "author": "相模",
     "kami_yomi": "うらみわび ほさぬそでだに あるものを",
     "shimo_yomi": "こいにくちなむ なこそおしけれ"},
    {"id": 66, "author": "前大僧正行尊",
     "kami_yomi": "もろともに あわれとおもえ やまざくら",
     "shimo_yomi": "はなよりほかに しるひともなし"},
    {"id": 67, "author": "周防内侍",
     "kami_yomi": "はるのよの ゆめばかりなる たまくらに",
     "shimo_yomi": "かいなくたたむ なこそおしけれ"},
    {"id": 68, "author": "三条院",
     "kami_yomi": "こころにも あらでうきよに ながらえば",
     "shimo_yomi": "こいしかるべき よわのつきかな"},
    {"id": 69, "author": "能因法師",
     "kami_yomi": "あらしふく みむろのやまの もみじばは",
     "shimo_yomi": "たつたのかわの にしきなりけり"},
    {"id": 70, "author": "良暹法師",
     "kami_yomi": "さびしさに やどをたちいでて ながむれば",
     "shimo_yomi": "いずこもおなじ あきのゆうぐれ"},
    {"id": 71, "author": "大納言経信",
     "kami_yomi": "ゆうされば かどたのいなば おとずれて",
     "shimo_yomi": "あしのまろやに あきかぜぞふく"},
    {"id": 72, "author": "祐子内親王家紀伊",
     "kami_yomi": "おとにきく たかしのはまの あだなみは",
     "shimo_yomi": "かけじやそでの ぬれもこそすれ"},
    {"id": 73, "author": "権中納言匡房",
     "kami_yomi": "たかさごの おのえのさくら さきにけり",
     "shimo_yomi": "とやまのかすみ たたずもあらなむ"},
    {"id": 74, "author": "源俊頼朝臣",
     "kami_yomi": "うかりける ひとをはつせの やまおろしよ",
     "shimo_yomi": "はげしかれとは いのらぬものを"},
    {"id": 75, "author": "藤原基俊",
     "kami_yomi": "ちぎりおきし させもがつゆを いのちにて",
     "shimo_yomi": "あわれことしの あきもいぬめり"},
    {"id": 76, "author": "法性寺入道前関白太政大臣",
     "kami_yomi": "わたのはら こぎいでてみれば ひさかたの",
     "shimo_yomi": "くもいにまごう おきつしらなみ"},
    {"id": 77, "author": "崇徳院",
     "kami_yomi": "せをはやみ いわにせかるる たきがわの",
     "shimo_yomi": "われてもすえに あわむとぞおもう"},
    {"id": 78, "author": "源兼昌",
     "kami_yomi": "あわじしま かようちどりの なくこえに",
     "shimo_yomi": "いくよねざめぬ すまのせきもり"},
    {"id": 79, "author": "左京大夫顕輔",
     "kami_yomi": "あきかぜに たなびくくもの たえまより",
     "shimo_yomi": "もれいずるつきの かげのさやけさ"},
    {"id": 80, "author": "待賢門院堀河",
     "kami_yomi": "ながからむ こころもしらず くろかみの",
     "shimo_yomi": "みだれてけさは ものをこそおもえ"},
    {"id": 81, "author": "後徳大寺左大臣",
     "kami_yomi": "ほととぎす なきつるかたを ながむれば",
     "shimo_yomi": "ただありあけの つきぞのこれる"},
    {"id": 82, "author": "道因法師",
     "kami_yomi": "おもいわび さてもいのちは あるものを",
     "shimo_yomi": "うきにたえぬは なみだなりけり"},
    {"id": 83, "author": "皇太后宮大夫俊成",
     "kami_yomi": "よのなかよ みちこそなけれ おもいいる",
     "shimo_yomi": "やまのおくにも しかぞなくなる"},
    {"id": 84, "author": "藤原清輔朝臣",
     "kami_yomi": "ながらえば またこのごろや しのばれむ",
     "shimo_yomi": "うしとみしよぞ いまはこいしき"},
    {"id": 85, "author": "俊恵法師",
     "kami_yomi": "よもすがら ものおもうころは あけやらで",
     "shimo_yomi": "ねやのひまさえ つれなかりけり"},
    {"id": 86, "author": "西行法師",
     "kami_yomi": "なげけとて つきやはものを おもわする",
     "shimo_yomi": "かこちがおなる わがなみだかな"},
    {"id": 87, "author": "寂蓮法師",
     "kami_yomi": "むらさめの つゆもまだひぬ まきのはに",
     "shimo_yomi": "きりたちのぼる あきのゆうぐれ"},
    {"id": 88, "author": "皇嘉門院別当",
     "kami_yomi": "なにわえの あしのかりねの ひとよゆえ",
     "shimo_yomi": "みをつくしてや こいわたるべき"},
    {"id": 89, "author": "式子内親王",
     "kami_yomi": "たまのおよ たえなばたえね ながらえば",
     "shimo_yomi": "しのぶることの よわりもぞする"},
    {"id": 90, "author": "殷富門院大輔",
     "kami_yomi": "みせばやな おじまのあまの そでだにも",
     "shimo_yomi": "ぬれにぞぬれし いろはかわらず"},
    {"id": 91, "author": "後京極摂政前太政大臣",
     "kami_yomi": "きりぎりす なくやしもよの さむしろに",
     "shimo_yomi": "ころもかたしき ひとりかもねむ"},
    {"id": 92, "author": "二条院讃岐",
     "kami_yomi": "わがそでは しおひにみえぬ おきのいしの",
     "shimo_yomi": "ひとこそしらね かわくまもなし"},
    {"id": 93, "author": "鎌倉右大臣",
     "kami_yomi": "よのなかは つねにもがもな なぎさこぐ",
     "shimo_yomi": "あまのおぶねの つなでかなしも"},
    {"id": 94, "author": "参議雅経",
     "kami_yomi": "みよしのの やまのあきかぜ さよふけて",
     "shimo_yomi": "ふるさとさむく ころもうつなり"},
    {"id": 95, "author": "前大僧正慈円",
     "kami_yomi": "おおけなく うきよのたみに おおうかな",
     "shimo_yomi": "わがたつそまに すみぞめのそで"},
    {"id": 96, "author": "入道前太政大臣",
     "kami_yomi": "はなさそう あらしのにわの ゆきならで",
     "shimo_yomi": "ふりゆくものは わがみなりけり"},
    {"id": 97, "author": "権中納言定家",
     "kami_yomi": "こぬひとを まつほのうらの ゆうなぎに",
     "shimo_yomi": "やくやもしおの みもこがれつつ"},
    {"id": 98, "author": "従二位家隆",
     "kami_yomi": "かぜそよぐ ならのおがわの ゆうぐれは",
     "shimo_yomi": "みそぎぞなつの しるしなりける"},
    {"id": 99, "author": "後鳥羽院",
     "kami_yomi": "ひともおし ひともうらめし あじきなく",
     "shimo_yomi": "よをおもうゆえに ものおもうみは"},
    {"id": 100, "author": "順徳院",
     "kami_yomi": "ももしきや ふるきのきばの しのぶにも",
     "shimo_yomi": "なおあまりある むかしなりけり"},
]


def check_voicevox():
    try:
        r = requests.get(f"{VOICEVOX_URL}/version", timeout=5)
        r.raise_for_status()
        print(f"VOICEVOX バージョン: {r.text.strip()}")
    except requests.exceptions.ConnectionError:
        print("エラー: VOICEVOX に接続できません。")
        print("VOICEVOX を起動してから再実行してください。")
        sys.exit(1)


def list_speakers():
    r = requests.get(f"{VOICEVOX_URL}/speakers", timeout=10)
    r.raise_for_status()
    speakers = r.json()
    print("\n利用可能な話者:")
    for sp in speakers:
        for style in sp["styles"]:
            print(f"  ID {style['id']:3d}  {sp['name']} ({style['name']})")
    return speakers


def generate_wav(text: str, speaker_id: int) -> bytes:
    # audio_query
    r = requests.post(
        f"{VOICEVOX_URL}/audio_query",
        params={"text": text, "speaker": speaker_id},
        timeout=30,
    )
    r.raise_for_status()
    query = r.json()

    query["speedScale"] = 0.75
    query["pitchScale"] = 0.0
    query["intonationScale"] = 1.2
    query["prePhonemeLength"] = 0.3
    query["postPhonemeLength"] = 0.8

    # synthesis
    r2 = requests.post(
        f"{VOICEVOX_URL}/synthesis",
        params={"speaker": speaker_id},
        headers={"Content-Type": "application/json"},
        data=json.dumps(query),
        timeout=60,
    )
    r2.raise_for_status()
    return r2.content


def wav_to_mp3(wav_bytes: bytes, out_path: str):
    cmd = [
        "ffmpeg", "-y",
        "-f", "wav", "-i", "pipe:0",
        "-b:a", MP3_BITRATE,
        out_path,
    ]
    result = subprocess.run(
        cmd,
        input=wav_bytes,
        capture_output=True,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.decode("utf-8", errors="replace"))


def main():
    parser = argparse.ArgumentParser(description="百人一首 VOICEVOX 音声生成")
    parser.add_argument("--speaker", type=int, default=0, help="話者ID (デフォルト: 0)")
    parser.add_argument("--skip-existing", action="store_true", help="生成済みファイルをスキップ")
    args = parser.parse_args()

    check_voicevox()
    list_speakers()

    print(f"\n使用話者ID: {args.speaker}")
    print(f"スキップモード: {'有効' if args.skip_existing else '無効'}")
    print()

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    total = len(HYAKUNIN_ISSHU) * 2
    done = 0
    failed = []
    start = time.time()

    for poem in HYAKUNIN_ISSHU:
        num = f"{poem['id']:03d}"
        items = [
            (f"{num}_kami.mp3", poem["kami_yomi"]),
            (f"{num}_shimo.mp3", poem["shimo_yomi"]),
        ]
        for filename, yomi_raw in items:
            done += 1
            out_path = os.path.join(OUTPUT_DIR, filename)
            label = f"[{done}/{total}] {filename}"

            if args.skip_existing and os.path.exists(out_path):
                print(f"{label} スキップ（生成済み）")
                continue

            print(f"{label} 生成中...", end="", flush=True)
            yomi = yomi_raw.replace("、", " ")
            try:
                wav = generate_wav(yomi, args.speaker)
                wav_to_mp3(wav, out_path)
                print(" 完了")
            except Exception as e:
                print(f" 失敗: {e}")
                failed.append(filename)

    elapsed = time.time() - start
    print(f"\n完了: {elapsed:.0f}秒")
    if failed:
        print(f"\n失敗ファイル ({len(failed)}件):")
        for f in failed:
            print(f"  {f}")
    else:
        print("すべてのファイルを生成しました。")


if __name__ == "__main__":
    main()
