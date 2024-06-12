import requests
from auth_util import gen_sign_headers

# 请注意替换APP_ID、APP_KEY
APP_ID = '3035921089'
APP_KEY = 'XCjChmlRyvPeEmMz'
DOMAIN = 'api-ai.vivo.com.cn'
URI = '/embedding-model-api/predict/batch'
METHOD = 'POST'


def embedding(sentence):
    params = {}
    post_data = {
        "model_name": "m3e-base",
        "sentences": sentence}
    headers = gen_sign_headers(APP_ID, APP_KEY, METHOD, URI, params)

    url = 'https://{}{}'.format(DOMAIN, URI)
    response = requests.post(url, json=post_data, headers=headers)
    if response.status_code == 200:
        #print(response.json()['data'])
        return response.json()['data']
    else:
        print(response.status_code, response.text)


if __name__ == '__main__':
    s=""
    embedding(s)
    print("\u5546\u5e97\u91cc\u4e00\u4e2a\u5973\u4eba\u633d\u7740\u4e00\u4e2a\u7537\u4eba\u5728\u770b\u6d88\u6bd2\u67dc")