Human-readable time delta formatter with relative precision ("ndigits")
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
