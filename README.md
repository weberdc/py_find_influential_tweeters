# py_twitter_analysis
An experimental project to analyse tweet data.

Current metrics generated are a variant on the academic h-index,
a retweeter/mention ratio, a mixture model of retweeter/mention
ratio and interactor ratio, and a modification of the Duan-rank
PageRank variant algorithm from a paper:

 * Duan, Y., et al. "An empirical study on learning to rank of tweets." Proceedings
of the 23rd International Conference on Computational Linguistics. Association for
Computational Linguistics, 2010.

# Usage
<pre>
$ bin/py_twitter_analysis
    -i|--input-file &lt;tweets_file.json&gt;  : File of tweets, one per line
    [-x|--max-iterations &lt;max loops&gt;]   : D-rank iteration roof value (default: 20)
    [-w|--weight &lt;weight factor value&gt;] : D-rank weighting factor (default: 0.2)
    [-c|--count &lt;tweet_count_limit&gt;]    : Only consider up to this many` `tweets (default: -1, all)
    [-v|--verbose]                       : Verbose debugging flag
</pre>
