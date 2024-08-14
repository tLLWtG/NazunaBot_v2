from nonebot import get_plugin_config
from nonebot.plugin import PluginMetadata
from nonebot.plugin import on_command
from nonebot.adapters import Message
from nonebot.params import CommandArg

from .config import Config

import requests
import json
import time

__plugin_meta__ = PluginMetadata(
    name="CP",
    description="",
    usage="",
    config=Config,
)

config = get_plugin_config(Config)

recent_contest = on_command("contest", priority=5, block=True)

find_user = on_command("find", priority=5, block=True)

@recent_contest.handle()
async def recent_contest_handler():
    contest = await get_contest()
    await recent_contest.finish(contest)
    
@find_user.handle()
async def find_user_handler(args: Message = CommandArg()):
    user_name = args.extract_plain_text()
    if not user_name:
        await find_user.finish('你想盒谁呢？使用 find 命令时请带上他的 ID')
    else:
        user_info = await get_user(user_name)
        await find_user.finish(user_info)
    
    
async def get_contest() -> str:
    try:
        res_text = requests.get('https://codeforces.com/api/contest.list?gym=false').text
    # res_text = '{"status":"OK","result":[{"id":1835,"name":"Codeforces Round (Div. 1)","type":"CF","phase":"BEFORE","frozen":false,"durationSeconds":7200,"startTimeSeconds":1687098900,"relativeTimeSeconds":-2081273},{"id":1836,"name":"Codeforces Round (Div. 2)","type":"CF","phase":"BEFORE","frozen":false,"durationSeconds":7200,"startTimeSeconds":1687098900,"relativeTimeSeconds":-2081273},{"id":1834,"name":"Codeforces Round (Div. 2)","type":"CF","phase":"BEFORE","frozen":false,"durationSeconds":7200,"startTimeSeconds":1687075500,"relativeTimeSeconds":-2057873},{"id":1838,"name":"Codeforces Round 876 (Div. 2)","type":"CF","phase":"BEFORE","frozen":false,"durationSeconds":7200,"startTimeSeconds":1685284500,"relativeTimeSeconds":-266873},{"id":1830,"name":"Codeforces Round 875 (Div. 1)","type":"CF","phase":"BEFORE","frozen":false,"durationSeconds":9000,"startTimeSeconds":1685198100,"relativeTimeSeconds":-180473},{"id":1831,"name":"Codeforces Round 875 (Div. 2)","type":"CF","phase":"BEFORE","frozen":false,"durationSeconds":9000,"startTimeSeconds":1685198100,"relativeTimeSeconds":-180473},{"id":1837,"name":"Educational Codeforces Round 149 (Rated for Div. 2)","type":"ICPC","phase":"BEFORE","frozen":false,"durationSeconds":7200,"startTimeSeconds":1685025300,"relativeTimeSeconds":-7675},{"id":1833,"name":"Codeforces Round 874 (Div. 3)","type":"ICPC","phase":"FINISHED","frozen":false,"durationSeconds":8100,"startTimeSeconds":1684506900,"relativeTimeSeconds":510727},{"id":1827,"name":"Codeforces Round 873 (Div. 1)","type":"CF","phase":"FINISHED","frozen":false,"durationSeconds":7200,"startTimeSeconds":1684074900,"relativeTimeSeconds":942726},{"id":1828,"name":"Codeforces Round 873 (Div. 2)","type":"CF","phase":"FINISHED","frozen":false,"durationSeconds":7200,"startTimeSeconds":1684074900,"relativeTimeSeconds":942727},{"id":1832,"name":"Educational Codeforces Round 148 (Rated for Div. 2)","type":"ICPC","phase":"FINISHED","frozen":false,"durationSeconds":7200,"startTimeSeconds":1683902100,"relativeTimeSeconds":1115527},{"id":1824,"name":"Codeforces Round 872 (Div. 1)","type":"CF","phase":"FINISHED","frozen":false,"durationSeconds":7200,"startTimeSeconds":1683547500,"relativeTimeSeconds":1470126},{"id":1825,"name":"Codeforces Round 872 (Div. 2)","type":"CF","phase":"FINISHED","frozen":false,"durationSeconds":7200,"startTimeSeconds":1683547500,"relativeTimeSeconds":1470127},{"id":1829,"name":"Codeforces Round 871 (Div. 4)","type":"ICPC","phase":"FINISHED","frozen":false,"durationSeconds":8100,"startTimeSeconds":1683383700,"relativeTimeSeconds":1633927}]}'
    # {"id":1835,"name":"Codeforces Round (Div. 1)","type":"CF","phase":"BEFORE","frozen":false,"durationSeconds":7200,"startTimeSeconds":1687098900,"relativeTimeSeconds":-2081273}
    except:
        return '查询失败：与 CF 服务器通信异常'
    
    contest_BEFORE = []
    
    try:
        res_dict = json.loads(res_text)

        if res_dict['status'] != 'OK':
            return f'查询失败：CF 服务器返回状态 {res_dict["status"]}'
        
        for contest in res_dict['result']:
            if contest['phase'] == 'BEFORE':
                contest_BEFORE.append(contest)
            else:
                break
    except:
        return '查询失败：无法解析接收到的比赛信息'
    
    if contest_BEFORE.__sizeof__() == 0:
        return '近期暂无比赛'
    
    res_contest_info = '查询到近期的比赛：\n\n'

    for contest in contest_BEFORE[::-1]:
        contest_time = int(contest['startTimeSeconds'])
        time_array = time.localtime(contest_time)
        other_style_time = time.strftime('%Y/%m/%d %H:%M', time_array)
        res_contest_info += f'比赛名称: {contest["name"]}#{contest["id"]}\n开始时间: {other_style_time} (UTC+8)\n比赛时长: {int(contest["durationSeconds"]/60)}min\n\n'
    # 2023/05/26 22:35 (UTC+8)
    res_contest_info = res_contest_info[:-2]
    
    return res_contest_info

async def get_user(user_name: str) -> str:
    try:
        res_text = requests.get(f'https://codeforces.com/api/user.info?handles={user_name}').text
        # {"status":"OK","result":[{"lastName":"Liu","country":"China","lastOnlineTimeSeconds":1685102389,"city":"Xiamen","rating":1603,"friendOfCount":21,"titlePhoto":"https://userpic.codeforces.org/2666095/title/79facb85f5d40bf3.jpg","handle":"tllwtg","avatar":"https://userpic.codeforces.org/2666095/avatar/6f691b091db0608a.jpg","firstName":"Zhiliu","contribution":7,"organization":"Xiamen University","rank":"expert","maxRating":1633,"registrationTimeSeconds":1657157707,"email":"1656336917@qq.com","maxRank":"expert"}]}
    except:
        return '盒打击失败：与 CF 服务器通信异常'
    
    try:
        res_dict = json.loads(res_text)
        if res_dict['status'] != 'OK':
            if res_dict['comment'] == f'handles: User with handle {user_name} not found':
                return f'盒打击失败：查无此人'
            else:
                return f'盒打击失败：CF 服务器返回状态 {res_dict["status"]}'
    except:
        return '盒打击失败：无法解析接收到的用户信息'
    
    user_info = '盒打击成功，查询到以下信息：\n\n'
    user_info += f'name: {res_dict["result"][0]["handle"]}\n'
    try:
        user_info += f'rating: {res_dict["result"][0]["rating"]}\n'
        user_info += f'maxRating: {res_dict["result"][0]["maxRating"]}\n'
        user_info += f'rank: {res_dict["result"][0]["rank"]}\n'
    except:
        user_info += f'rating: unrated\n'
        user_info += f'maxRating: unrated\n'
        user_info += f'rank: unrated\n'
    user_info += f'friends: {res_dict["result"][0]["friendOfCount"]}\n'
    user_info += f'contribution: {res_dict["result"][0]["contribution"]}\n\n'
    
    online_time = int(res_dict["result"][0]["lastOnlineTimeSeconds"])
    time_array = time.localtime(online_time)
    other_style_time_lo = time.strftime('%Y/%m/%d %H:%M:%S', time_array)
    
    try:
        res_text = requests.get(f'https://codeforces.com/api/user.status?handle={user_name}&from=1&count=1').text
        # {"status":"OK","result":[{"id":207229370,"contestId":1837,"creationTimeSeconds":1685029343,"relativeTimeSeconds":4043,"problem":{"contestId":1837,"index":"D","name":"Bracket Coloring","type":"PROGRAMMING","tags":["constructive algorithms","data structures","greedy"]},"author":{"contestId":1837,"members":[{"handle":"tllwtg"}],"participantType":"CONTESTANT","ghost":false,"startTimeSeconds":1685025300},"programmingLanguage":"GNU C++17","verdict":"OK","testset":"TESTS","passedTestCount":21,"timeConsumedMillis":31,"memoryConsumedBytes":2150400}]}
    except:
        return '盒打击失败：与 CF 服务器通信异常'
        
    try:
        res_dict = json.loads(res_text)
        if res_dict['status'] != 'OK':
            if res_dict['comment'] == f'handles: User with handle {user_name} not found':
                return f'盒打击失败：查无此人'
            else:
                return f'盒打击失败：CF 服务器返回状态 {res_dict["status"]}'
    except:
        return '盒打击失败：无法解析接收到的用户信息'
    
    if not res_dict["result"]:
        user_info += f'lastSubmission: never submit\n'
    else:
        online_time = int(res_dict["result"][0]["creationTimeSeconds"])
        time_array = time.localtime(online_time)
        other_style_time_ls = time.strftime('%Y/%m/%d %H:%M:%S', time_array)
        user_info += f'lastSubmission: {other_style_time_ls}\n'
    
    user_info += f'lastOnline: {other_style_time_lo}'

    return user_info