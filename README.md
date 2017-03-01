# py_twitter_analysis
An experimental project to analyse tweet data, specifically looking for signs of *"influence"*.

Current metrics generated are a variant on the academic h-index,
a retweeter/mention ratio, a mixture model of retweeter/mention
ratio and interactor ratio, and a modification of the Duan-rank
PageRank variant algorithm from a paper:

 * Duan, Y., et al. "An empirical study on learning to rank of tweets." Proceedings
of the 23rd International Conference on Computational Linguistics. Association for
Computational Linguistics, 2010.

The mixture model value may not be much use because it assumes all three values that it mixes
occur within the same range, which is not correct. I think there's a good chance it's not very
meaningful at all, so feel free to ignore it.

# Usage
<pre>
$ bin/py_twitter_analysis
    -i|--input-file &lt;tweets_file.json&gt;  : File of tweets, one per line
    [-x|--max-iterations &lt;max loops&gt;]   : D-rank iteration roof value (default: 20)
    [-w|--weight &lt;weight factor value&gt;] : D-rank weighting factor (default: 0.2)
    [-c|--count &lt;tweet_count_limit&gt;]    : Only consider up to this many tweets (default: -1, all)
    [-v|--verbose]                      : Verbose debugging flag
</pre>

# Test Data
In the `data` directory are two test files, one, `qanda-100.json`, has 100 tweets including the `#qanda`
hashtag collected ABC's Q&A panel discussion from mid-August 2016 (the episode aired on the 15th of
August 2016). The other, `test.json`, is a hand-crafted set of 16 tweets by six users, `A`, `B`, `C`,
`D`, `E`, and `F`. `A` tweets **four** original tweets:

* `@A: tweet A1` (ID: `1`, follower count: 10)
* `@A: tweet A2` (ID: `2`, follower count: 10)
* `@A: tweet A3` (ID: `3`, follower count: 10)
* `@A: tweet A4` (ID: `4`, follower count: 10)

Users `B`, `C`, and `D` all retweet `A`'s first three tweets, resulting in:

* `@B: RT @A: tweet A1` (ID: `11`)
* `@B: RT @A: tweet A2` (ID: `12`)
* `@B: RT @A: tweet A3` (ID: `13`)
* `@C: RT @A: tweet A1` (ID: `21`)
* `@C: RT @A: tweet A2` (ID: `22`)
* `@C: RT @A: tweet A3` (ID: `23`)
* `@D: RT @A: tweet A1` (ID: `31`)
* `@D: RT @A: tweet A2` (ID: `32`)
* `@D: RT @A: tweet A3` (ID: `33`)

User `E` replies to two of `A`'s tweets:

* `@E: @A IKR (reply to A1)` (ID: `41`, replying to tweet id: `1`)
* `@E: @A IKR (reply to A2)` (ID: `42`, replying to tweet id: `2`)

And user `F` simply *mention*s `A`:

* `@F: Tweeting about @A` (ID: `51`, mentions screen name: `A`)

The expected output based on this set is for user `A` to have an h-index of 3 (3 tweets each retweeted at
least 3 times), an interactor ratio of 0.5 (unique users retweeting and mentioning (5) / followers (10))
and a retweet/mention ratio of 1.5 (tweets retweeted (3) and tweets mentioning (3 (incl 2 replies)) / 
tweets in corpus (4)). `A`'s Duan rank value turns out to be 4.64.

The JSON for the tweets in `test.json` aren't as populated as tweets that are delivered by Twitter itself.
I only included the fields and values that the code required, though I also included some fields that were
required by another analysis programme, separate from this project. The extra fields, of course, don't affect
the operation of this code, as they're simply ignored.