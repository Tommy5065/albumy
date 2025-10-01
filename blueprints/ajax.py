"""
使用AJAX获取用户数据
思路：
1.鼠标悬停时发起AJAX请求
2.服务端把数据渲染进弹窗的html代码里
3.客户端获响应，显示弹窗
"""
from flask import Blueprint, render_template
from albumy.models import User

bp = Blueprint('ajax', __name__)

# 处理ajax请求试图函数


@bp.route('/profile_popup/<int:user_id>')
def get_profile(user_id):
    user = User.query.get_or_404(user_id)
    return render_template('main/profile_popup.html', user=user)
