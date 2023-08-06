import webbrowser


def open_browser(text):
    ''' 打开指定网址'''
    urls = {
        'baidu':'http://www.baidu.com',
        'yuanfudao':'http://yuanfudao.com',
        'xiaoyuan':'http://www.yuanfudao.com/info/emojis',
        'sougou':'http://www.sogou.com',
    	'sanliuling':'http://www.so.com',
    	'shipin':'http://v.qq.com',
    	'youxi':'http://www.4399.com',
    	'yinyue':'http://music.163.com',
    	'donghua':'http://child.iqiyi.com',
    	'dianying':'http://www.iqiyi.com/dianying/',
        'xuexi':'http://yuanfudao.com'
    }
    if not text:
        return -1
    if 'baidu' in res :
        url = urls['baidu']
    elif 'yuanfudao' in res :
        url = urls['yuanfudao']
    elif 'xiao' in res :
        url = urls['xiaoyuan']
    elif 'sou' in res :
        url = urls['sougou']
    elif 'sanliuling' in res :
        url = urls['sanliuling']
    elif 'shipin' in res :
        url = urls['shipin']
    elif 'youxi' in res :
        url = urls['youxi']
    elif 'yinyue' in res :
        url = urls['yinyue']
    elif 'donghua' in res :
        url = urls['donghua']
    elif 'dianying' in res :
        url = urls['dianying']
    elif 'xuexi' in res :
        url = urls['xuexi']
    else:
        url = "http://www.baidu.com"
    return webbrowser.open_new_tab(url)


def main():
    open_browser('百度')
    # record1('9.wav')
    # record1('9.mp3')
    # record1('11.wav')
    # print(v2t('11.wav'))
    # print(v2t('12.mp3'))
    # record('1.mp3')
    # record('1.wav')
    # print(voice2text('1.mp3'))
    # text2voice('大家好，欢迎来到小猿编程','2.mp3')
    # text2voice('大家好，欢迎来到小猿编程','2.wav')
    # res = voice2text1('1.mp3')
    # print(res)
    # res = voice2text1('1.wav')
    # print(res)
    #
    # res = voice2text('2.mp3')
    # print(res)
    # res = voice2text('2.wav')
    # print(res)
    # res = v2t('1.wav',8000)
    # print(res)
    # res = v2t('2.wav',16000)
    # print(res)
    # record('3.wav')
    # record('3.mp3')
    # res = v2t('3.wav',8000)
    # print(res)
    # res = v2t('5.wav')
    # print(res)
    # res = t2v('大家好，欢迎来到猿辅导','4.wav',0)
    # print(res)
    # res = t2v('大家好，欢迎来到猿辅导','5.wav',1)
    # print(res)
    # res = t2v('大家好，欢迎来到猿辅导','6.wav',2)
    # print(res)
    # res = t2v('大家好，欢迎来到猿辅导','7.wav',3)
    # print(res)
    # res = t2v('大家好，欢迎来到猿辅导','8.wav',4)
    # print(res)
if __name__ == '__main__':
    main()
