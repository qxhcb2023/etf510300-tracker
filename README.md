# 510300 ETF每日总份额

来源：上海证券交易所ETF规模页面，统计口径为清算后总份额，原始单位万份。

网页支持鼠标悬停、手机点按及键盘左右键查看日期和总份额，提供CSV下载。网页每5分钟检查已部署数据，不直接从浏览器跨域请求上交所。

GitHub Actions每天北京时间21:30和23:30抓取最近11个自然日及此前失败、遗漏日期，保留历史记录并重新部署GitHub Pages。定时执行可能排队延迟。官网无记录日不补零或前值；失败时保留原数据并标注状态。

部署目标：GitHub公开仓库 + GitHub Pages公开网页，使用GitHub Free即可。

1. 仓库必须设为Public。`.github/workflows/daily.yml`负责自动更新和部署。
2. 在Settings → Pages中选择GitHub Actions作为Source，然后手动运行一次工作流。
3. `build_site.py`只把网页和公开基金数据放入发布目录；网站源代码和采集代码同样能从公开仓库查看。
4. 网页设置 `noindex` 并提供 `robots.txt`，降低被搜索引擎收录的机会。这不是访问控制；知道网址的人仍能访问。

本地更新：`python update.py`。离线生成：`python update.py --offline --end YYYY-MM-DD`。

线上部署状态可在仓库的 Actions 页面查看。
