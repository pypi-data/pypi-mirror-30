from google.appengine.ext.key_range import KeyRange
from im_util import logdebug
from im_future import future, GenerateOnAllChildSuccess, setlocalprogress, FutureReadyForResult, \
    generatefuturepagemapf, FutureNotReadyForResult, GetFutureAndCheckReady
from im_task import RetryTaskException

def futurendbshardedpagemap(pagemapf=None, ndbquery=None, pagesize=100, onsuccessf=None, onfailuref=None, onprogressf = None, onallchildsuccessf = None, initialresult = None, oncombineresultsf = None, weight = None, parentkey=None, **taskkwargs):
    kind = ndbquery.kind
 
    krlist = KeyRange.compute_split_points(kind, 5)
    logdebug("first krlist: %s" % krlist)
    logdebug(taskkwargs)
 
    @future(onsuccessf = onsuccessf, onfailuref = onfailuref, onprogressf = onprogressf, onallchildsuccessf=onallchildsuccessf, parentkey=parentkey, weight = weight, **taskkwargs)
    def dofuturendbshardedmap(futurekey):
        logdebug(taskkwargs)
 
        linitialresult = initialresult if not initialresult is None else 0
        loncombineresultsf = oncombineresultsf if oncombineresultsf else lambda a, b: a + b
    
        def MapOverRange(futurekey, keyrange, weight, **kwargs):
            logdebug("Enter MapOverRange: %s" % keyrange)
            try:
                _fixkeyend(keyrange, kind)
                
                filteredquery = keyrange.filter_ndb_query(ndbquery)
                
                logdebug (filteredquery)
                 
                keys, _, more = filteredquery.fetch_page(pagesize, keys_only=True)

                lonallchildsuccessf = GenerateOnAllChildSuccess(futurekey, 0 if pagemapf else len(keys), lambda a, b: a + b)
                         
                lweightUsed = 0
                if pagemapf:
                    futurename = "pagemap %s of %s" % (len(keys), keyrange)
                    lonallchildsuccessf = GenerateOnAllChildSuccess(futurekey, linitialresult, loncombineresultsf)
                    
                    lweightUsed = weight * 0.05
                    future(pagemapf, parentkey=futurekey, futurename=futurename, onallchildsuccessf=lonallchildsuccessf, weight = lweightUsed, **taskkwargs)(keys)
                else:
                    pass
                    #setlocalprogress(futurekey, len(keys))

                if more and keys:
                    lonallchildsuccessf = GenerateOnAllChildSuccess(futurekey, linitialresult if pagemapf else len(keys), loncombineresultsf)
                    newkeyrange = KeyRange(keys[-1], keyrange.key_end, keyrange.direction, False, keyrange.include_end)
                    krlist = newkeyrange.split_range()
                    logdebug("krlist: %s" % krlist)
                    newweight = (weight - lweightUsed) / len(krlist) if weight else None
                    for kr in krlist:
                        futurename = "shard %s" % (kr)
                        future(MapOverRange, parentkey=futurekey, futurename=futurename, onallchildsuccessf = lonallchildsuccessf, weight = newweight, **taskkwargs)(kr, weight = newweight)
# 
                if pagemapf or (more and keys):
#                 if (more and keys):
                    raise FutureReadyForResult("still going")
                else:
                    return len(keys)#(len(keys), 0, keyrange)
#                 return len(keys)
            finally:
                logdebug("Leave MapOverRange: %s" % keyrange)
  
        for kr in krlist:
            lonallchildsuccessf = GenerateOnAllChildSuccess(futurekey, linitialresult, loncombineresultsf)
            
            futurename = "shard %s" % (kr)

            newweight = weight / len(krlist) if weight else None
            future(MapOverRange, parentkey=futurekey, futurename=futurename, onallchildsuccessf=lonallchildsuccessf, weight = newweight, **taskkwargs)(kr, weight = newweight)
 
        raise FutureReadyForResult("still going")
 
    return dofuturendbshardedmap()

def generateinvokemapf(mapf):
    def InvokeMap(futurekey, key, **kwargs):
        logdebug("Enter InvokeMap: %s" % key)
        try:
            obj = key.get()
            if not obj:
                raise RetryTaskException("couldn't get object for key %s" % key)
     
            return mapf(futurekey, obj, **kwargs)
        finally:
            logdebug("Leave InvokeMap: %s" % key)
    return InvokeMap

def futurendbshardedmap(mapf=None, ndbquery=None, pagesize = 100, onsuccessf = None, onfailuref = None, onprogressf = None, onallchildsuccessf = None, initialresult = None, oncombineresultsf = None, weight = None, parentkey = None, **taskkwargs):
    invokeMapF = generateinvokemapf(mapf)
    pageMapF = generatefuturepagemapf(invokeMapF, initialresult, oncombineresultsf, **taskkwargs)
    return futurendbshardedpagemap(pageMapF, ndbquery, pagesize, onsuccessf = onsuccessf, onfailuref = onfailuref, onprogressf = onprogressf, onallchildsuccessf = onallchildsuccessf, initialresult = initialresult, oncombineresultsf = oncombineresultsf, parentkey=parentkey, weight=weight, **taskkwargs)

def futurendbshardedpagemapwithcount(pagemapf=None, ndbquery=None, pagesize=100, onsuccessf=None, onfailuref=None, onprogressf=None, onallchildsuccessf=None, initialresult = None, oncombineresultsf = None, parentkey = None, **taskkwargs):
    @future(onsuccessf = onsuccessf, onfailuref = onfailuref, onprogressf = onprogressf, onallchildsuccessf=onallchildsuccessf, parentkey = parentkey, weight=None, **taskkwargs)
    def countthenpagemap(futurekey):
        @future(parentkey=futurekey, futurename="placeholder for pagemap", weight = None, **taskkwargs)
        def DoNothing(futurekey):
            raise FutureNotReadyForResult("waiting for count")
         
        placeholderfuture = DoNothing()
        placeholderfuturekey = placeholderfuture.key

        def OnPageMapSuccess(pagemapfuturekey):
            pagemapfuture = GetFutureAndCheckReady(pagemapfuturekey)
            placeholderfuture = GetFutureAndCheckReady(placeholderfuturekey)
            future = GetFutureAndCheckReady(futurekey)
            result = pagemapfuture.get_result()
            placeholderfuture.set_success(result)
            future.set_success(result)
         
        def OnCountSuccess(countfuturekey):
            countfuture = GetFutureAndCheckReady(countfuturekey)
            futureobj = GetFutureAndCheckReady(futurekey)
            count = countfuture.get_result() 
            placeholderfuture = placeholderfuturekey.get()
            if placeholderfuture:
                placeholderfuture.set_weight(count*2)
                futureobj.set_weight(count*2)
                futurendbshardedpagemap(pagemapf, ndbquery, pagesize, onsuccessf = OnPageMapSuccess, weight = count, parentkey = placeholderfuturekey, **taskkwargs)

                # now that the second pass is actually constructed and running, we can let the placeholder accept a result.
                placeholderfuture.set_readyforesult()
         
        futurendbshardedpagemap(None, ndbquery, pagesize, onsuccessf = OnCountSuccess, parentkey = futurekey, initialresult = initialresult, oncombineresultsf = oncombineresultsf, weight = None, **taskkwargs)
        
        raise FutureReadyForResult("still going")
    return countthenpagemap()

def futurendbshardedmapwithcount(mapf=None, ndbquery=None, pagesize = 100, onsuccessf = None, onfailuref = None, onprogressf = None, onallchildsuccessf = None, initialresult = None, oncombineresultsf = None, weight = None, parentkey = None, **taskkwargs):
    invokeMapF = generateinvokemapf(mapf)
    pageMapF = generatefuturepagemapf(invokeMapF, initialresult, oncombineresultsf, **taskkwargs)
    return futurendbshardedpagemapwithcount(pageMapF, ndbquery, pagesize, onsuccessf = onsuccessf, onfailuref = onfailuref, onprogressf = onprogressf, onallchildsuccessf=onallchildsuccessf, initialresult = initialresult, oncombineresultsf = oncombineresultsf, parentkey=parentkey, **taskkwargs)

def _fixkeyend(keyrange, kind):
    if keyrange.key_start and not keyrange.key_end:
        endkey = KeyRange.guess_end_key(kind, keyrange.key_start)
        if endkey and endkey > keyrange.key_start:
            logdebug("Fixing end: %s" % endkey)
            keyrange.key_end = endkey
