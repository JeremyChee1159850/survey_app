import sys
import os

# 获取当前脚本的目录
current_dir = os.path.dirname(os.path.abspath(__file__))

# 将项目根目录添加到路径
sys.path.append(
    os.path.abspath(os.path.join(current_dir, "../.."))
)  # 向上两层到项目根目录

from project693.dao.competition_dao import CompetitionDao

competitionDao = CompetitionDao()
competitionDao.update_status_for_expired_competitions(None)
