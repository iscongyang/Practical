from prettytable import PrettyTable
from PIL import Image, ImageDraw, ImageFont
import datetime


class MakePicture:
    '''
    生成图片
    :param message: 传入的add_row信息，为字典
    :param fieldnames: 表头信息
    :param picture_name: 图片前缀
    :return:
    '''

    def __init__(self):
        self.tab = PrettyTable()

    def field_names(self, fieldnames: list):
        self.tab.field_names = fieldnames

    def row(self, content: list):
        self.tab.add_row(content)

    def picture(self, name: str):
        tab_info = str(self.tab)
        space = 5
        font = ImageFont.truetype(
            '/app/django/fonts/simkai.ttf',
            20, encoding='utf-8')
        im = Image.new('RGB', (10, 10), (255, 255, 255))
        draw = ImageDraw.Draw(im, "RGB")
        img_size = draw.multiline_textsize(tab_info, font=font)
        im_new = im.resize((img_size[0] + space * 2, img_size[1] + space * 2))
        del draw
        del im
        draw = ImageDraw.Draw(im_new, 'RGB')
        draw.multiline_text((space, space), tab_info, fill=(0, 0, 0), font=font)
        im_new.save('{0}.PNG'.format(name), "PNG")


def test():
    webhook = 'https://oapi.dingtalk.com/robot/send?access_token=x'
    yesterday = (datetime.datetime.today() - datetime.timedelta(days=1))
    # 以下为累计日票数据
    picture = MakePicture()
    picture.field_names(["统计类", "支付宝", "银联", "微信", "总计"])
    picture.row(['累计购买一日票人数', '{}'.format("xx(xx.xx%)"), '{}'.format("xx(xx.xx%)"), '{}'.format("xx(xx.xx%)"), '{}'.format("xx(xx.xx%)")])
    picture.row(['累计购买一日票张数', '{}'.format("xx(xx.xx%)"), '{}'.format("xx(xx.xx%)"), '{}'.format("xx(xx.xx%)"),
                 '{}'.format("xx(xx.xx%)")])
    picture.row(['累计购买三日票人数', '{}'.format("xx(xx.xx%)"), '{}'.format("xx(xx.xx%)"), '{}'.format("xx(xx.xx%)"),
                 '{}'.format("xx(xx.xx%)")])
    picture.row(['累计购买三日票张数', '{}'.format("xx(xx.xx%)"), '{}'.format("xx(xx.xx%)"), '{}'.format("xx(xx.xx%)"),
                 '{}'.format("xx(xx.xx%)")])
    picture.row(['累计失效一日票张数', '{}'.format("xx(xx.xx%)"), '{}'.format("xx(xx.xx%)"), '{}'.format("xx(xx.xx%)"),
                 '{}'.format("xx(xx.xx%)")])
    picture.row(['累计失效三日票张数', '{}'.format("xx(xx.xx%)"), '{}'.format("xx(xx.xx%)"), '{}'.format("xx(xx.xx%)"),
                 '{}'.format("xx(xx.xx%)")])
    picture.row(['累计退票一日票张数', '{}'.format("xx(xx.xx%)"), '{}'.format("xx(xx.xx%)"), '{}'.format("xx(xx.xx%)"),
                 '{}'.format("xx(xx.xx%)")])
    picture.row(['累计退票三日票张数', '{}'.format("xx(xx.xx%)"), '{}'.format("xx(xx.xx%)"), '{}'.format("xx(xx.xx%)"),
                 '{}'.format("xx(xx.xx%)")])
    picture.row(['累计购买一日票/三日票人数', '{}'.format("xx(xx.xx%)"), '{}'.format("xx(xx.xx%)"), '{}'.format("xx(xx.xx%)"),
                 '{}'.format("xx(xx.xx%)")])
    #picture.picture('/app/metro_daily/ripiao/ripiao_total_{}'.format(yesterday.strftime(('%Y%m%d%H%M%S'))))
    picture.picture('D:\\ripiao\\ripiao_total_{}'.format(yesterday.strftime(('%Y%m%d%H%M%S'))))
    #url_ripiao_total = 'http://x.com/metro_daily/ripiao/ripiao_total_{}.png'.format(yesterday.strftime(('%Y%m%d%H%M%S')))


if __name__ == "__main__":
    test()
