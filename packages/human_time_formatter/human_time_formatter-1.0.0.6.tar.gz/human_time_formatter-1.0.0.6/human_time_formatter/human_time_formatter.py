'''Human-readable time delta formatter with relative precision ("ndigits")
Gives human-readable output for basic timing benchmarks
Returns a string formatted in: "Y years, W weeks, D days, HH:MM:SSs"
  (or ms, us, ns, ps, fs for very small times)
Automatically reduces fields which are larger than the time passed or
  smaller than the requested precision.

Examples with ndigits=4:
  format_seconds(0.00096685) -> "966.9us"
  format_seconds(0.00387514) -> "3.875ms"
  format_seconds(0.01553157) -> "15.53ms"
  format_seconds(0.06225062) -> "62.25ms"
  format_seconds(0.24950074) -> "0.2495s"
  format_seconds(1.0       ) -> "1s"
  format_seconds(4.008004  ) -> "4.008s"
  format_seconds(16.0640960) -> "16.06s"
  format_seconds(64.3849612) -> "1:04.4s"
  format_seconds(258.055182) -> "4:18.1s"
  format_seconds(1034.28620) -> "17:14s"
  format_seconds(4145.42323) -> "1:09:05s"
  format_seconds(16614.8729) -> "4:36:55s"
  format_seconds(66592.4771) -> "18:29m"
  format_seconds(266902.914) -> "3 days, 02:08m"
  format_seconds(1069747.94) -> "1 week, 5 days, 9h"
  format_seconds(4287554.06) -> "7 weeks, 0 days, 14h"
  format_seconds(17184533.8) -> "28 weeks, 2 days"
  format_seconds(68875680.3) -> "2 years, 9 weeks, 4 days"
  format_seconds(276054002.) -> "8 years, 39 weeks, 2 days"
'''
from __future__ import print_function
from builtins import str
from builtins import range

def divmod_seconds(total_seconds):
    '''Approximately break seconds into years, days, hours, minutes, seconds
       Assumes 365 days/year (close enough for most things)'''
    m, s = divmod(total_seconds, 60)
    h, m = divmod(m, 60)
    d, h = divmod(h, 24)
    y, d = divmod(d, 365)
    w, d = divmod(d, 7)
    return int(y), int(w), int(d), int(h), int(m), s

def convert_ywdhms_to_seconds(y, w, d, h, m, s):
    '''The inverse of _divmod_time'''
    d += w * 7
    d += y * 365
    h += 24 * d
    m += 60 * h
    s += 60 * m
    return s

def format_seconds(total_seconds, ndigits=3):
    '''Human-readable time delta formatter with relative precision ("ndigits")
       Gives human-readable output for basic timing benchmarks
       Returns a string formatted in: "Y years, W weeks, D days, HH:MM:SSs"
         (or ms, us, ns, ps, fs for very small times)
       Automatically reduces fields which are larger than the time passed or
         smaller than the requested precision.
       Examples:
       
       
       Long Example:
         print 'input seconds   formatted_time            (y, w, d, h, m, s)'
         x_list = [2.002 ** (i - 10) for i in range(0, 40, 2)]
         for x in x_list:
             print '{0: <10}'.format(x)[:10] + '     ',
             print '{0: <25}'.format(format_seconds(x, ndigits=4)),
             print str(divmod_seconds(x))
         
         input seconds   formatted_time            (y, w, d, h, m, s)
         0.00096685      966.9us                   (0, 0, 0, 0, 0, 0.0009668503717900431)
         0.00387514      3.875ms                   (0, 0, 0, 0, 0, 0.003875140157535979)
         0.01553157      15.53ms                   (0, 0, 0, 0, 0, 0.01553157725196483)
         0.06225062      62.25ms                   (0, 0, 0, 0, 0, 0.062250623752184035)
         0.24950074      0.2495s                   (0, 0, 0, 0, 0, 0.24950074900124855)
         1.0             1s                        (0, 0, 0, 0, 0, 1.0)
         4.008004        4.008s                    (0, 0, 0, 0, 0, 4.008003999999999)
         16.0640960      16.06s                    (0, 0, 0, 0, 0, 16.06409606401599)
         64.3849612      1:04.4s                   (0, 0, 0, 0, 1, 4.38496128096034)
         258.055182      4:18.1s                   (0, 0, 0, 0, 4, 18.05518235393413)
         1034.28620      17:14s                    (0, 0, 0, 0, 17, 14.286203095297196)
         4145.42323      1:09:05s                  (0, 0, 0, 1, 9, 5.423239150762129)
         16614.8729      4:36:55s                  (0, 0, 0, 4, 36, 54.87292420920858)
         66592.4771      18:29m                    (0, 0, 0, 18, 29, 52.47713972219208)
         266902.914      3 days, 02:08m            (0, 0, 3, 2, 8, 22.91474591504084)
         1069747.94      1 week, 5 days, 9h        (0, 1, 5, 9, 9, 7.949913286138326)
         4287554.06      7 weeks, 0 days, 14h      (0, 7, 0, 14, 59, 14.062244249507785)
         17184533.8      28 weeks, 2 days          (0, 28, 2, 21, 28, 53.831691198050976)
         68875680.3      2 years, 9 weeks, 4 days  (2, 9, 4, 4, 8, 0.3355536311864853)
         276054002.      8 years, 39 weeks, 2 days (8, 39, 2, 1, 40, 2.28762024641037)

       '''
    y, w, d, h, m, s = divmod_seconds(total_seconds)
    res = ''
    started = False
    for t, v, st, sep in (('y', y, '{} years', ', '),
                          ('w', w, '{} weeks', ', '),
                          ('d', d, '{} days', ', '),
                          ('h', h, '{}', ':'),
                          ('m', m, '{}', ':'),
                         ):
        if v == 0 and not started:
            continue
        if v == 1 and t in 'ywd':
            st = st[:-1] # chop the s
        if started and v < 10 and (
           t == 'm' or (t =='h' and ndigits > 2)):
            res += '0'
        res += st.format(v)
        ndigits -= max(len(str(v)), 2 if started else 1)
        if ndigits > 0:
            res += sep
        else:
            if t in 'hm':
                res += t
            break
        started = True
    
    if ndigits > 0:
        if started:
            if s < 10:
                res += '0'
            fstr = '{0:.' + str(max(ndigits - 2, 0)) + 'f}'
            res += fstr.format(s) + 's'
        else:
            fstr = '{0:.' + str(ndigits) + 'g}'
            res = ('0s'                         if s == 0 else
                   fstr.format(s) + 's'         if s < 1e-15 else
                   fstr.format(s * 1e15) + 'fs' if s < 1e-12 else
                   fstr.format(s * 1e12) + 'ps' if s < 1e-9 else
                   fstr.format(s * 1e9) + 'ns'  if s < 1e-6 else
                   fstr.format(s * 1e6) + 'us'  if s < 1e-3 else
                   fstr.format(s * 1e3) + 'ms'  if s < 0.1 else
                   fstr.format(s) + 's')
    return res

if __name__ == "__main__":
    # Examples :)
    print('input seconds   formatted_time            (y, w, d, h, m, s)')
    x_list = [2.002 ** (i - 10) for i in range(0, 40, 2)]
    for x in x_list:
        print('{0: <10}'.format(x)[:10] + '     ', end=' ')
        print('{0: <25}'.format(format_seconds(x, ndigits=4)), end=' ')
        print(str(divmod_seconds(x)))
