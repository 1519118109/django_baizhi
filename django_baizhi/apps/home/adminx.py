import xadmin
from xadmin import views

from home.models import Banner, Nav


class BaseSettings(object):
    enable_themes = True    # 开始主题切换
    use_bootswatch = True


xadmin.site.register(views.BaseAdminView, BaseSettings)


class GlobalSetting(object):
    site_title = "百知教育在线教育商城后台管理系统"
    site_footer = "北京百知信息科技有限公司"
    menu_style = "accordion"  # 设置菜单折叠


xadmin.site.register(views.CommAdminView, GlobalSetting)


# 将banner注册到后台
class BannerInfo(object):
    # 指定默认展示的列
    list_display = ["title", 'orders', "is_show"]


xadmin.site.register(Banner, BannerInfo)


# 将banner注册到后台
class NavInfo(object):
    # 指定默认展示的列
    list_display = ["title", 'orders', "is_show"]


xadmin.site.register(Nav, NavInfo)
