"""Update only official SSE 510300 total shares; Python standard library only."""
import argparse, datetime as dt, json, re, time, urllib.request, urllib.parse
from pathlib import Path
from decimal import Decimal

ROOT=Path(__file__).resolve().parent
TZ=dt.timezone(dt.timedelta(hours=8))
SOURCE='https://www.sse.com.cn/market/funddata/volumn/etfvolumn/'
API='https://query.sse.com.cn/commonQuery.do'

def query(day):
    params={'isPagination':'true','pageHelp.pageSize':2000,'pageHelp.pageNo':1,'pageHelp.beginPage':1,'pageHelp.endPage':1,'pageHelp.cacheSize':1,'sqlId':'COMMON_SSE_ZQPZ_ETFZL_XXPL_ETFGM_SEARCH_L','STAT_DATE':day}
    for attempt in range(3):
        try:
            req=urllib.request.Request(API+'?'+urllib.parse.urlencode(params),headers={'Referer':SOURCE,'User-Agent':'Mozilla/5.0'})
            with urllib.request.urlopen(req,timeout=30) as response:
                payload=json.loads(response.read().decode('utf-8'))
            rows=payload['result']
            if not isinstance(rows,list) or len(rows)!=int(payload['pageHelp']['total']):
                raise ValueError('Incomplete official response')
            if any(r['STAT_DATE']!=day for r in rows):
                raise ValueError('Response date does not match request')
            found=[r for r in rows if r['SEC_CODE']=='510300']
            if len(found)>1 or (rows and not found):
                raise ValueError('Official response has missing or duplicate fund')
            if not found:return None
            val=Decimal(found[0]['TOT_VOL'].replace(',',''))
            if not val.is_finite() or val<=0:raise ValueError('Invalid total shares')
            return {'date':day,'code':'510300','name':found[0]['SEC_NAME'],'total_10k':str(val),'total_100m':str(val/10000),'checked_at':dt.datetime.now(TZ).isoformat()}
        except Exception:
            if attempt==2:raise
            time.sleep(2*(attempt+1))

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--end');parser.add_argument('--offline',action='store_true');args=parser.parse_args()
    data=json.loads((ROOT/'data.json').read_text(encoding='utf-8'))
    end=dt.date.fromisoformat(args.end) if args.end else dt.datetime.now(TZ).date()
    if end<dt.date.fromisoformat(data['requested_end']):raise ValueError('Refusing to move data coverage backwards')
    records={r['date']:r for r in data['records']};checked=set(data.get('checked_dates',[]));failed={e['date'] for e in data.get('errors',[])};errors=[]
    start=dt.date(2026,1,1);days=[start+dt.timedelta(days=i) for i in range((end-start).days+1)]
    if not args.offline:
        for day in days:
            key=str(day)
            if key in checked and day<end-dt.timedelta(days=10) and key not in failed:continue
            try:
                result=query(key)
                if result:records[key]=result
                elif key in records:raise ValueError('Previously published record disappeared; preserved old record')
                checked.add(key);data['last_success_at']=dt.datetime.now(TZ).isoformat()
            except Exception as exc:errors.append({'date':key,'error':type(exc).__name__})
            time.sleep(.3)
        data.update(requested_end=str(end),checked_dates=sorted(checked),errors=errors,last_attempt_at=dt.datetime.now(TZ).isoformat())
    data['records']=[records[k] for k in sorted(records)]
    data['days_without_record']=[str(day) for day in days if str(day) not in records]
    assert data['records']
    text=json.dumps(data,ensure_ascii=False,indent=2)
    tmp=ROOT/'data.tmp';tmp.write_text(text,encoding='utf-8');tmp.replace(ROOT/'data.json')
    page=(ROOT/'index.html').read_text(encoding='utf-8')
    seed=json.dumps(data,ensure_ascii=False).replace('</','<\\/')
    page=re.sub(r'(<script id="seed" type="application/json">).*?(</script>)',lambda m:m[1]+seed+m[2],page,flags=re.S)
    (ROOT/'index.html').write_text(page,encoding='utf-8')
    print(json.dumps({'records':len(records),'latest':data['records'][-1]['date'],'errors':errors},ensure_ascii=False))
    return bool(data.get('errors'))

if __name__=='__main__':raise SystemExit(main())
